"use client";

import {
  Bell,
  BellRing,
  Radio,
  RefreshCw,
  ShieldCheck,
  Volume2,
  VolumeX,
  Zap,
} from "lucide-react";
import { SentinelTelemetry } from "@/lib/types/geointel";

interface TelemetryHeaderProps {
  telemetry: SentinelTelemetry | null;
  sseConnected: boolean;
  notificationsGranted: boolean;
  soundEnabled: boolean;
  isScanningNow: boolean;
  onForceScan: (drill: boolean) => void;
  onRequestNotifications: () => void;
  onToggleSound: () => void;
}

export default function TelemetryHeader({
  telemetry,
  sseConnected,
  notificationsGranted,
  soundEnabled,
  isScanningNow,
  onForceScan,
  onRequestNotifications,
  onToggleSound,
}: TelemetryHeaderProps) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/90 bg-[#070b14]/95 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3">
        {/* Brand & Vigilance Status */}
        <div className="flex items-center gap-3">
          <div className="relative flex h-11 w-11 items-center justify-center rounded-xl border border-emerald-500/40 bg-emerald-500/10 shadow-[0_0_20px_rgba(16,185,129,0.18)]">
            <Radio className="h-5 w-5 text-emerald-400" />
            <span className="absolute -top-1 -left-1 flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-500" />
            </span>
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-slate-50 sm:text-xl">
                راصِـد <span className="text-emerald-400">| RASED</span>
              </h1>
              <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/15 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-300">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                {sseConnected ? "متأهب 24/7 • بث حي متصل" : "وضع التأهب المستمر"}
              </span>
              <span className="hidden rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-0.5 text-[11px] font-medium text-cyan-300 md:inline-flex">
                المصادر الأم فقط (Strict Root-Only)
              </span>
            </div>
            <p className="mt-0.5 text-xs text-slate-400">
              منظومة الإنذار المبكر والرصد الجيوسياسي والعسكري • التحقق من المصدر الأصلي والصياغة العربية الدقيقة
            </p>
          </div>
        </div>

        {/* Live Telemetry Counters & Action Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {telemetry && (
            <div className="hidden items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/70 px-3 py-1.5 text-xs xl:flex">
              <div className="flex items-center gap-1.5 text-slate-300">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                <span>المصادر الأم النشطة:</span>
                <strong className="font-mono text-emerald-300">
                  {telemetry.activeRootSourcesCount}
                </strong>
              </div>
              <span className="text-slate-700">|</span>
              <div className="text-slate-300">
                <span>شائعات حُجبت:</span>{" "}
                <strong className="font-mono text-amber-300">
                  {telemetry.totalRejectedNoiseCount}
                </strong>
              </div>
              <span className="text-slate-700">|</span>
              <div className="text-slate-400">
                <span>الفحص القادم:</span>{" "}
                <strong className="font-mono text-cyan-300">
                  {telemetry.nextScanInSeconds}ث
                </strong>
              </div>
            </div>
          )}

          {/* Audio Siren Toggle */}
          <button
            type="button"
            onClick={onToggleSound}
            title={soundEnabled ? "كتم صافرة الإنذار الصوتي" : "تفعيل صافرة الإنذار الصوتي"}
            className={`inline-flex items-center gap-1.5 rounded-xl border px-2.5 py-2 text-xs font-medium transition ${
              soundEnabled
                ? "border-cyan-500/40 bg-cyan-500/10 text-cyan-200 hover:bg-cyan-500/20"
                : "border-slate-700 bg-slate-900 text-slate-400 hover:text-slate-200"
            }`}
          >
            {soundEnabled ? (
              <Volume2 className="h-4 w-4 text-cyan-400" />
            ) : (
              <VolumeX className="h-4 w-4" />
            )}
            <span className="hidden sm:inline">
              {soundEnabled ? "الصوت مفعل" : "صامت"}
            </span>
          </button>

          {/* Push Notifications Permission */}
          <button
            type="button"
            onClick={onRequestNotifications}
            className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-medium transition ${
              notificationsGranted
                ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
                : "border-amber-500/40 bg-amber-500/15 text-amber-200 hover:bg-amber-500/25"
            }`}
          >
            {notificationsGranted ? (
              <BellRing className="h-4 w-4 text-emerald-400" />
            ) : (
              <Bell className="h-4 w-4 text-amber-400" />
            )}
            <span>
              {notificationsGranted ? "الإشعارات الفورية مفعلة" : "تفعيل الإشعارات"}
            </span>
          </button>

          {/* Force Root Scan */}
          <button
            type="button"
            disabled={isScanningNow}
            onClick={() => onForceScan(false)}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-800/90 px-3 py-2 text-xs font-semibold text-slate-100 transition hover:border-slate-600 hover:bg-slate-700 disabled:opacity-50"
          >
            <RefreshCw
              className={`h-3.5 w-3.5 text-cyan-400 ${
                isScanningNow ? "animate-spin" : ""
              }`}
            />
            <span>فحص المصادر الأم</span>
          </button>

          {/* Live Alert Drill Button */}
          <button
            type="button"
            disabled={isScanningNow}
            onClick={() => onForceScan(true)}
            className="inline-flex items-center gap-1.5 rounded-xl border border-rose-500/50 bg-rose-500/20 px-3 py-2 text-xs font-bold text-rose-200 shadow-[0_0_16px_rgba(244,63,94,0.2)] transition hover:bg-rose-500/30 disabled:opacity-50"
          >
            <Zap className="h-3.5 w-3.5 text-rose-400" />
            <span>اختبار إنذار عاجل</span>
          </button>
        </div>
      </div>
    </header>
  );
}
