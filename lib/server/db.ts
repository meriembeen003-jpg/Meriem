import fs from "fs";
import path from "path";
import {
  CloudSentinelSettings,
  GeopoliticalDispatch,
  MediaForensicResult,
  RejectedNoiseEntry,
  RootSource,
} from "@/lib/types/geointel";
import {
  INITIAL_REJECTED_NOISE,
  INITIAL_ROOT_SOURCES,
} from "@/lib/data/root-sources";
import { BASELINE_DISPATCHES } from "@/lib/data/war-theaters";

export interface RasedDatabaseSchema {
  dispatches: GeopoliticalDispatch[];
  rootSources: RootSource[];
  rejectedNoise: RejectedNoiseEntry[];
  forensicHistory: MediaForensicResult[];
  seenExternalGuids: string[];
  settings: CloudSentinelSettings;
}

const DATA_DIR = path.join(process.cwd(), "data");
const DB_PATH = path.join(DATA_DIR, "rased-db.json");

function createDefaultDb(): RasedDatabaseSchema {
  return {
    dispatches: [...BASELINE_DISPATCHES],
    rootSources: [...INITIAL_ROOT_SOURCES],
    rejectedNoise: [...INITIAL_REJECTED_NOISE],
    forensicHistory: [],
    seenExternalGuids: [],
    settings: {
      aiProvider: "auto",
      geminiApiKey: process.env.GEMINI_API_KEY || "",
      openaiApiKey: process.env.OPENAI_API_KEY || "",
      anthropicApiKey: process.env.ANTHROPIC_API_KEY || "",
      fcmServerKeyOrWebhook: process.env.FCM_WEBHOOK_URL || "",
      cloudServerPublicUrl: process.env.CLOUD_SERVER_PUBLIC_URL || "",
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
    },
  };
}

declare global {
  var __rasedDbCache: RasedDatabaseSchema | undefined;
}

export function getDb(): RasedDatabaseSchema {
  if (globalThis.__rasedDbCache) {
    return globalThis.__rasedDbCache;
  }

  try {
    if (fs.existsSync(DB_PATH)) {
      const raw = fs.readFileSync(DB_PATH, "utf-8");
      const parsed = JSON.parse(raw) as Partial<RasedDatabaseSchema>;
      const defaults = createDefaultDb();
      globalThis.__rasedDbCache = {
        dispatches: parsed.dispatches?.length ? parsed.dispatches : defaults.dispatches,
        rootSources: parsed.rootSources?.length ? parsed.rootSources : defaults.rootSources,
        rejectedNoise: parsed.rejectedNoise?.length
          ? parsed.rejectedNoise
          : defaults.rejectedNoise,
        forensicHistory: parsed.forensicHistory || [],
        seenExternalGuids: parsed.seenExternalGuids || [],
        settings: {
          ...defaults.settings,
          ...(parsed.settings || {}),
        },
      };
      return globalThis.__rasedDbCache;
    }
  } catch (err) {
    console.warn("[RASED DB] Falling back to fresh DB state:", err);
  }

  const fresh = createDefaultDb();
  globalThis.__rasedDbCache = fresh;
  saveDb(fresh);
  return fresh;
}

export function saveDb(db: RasedDatabaseSchema = getDb()): void {
  globalThis.__rasedDbCache = db;
  try {
    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }
    const tmpPath = `${DB_PATH}.tmp`;
    fs.writeFileSync(tmpPath, JSON.stringify(db, null, 2), "utf-8");
    fs.renameSync(tmpPath, DB_PATH);
  } catch (err) {
    console.warn("[RASED DB] Persist warning:", err);
  }
}

export function getSanitizedSettings(settings: CloudSentinelSettings) {
  return {
    ...settings,
    geminiApiKey: settings.geminiApiKey ? "••••••••" + settings.geminiApiKey.slice(-4) : "",
    openaiApiKey: settings.openaiApiKey ? "••••••••" + settings.openaiApiKey.slice(-4) : "",
    anthropicApiKey: settings.anthropicApiKey
      ? "••••••••" + settings.anthropicApiKey.slice(-4)
      : "",
    hasGeminiKey: Boolean(settings.geminiApiKey && settings.geminiApiKey.length > 8),
    hasOpenaiKey: Boolean(settings.openaiApiKey && settings.openaiApiKey.length > 8),
    hasAnthropicKey: Boolean(settings.anthropicApiKey && settings.anthropicApiKey.length > 8),
  };
}
