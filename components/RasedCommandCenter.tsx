"use client";

import { useCallback, useEffect, useState } from "react";
import {
  BellRing,
  Compass,
  Newspaper,
  ScanSearch,
  Shield,
  Smartphone,
  X,
} from "lucide-react";
import {
  CloudSentinelSettings,
  GeopoliticalDispatch,
  MediaForensicResult,
  RejectedNoiseEntry,
  RootSource,
  SentinelTelemetry,
  WarTheater,
  WarTheaterId,
} from "@/lib/types/geointel";
import { BASELINE_DISPATCHES, WAR_THEATERS } from "@/lib/data/war-theaters";
import {
  INITIAL_REJECTED_NOISE,
  INITIAL_ROOT_SOURCES,
} from "@/lib/data/root-sources";
import {
  apiUrl,
  fireInstantArabicNotification,
  playTacticalAlertTone,
  requestAlertPermissions,
} from "@/lib/client/native-bridge";
import TelemetryHeader from "@/components/TelemetryHeader";
import DispatchFeedAndDetail from "@/components/DispatchFeedAndDetail";
import WarMapRadar from "@/components/WarMapRadar";
import MediaForensicsLab from "@/components/MediaForensicsLab";
import RootSourcesGatekeeper from "@/components/RootSourcesGatekeeper";
import ApkAndCloudHub from "@/components/ApkAndCloudHub";

type ActiveTab = "FEED" | "MAP" | "LAB" | "SOURCES" | "APK_CLOUD";

const OFFLINE_CACHE_KEY = "rased_offline_snapshot_v1";

export default function RasedCommandCenter() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("FEED");
  const [selectedTheater, setSelectedTheater] = useState<WarTheaterId | "ALL">(
    "ALL"
  );

  const [telemetry, setTelemetry] = useState<SentinelTelemetry | null>(null);
  const [theaters, setTheaters] = useState<WarTheater[]>(WAR_THEATERS);
  const [dispatches, setDispatches] =
    useState<GeopoliticalDispatch[]>(BASELINE_DISPATCHES);
  const [rootSources, setRootSources] =
    useState<RootSource[]>(INITIAL_ROOT_SOURCES);
  const [rejectedNoise, setRejectedNoise] = useState<RejectedNoiseEntry[]>(
    INITIAL_REJECTED_NOISE
  );
  const [forensicHistory, setForensicHistory] = useState<MediaForensicResult[]>(
    []
  );
  const [settings, setSettings] = useState<CloudSentinelSettings>({
    aiProvider: "auto",
    cloudServerPublicUrl: "",
    scanIntervalSeconds: 45,
    minAccuracyForPush: 78,
    notifySeverities: ["CRITICAL", "HIGH"],
    watchedTheaters: [
      "MIDDLE_EAST_RED_SEA",
      "EAST_EUROPE",
      "INDO_PACIFIC_TAIWAN",
      "SAHEL_HORN_AFRICA",
      "STRATEGIC_NUCLEAR_CYBER",
    ],
    strictRootOnlyMode: true,
    soundAlertsEnabled: true,
  });

  const [sseConnected, setSseConnected] = useState(false);
  const [isScanningNow, setIsScanningNow] = useState(false);
  const [notificationsGranted, setNotificationsGranted] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [flashAlert, setFlashAlert] = useState<GeopoliticalDispatch | null>(
    null
  );

  const fetchFullState = useCallback(async () => {
    try {
      const res = await fetch(apiUrl("/api/state"), { cache: "no-store" });
      if (!res.ok) return;
      const json = await res.json();
      if (!json.ok) return;

      setTelemetry(json.telemetry);
      setTheaters(json.theaters || WAR_THEATERS);
      setDispatches(json.dispatches || BASELINE_DISPATCHES);
      setRootSources(json.rootSources || INITIAL_ROOT_SOURCES);
      setRejectedNoise(json.rejectedNoise || INITIAL_REJECTED_NOISE);
      setForensicHistory(json.forensicHistory || []);
      if (json.settings) {
        setSettings(json.settings);
        setSoundEnabled(Boolean(json.settings.soundAlertsEnabled));
      }

      try {
        localStorage.setItem(
          OFFLINE_CACHE_KEY,
          JSON.stringify({
            dispatches: json.dispatches,
            rootSources: json.rootSources,
            rejectedNoise: json.rejectedNoise,
          })
        );
      } catch {
        // Storage quota ignore
      }
    } catch {
      // Load offline snapshot if running in APK while disconnected
      try {
        const cached = localStorage.getItem(OFFLINE_CACHE_KEY);
        if (cached) {
          const parsed = JSON.parse(cached);
          if (parsed.dispatches?.length) setDispatches(parsed.dispatches);
          if (parsed.rootSources?.length) setRootSources(parsed.rootSources);
        }
      } catch {
        // Ignore
      }
    }
  }, []);

  useEffect(() => {
    void fetchFullState();
    if (
      typeof window !== "undefined" &&
      "Notification" in window &&
      Notification.permission === "granted"
    ) {
      setNotificationsGranted(true);
    }
  }, [fetchFullState]);

  // Real-time Server-Sent Events (SSE) continuous vigilance connection
  useEffect(() => {
    let es: EventSource | null = null;
    try {
      es = new EventSource(apiUrl("/api/stream"));
      es.addEventListener("connected", (ev) => {
        setSseConnected(true);
        try {
          setTelemetry(JSON.parse((ev as MessageEvent).data));
        } catch {
          // Ignore
        }
      });

      es.addEventListener("heartbeat", (ev) => {
        setSseConnected(true);
        try {
          setTelemetry(JSON.parse((ev as MessageEvent).data));
        } catch {
          // Ignore
        }
      });

      es.addEventListener("scan_started", () => {
        setIsScanningNow(true);
      });

      es.addEventListener("scan_completed", (ev) => {
        setIsScanningNow(false);
        try {
          setTelemetry(JSON.parse((ev as MessageEvent).data));
        } catch {
          // Ignore
        }
      });

      es.addEventListener("new_dispatch", (ev) => {
        try {
          const payload = JSON.parse((ev as MessageEvent).data) as {
            dispatch: GeopoliticalDispatch;
            shouldTriggerAlert: boolean;
          };
          setDispatches((prev) => {
            if (prev.some((p) => p.id === payload.dispatch.id)) return prev;
            return [payload.dispatch, ...prev];
          });
          setFlashAlert(payload.dispatch);
          if (payload.shouldTriggerAlert) {
            void fireInstantArabicNotification(payload.dispatch, soundEnabled);
          }
        } catch {
          // Ignore
        }
      });

      es.onerror = () => {
        setSseConnected(false);
      };
    } catch {
      setSseConnected(false);
    }

    return () => {
      if (es) es.close();
    };
  }, [soundEnabled]);

  const handleForceScan = async (drill: boolean) => {
    setIsScanningNow(true);
    try {
      const res = await fetch(apiUrl("/api/scan"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ drill }),
      });
      const json = await res.json();
      if (json.ok && Array.isArray(json.newDispatches) && json.newDispatches.length > 0) {
        const newest = json.newDispatches[0] as GeopoliticalDispatch;
        setDispatches((prev) => {
          const existingIds = new Set(prev.map((x) => x.id));
          const fresh = (json.newDispatches as GeopoliticalDispatch[]).filter(
            (x) => !existingIds.has(x.id)
          );
          return [...fresh, ...prev];
        });
        setFlashAlert(newest);
        if (drill) {
          void fireInstantArabicNotification(newest, soundEnabled);
        }
      }
      if (json.telemetry) {
        setTelemetry(json.telemetry);
      }
    } finally {
      setIsScanningNow(false);
    }
  };

  const handleRequestNotifications = async () => {
    const res = await requestAlertPermissions();
    setNotificationsGranted(res.granted);
    if (res.granted && soundEnabled) {
      playTacticalAlertTone("HIGH");
    }
  };

  const handleToggleSound = async () => {
    const next = !soundEnabled;
    setSoundEnabled(next);
    if (next) {
      playTacticalAlertTone("HIGH");
    }
    await fetch(apiUrl("/api/settings"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ soundAlertsEnabled: next }),
    }).catch(() => null);
  };

  const navItems: Array<{
    id: ActiveTab;
    label: string;
    shortLabel: string;
    icon: typeof Newspaper;
    badge?: string;
  }> = [
    {
      id: "FEED",
      label: "الرصد العاجل (المصادر الأم)",
      shortLabel: "الرصد",
      icon: Newspaper,
      badge: String(dispatches.length),
    },
    {
      id: "MAP",
      label: "خريطة مسارح الحروب",
      shortLabel: "الخريطة",
      icon: Compass,
      badge: "5",
    },
    {
      id: "LAB",
      label: "مختبر الفيديو والنصوص",
      shortLabel: "مختبر التحقق",
      icon: ScanSearch,
    },
    {
      id: "SOURCES",
      label: "بوابة المصادر الأم",
      shortLabel: "المصادر",
      icon: Shield,
      badge: String(rootSources.filter((s) => s.enabled).length),
    },
    {
      id: "APK_CLOUD",
      label: "تطبيق APK والخادم السحابي",
      shortLabel: "APK والسحابة",
      icon: Smartphone,
    },
  ];

  return (
    <div
      dir="rtl"
      className="min-h-screen bg-[#060911] pb-24 text-slate-100 md:pb-10"
    >
      <TelemetryHeader
        telemetry={telemetry}
        sseConnected={sseConnected}
        notificationsGranted={notificationsGranted}
        soundEnabled={soundEnabled}
        isScanningNow={isScanningNow}
        onForceScan={handleForceScan}
        onRequestNotifications={handleRequestNotifications}
        onToggleSound={handleToggleSound}
      />

      {/* Instant Breaking Flash Alert Toast */}
      {flashAlert && (
        <div className="mx-auto mt-3 max-w-7xl px-4">
          <div className="flex items-start justify-between gap-3 rounded-2xl border border-rose-500/60 bg-gradient-to-l from-rose-950/90 via-[#190d18] to-[#0b1220] p-4 shadow-[0_0_30px_rgba(244,63,94,0.25)]">
            <div className="flex items-start gap-3">
              <div className="mt-0.5 rounded-xl bg-rose-500/20 p-2">
                <BellRing className="h-5 w-5 animate-bounce text-rose-400" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="rounded-full bg-rose-500 px-2.5 py-0.5 font-extrabold text-white">
                    إشعار فوري من المصدر الأم
                  </span>
                  <span className="font-mono font-bold text-emerald-300">
                    دقة التحقق: {flashAlert.accuracy.overallScore}%
                  </span>
                  <span className="text-slate-300">
                    • {flashAlert.rootSourceNameAr}
                  </span>
                </div>
                <p className="mt-1.5 text-sm font-bold text-white">
                  {flashAlert.headlineAr}
                </p>
                <p className="mt-0.5 text-xs text-slate-300">
                  {flashAlert.flashSummaryAr}
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setFlashAlert(null)}
              className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Desktop Tactical Navigation Tabs */}
      <nav className="mx-auto mt-4 hidden max-w-7xl px-4 md:block">
        <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-800/90 bg-[#0b1220] p-1.5">
          {navItems.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition ${
                  active
                    ? "bg-gradient-to-l from-emerald-500/20 to-cyan-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className="rounded-full bg-slate-900 px-2 py-0.5 font-mono text-[10px] text-cyan-300">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Content Workspace */}
      <main className="mx-auto mt-4 max-w-7xl px-4">
        {activeTab === "FEED" && (
          <DispatchFeedAndDetail
            dispatches={dispatches}
            theaters={theaters}
            selectedTheater={selectedTheater}
            onSelectTheater={setSelectedTheater}
          />
        )}

        {activeTab === "MAP" && (
          <WarMapRadar
            theaters={theaters}
            dispatches={dispatches}
            selectedTheater={selectedTheater}
            onSelectTheater={setSelectedTheater}
            onJumpToFeedWithTheater={(id) => {
              setSelectedTheater(id);
              setActiveTab("FEED");
            }}
          />
        )}

        {activeTab === "LAB" && (
          <MediaForensicsLab initialHistory={forensicHistory} />
        )}

        {activeTab === "SOURCES" && (
          <RootSourcesGatekeeper
            rootSources={rootSources}
            rejectedNoise={rejectedNoise}
            onRefreshState={fetchFullState}
          />
        )}

        {activeTab === "APK_CLOUD" && (
          <ApkAndCloudHub
            settings={settings}
            onRefreshState={fetchFullState}
          />
        )}
      </main>

      {/* Mobile / Android APK Bottom Navigation Bar */}
      <nav className="fixed right-0 bottom-0 left-0 z-50 border-t border-slate-800 bg-[#070b14]/95 px-2 py-1.5 backdrop-blur-md md:hidden">
        <div className="grid grid-cols-5 gap-1">
          {navItems.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`flex flex-col items-center justify-center rounded-xl py-1.5 text-[10px] font-bold transition ${
                  active
                    ? "bg-emerald-500/15 text-emerald-300"
                    : "text-slate-400"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="mt-1 truncate">{tab.shortLabel}</span>
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
