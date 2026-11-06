export type WarTheaterId =
  | "EAST_EUROPE"
  | "MIDDLE_EAST_RED_SEA"
  | "INDO_PACIFIC_TAIWAN"
  | "SAHEL_HORN_AFRICA"
  | "STRATEGIC_NUCLEAR_CYBER";

export type AlertSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "ROUTINE";

export type SourceCategory =
  | "GLOBAL_WIRE_AGENCY"
  | "DEFENSE_MINISTRY"
  | "MARITIME_INTL_MONITOR"
  | "STRATEGIC_INSTITUTE";

export type VerificationBadge =
  | "CONFIRMED_MULTI_PRIMARY"
  | "OFFICIAL_BELLIGERENT_STATEMENT"
  | "INITIAL_PRIMARY_WIRE"
  | "DISPUTED_OR_UNVERIFIED";

export type CaptureMode =
  | "LIVE_RSS_VERIFIED"
  | "REFERENCE_BASELINE"
  | "MANUAL_VERIFIED_SCAN";

export interface RootSource {
  id: string;
  shortCode: string;
  nameAr: string;
  nameOriginal: string;
  category: SourceCategory;
  countryOrOrgAr: string;
  officialDomain: string;
  rssUrl: string;
  language: "en" | "ar" | "ru" | "zh" | "fr";
  reliabilityBaseScore: number; // 0-100
  biasNatureAr: string;
  requiresCrossCheck: boolean; // True for state/belligerent defense ministries
  enabled: boolean;
  lastCheckedUtc?: string;
  lastStatus?: "OK" | "STANDBY_OFFLINE" | "ERROR";
  capturedCount: number;
}

export interface WarTheater {
  id: WarTheaterId;
  nameAr: string;
  shortNameAr: string;
  regionCode: string;
  escalationLevel: 1 | 2 | 3 | 4 | 5; // 5 = Critical Active Warfare
  escalationLabelAr: string;
  coordinates: {
    lat: number;
    lng: number;
    mapX: number; // 0-1000 SVG coordinate
    mapY: number; // 0-500 SVG coordinate
  };
  chokePointsAr: string[];
  activeForcesAr: string[];
  strategicSummaryAr: string;
}

export interface AccuracyBreakdown {
  rootAuthenticity: number; // 0-100 (weight 35%)
  independentCorroboration: number; // 0-100 (weight 30%)
  geoTemporalConsistency: number; // 0-100 (weight 20%)
  mediaIntegrity: number; // 0-100 (weight 15%)
  overallScore: number; // 0-100 weighted
  rationaleAr: string;
}

export interface CorroboratingSourceRef {
  sourceId: string;
  nameAr: string;
  officialDomain: string;
  confirmationNoteAr: string;
  timestampUtc: string;
}

export interface StrategicExplanation {
  operationalImpactAr: string;
  militarySystemsAr: string[];
  narrativeBalanceAr: string;
  scenarios24to72hAr: string[];
  historicalContextAr: string;
}

export interface GeopoliticalDispatch {
  id: string;
  headlineAr: string;
  flashSummaryAr: string;
  detailedRewriteAr: string;
  originalHeadline: string;
  originalExcerpt: string;
  originalLanguage: string;
  rootSourceId: string;
  rootSourceNameAr: string;
  rootSourceDomain: string;
  rootSourceUrl: string;
  corroboratingSources: CorroboratingSourceRef[];
  theaterId: WarTheaterId;
  locationAr: string;
  coordinates: {
    lat: number;
    lng: number;
    label: string;
  };
  severity: AlertSeverity;
  verificationBadge: VerificationBadge;
  captureMode: CaptureMode;
  accuracy: AccuracyBreakdown;
  strategicExplanation: StrategicExplanation;
  tagsAr: string[];
  publishedAtUtc: string;
  capturedAtUtc: string;
  aiEngineUsed: string;
  hasVideoAnalysis?: boolean;
  videoForensicSummaryAr?: string;
}

export interface RejectedNoiseEntry {
  id: string;
  timestampUtc: string;
  originDomainOrHandle: string;
  rawHeadline: string;
  rejectionReasonAr: string;
  ruleCode:
    | "NON_ROOT_AGGREGATOR"
    | "UNATTRIBUTED_SOCIAL_CLAIM"
    | "RECYCLED_ARCHIVE_MEDIA"
    | "PROPAGANDA_SENSATIONALISM";
}

export interface ExtractedVideoFrame {
  timestampSec: number;
  dataUrl: string; // base64 JPEG
  avgLuminance: number;
  contrastScore: number;
  dominantTone: "DAYLIGHT" | "NIGHT_DARK" | "NIGHT_VISION_GREEN" | "THERMAL_MONO" | "HIGH_FLASH";
}

export interface MediaForensicRequest {
  mode: "TEXT_OR_URL" | "VIDEO_FORENSICS";
  claimText: string;
  sourceUrl?: string;
  claimedLocationAr?: string;
  claimedDate?: string;
  videoMeta?: {
    fileName: string;
    fileSizeBytes: number;
    durationSec: number;
    width: number;
    height: number;
    mimeType: string;
    sha256: string;
  };
  frames?: ExtractedVideoFrame[];
}

export interface MediaForensicResult {
  id: string;
  analyzedAtUtc: string;
  verdict:
    | "VERIFIED_ROOT_SOURCE"
    | "PARTIALLY_CORROBORATED"
    | "UNVERIFIED_SECONDARY_CLAIM"
    | "HIGH_MANIPULATION_OR_OLD_FOOTAGE_RISK";
  verdictLabelAr: string;
  authenticityScore: number; // 0-100
  isRootSourceDomain: boolean;
  matchedRootSourceNameAr?: string;
  arabicNeutralRewrite: string;
  strategicInterpretationAr: string;
  findingsAr: string[];
  redFlagsAr: string[];
  visualFrameObservationsAr?: string[];
  matchedDispatches: Array<{
    id: string;
    headlineAr: string;
    rootSourceNameAr: string;
    accuracyScore: number;
  }>;
  aiEngineUsed: string;
}

export type AiProviderChoice = "auto" | "gemini" | "openai" | "anthropic" | "local";

export interface CloudSentinelSettings {
  aiProvider: AiProviderChoice;
  geminiApiKey?: string;
  openaiApiKey?: string;
  anthropicApiKey?: string;
  fcmServerKeyOrWebhook?: string;
  cloudServerPublicUrl: string;
  scanIntervalSeconds: number;
  minAccuracyForPush: number; // e.g., 78
  notifySeverities: AlertSeverity[];
  watchedTheaters: WarTheaterId[];
  strictRootOnlyMode: boolean; // Always true per user requirement, configurable lock
  soundAlertsEnabled: boolean;
}

export interface SentinelTelemetry {
  status: "ARMED_24_7" | "SCANNING";
  startedAtUtc: string;
  lastHeartbeatUtc: string;
  lastScanUtc: string;
  nextScanInSeconds: number;
  totalScansCompleted: number;
  activeRootSourcesCount: number;
  totalVerifiedDispatches: number;
  totalRejectedNoiseCount: number;
  networkFeedMode: "LIVE_CLOUD_FEEDS" | "SANDBOX_RESTRICTED_STANDBY";
  configuredAiEngine: string;
}
