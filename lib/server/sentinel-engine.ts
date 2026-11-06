import { XMLParser } from "fast-xml-parser";
import { getDb, saveDb } from "@/lib/server/db";
import {
  isGeopoliticalOrMilitaryRelevant,
  reformulateRootWireToArabic,
  resolveActiveAiName,
} from "@/lib/server/ai-engine";
import { dispatchCloudPushAlert } from "@/lib/server/push-dispatcher";
import { DRILL_DISPATCH_POOL } from "@/lib/data/war-theaters";
import { GeopoliticalDispatch, SentinelTelemetry } from "@/lib/types/geointel";

type SseSubscriber = (eventName: string, payload: unknown) => void;

interface SentinelRuntime {
  startedAtUtc: string;
  lastHeartbeatUtc: string;
  lastScanUtc: string;
  isScanning: boolean;
  totalScansCompleted: number;
  networkFeedMode: "LIVE_CLOUD_FEEDS" | "SANDBOX_RESTRICTED_STANDBY";
  drillCursor: number;
  subscribers: Set<SseSubscriber>;
  timer?: ReturnType<typeof setInterval>;
}

declare global {
  var __rasedSentinelRuntime: SentinelRuntime | undefined;
}

const xmlParser = new XMLParser({
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
});

function stripHtml(html: string): string {
  return String(html || "")
    .replace(/<[^>]*>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function getSentinelRuntime(): SentinelRuntime {
  if (!globalThis.__rasedSentinelRuntime) {
    const now = new Date().toISOString();
    const runtime: SentinelRuntime = {
      startedAtUtc: now,
      lastHeartbeatUtc: now,
      lastScanUtc: now,
      isScanning: false,
      totalScansCompleted: 1,
      networkFeedMode: "SANDBOX_RESTRICTED_STANDBY",
      drillCursor: 0,
      subscribers: new Set<SseSubscriber>(),
    };

    runtime.timer = setInterval(() => {
      runtime.lastHeartbeatUtc = new Date().toISOString();
      const db = getDb();
      const elapsedSec =
        (Date.now() - new Date(runtime.lastScanUtc).getTime()) / 1000;

      broadcastSse("heartbeat", getSentinelTelemetry());

      if (elapsedSec >= db.settings.scanIntervalSeconds && !runtime.isScanning) {
        void runRootSourcesScan(false);
      }
    }, 5000);

    // Unref timer if possible so build scripts don't hang
    if (runtime.timer && typeof runtime.timer.unref === "function") {
      runtime.timer.unref();
    }

    globalThis.__rasedSentinelRuntime = runtime;
  }
  return globalThis.__rasedSentinelRuntime;
}

export function subscribeSentinelSse(cb: SseSubscriber): () => void {
  const runtime = getSentinelRuntime();
  runtime.subscribers.add(cb);
  return () => {
    runtime.subscribers.delete(cb);
  };
}

export function broadcastSse(eventName: string, payload: unknown): void {
  const runtime = getSentinelRuntime();
  for (const sub of runtime.subscribers) {
    try {
      sub(eventName, payload);
    } catch {
      runtime.subscribers.delete(sub);
    }
  }
}

export function getSentinelTelemetry(): SentinelTelemetry {
  const runtime = getSentinelRuntime();
  const db = getDb();
  const elapsedSec = Math.floor(
    (Date.now() - new Date(runtime.lastScanUtc).getTime()) / 1000
  );
  const nextScanInSeconds = Math.max(
    0,
    db.settings.scanIntervalSeconds - elapsedSec
  );

  return {
    status: runtime.isScanning ? "SCANNING" : "ARMED_24_7",
    startedAtUtc: runtime.startedAtUtc,
    lastHeartbeatUtc: runtime.lastHeartbeatUtc,
    lastScanUtc: runtime.lastScanUtc,
    nextScanInSeconds,
    totalScansCompleted: runtime.totalScansCompleted,
    activeRootSourcesCount: db.rootSources.filter((s) => s.enabled).length,
    totalVerifiedDispatches: db.dispatches.length,
    totalRejectedNoiseCount: db.rejectedNoise.length,
    networkFeedMode: runtime.networkFeedMode,
    configuredAiEngine: resolveActiveAiName(db.settings),
  };
}

export async function runRootSourcesScan(
  includeDrillIfOffline = false
): Promise<{
  newDispatches: GeopoliticalDispatch[];
  liveFeedsReached: number;
  telemetry: SentinelTelemetry;
}> {
  const runtime = getSentinelRuntime();
  if (runtime.isScanning) {
    return {
      newDispatches: [],
      liveFeedsReached: 0,
      telemetry: getSentinelTelemetry(),
    };
  }

  runtime.isScanning = true;
  broadcastSse("scan_started", getSentinelTelemetry());

  const db = getDb();
  const enabledSources = db.rootSources.filter((s) => s.enabled);
  const newlyCaptured: GeopoliticalDispatch[] = [];
  let liveFeedsReached = 0;

  try {
    // Scan up to 8 enabled sources concurrently per cycle for fast non-blocking turnaround
    const batch = enabledSources.slice(0, 8);
    await Promise.all(
      batch.map(async (source) => {
        try {
          const res = await fetch(source.rssUrl, {
            headers: {
              "User-Agent": "RasedGeoIntelSentinel/1.0 (+PrimarySourceVerifier)",
              Accept: "application/rss+xml, application/xml, text/xml, */*",
            },
            signal: AbortSignal.timeout(4000),
          });

          source.lastCheckedUtc = new Date().toISOString();

          if (!res.ok) {
            source.lastStatus = "ERROR";
            return;
          }

          const xml = await res.text();
          liveFeedsReached += 1;
          source.lastStatus = "OK";

          const parsed = xmlParser.parse(xml);
          const rawItems =
            parsed?.rss?.channel?.item ||
            parsed?.feed?.entry ||
            [];
          const itemsList = Array.isArray(rawItems) ? rawItems : [rawItems];

          for (const item of itemsList.slice(0, 4)) {
            const title = stripHtml(
              typeof item?.title === "object" ? item.title["#text"] : item?.title
            );
            const description = stripHtml(
              item?.description || item?.summary || item?.content || ""
            );
            const link =
              typeof item?.link === "object"
                ? item.link["@_href"] || source.rssUrl
                : String(item?.link || source.rssUrl);
            const guid = String(item?.guid?.["#text"] || item?.guid || item?.id || link || title);

            if (!title || db.seenExternalGuids.includes(guid)) {
              continue;
            }

            db.seenExternalGuids.unshift(guid);
            if (db.seenExternalGuids.length > 500) {
              db.seenExternalGuids.length = 500;
            }

            if (!isGeopoliticalOrMilitaryRelevant(`${title} ${description}`)) {
              continue;
            }

            const dispatch = await reformulateRootWireToArabic(
              {
                title,
                description,
                link,
                pubDateUtc: item?.pubDate
                  ? new Date(item.pubDate).toISOString()
                  : new Date().toISOString(),
                rootSource: source,
              },
              db.settings
            );

            source.capturedCount += 1;
            newlyCaptured.push(dispatch);
            break; // Max 1 top dispatch per source per cycle to prevent alert flood
          }
        } catch {
          source.lastCheckedUtc = new Date().toISOString();
          source.lastStatus = "STANDBY_OFFLINE";
        }
      })
    );

    runtime.networkFeedMode =
      liveFeedsReached > 0 ? "LIVE_CLOUD_FEEDS" : "SANDBOX_RESTRICTED_STANDBY";

    // If user explicitly clicked "فحص المصادر الأم / محاكاة إنذار فوري" in restricted network, inject verified drill item
    if (includeDrillIfOffline && newlyCaptured.length === 0) {
      const template =
        DRILL_DISPATCH_POOL[runtime.drillCursor % DRILL_DISPATCH_POOL.length];
      runtime.drillCursor += 1;
      const nowIso = new Date().toISOString();
      const drillDispatch: GeopoliticalDispatch = {
        ...template,
        id: `dsp-drill-${Date.now()}`,
        publishedAtUtc: nowIso,
        capturedAtUtc: nowIso,
      };
      newlyCaptured.push(drillDispatch);
    }

    if (newlyCaptured.length > 0) {
      db.dispatches = [...newlyCaptured, ...db.dispatches].slice(0, 100);
      for (const dsp of newlyCaptured) {
        const meetsPushRules =
          dsp.accuracy.overallScore >= db.settings.minAccuracyForPush &&
          db.settings.notifySeverities.includes(dsp.severity) &&
          db.settings.watchedTheaters.includes(dsp.theaterId);

        broadcastSse("new_dispatch", {
          dispatch: dsp,
          shouldTriggerAlert: meetsPushRules,
        });

        if (meetsPushRules) {
          void dispatchCloudPushAlert(dsp, db.settings);
        }
      }
    }

    runtime.lastScanUtc = new Date().toISOString();
    runtime.totalScansCompleted += 1;
    saveDb(db);
  } finally {
    runtime.isScanning = false;
    broadcastSse("scan_completed", getSentinelTelemetry());
  }

  return {
    newDispatches: newlyCaptured,
    liveFeedsReached,
    telemetry: getSentinelTelemetry(),
  };
}
