"use client";

import { useRef, useState } from "react";
import {
  AlertOctagon,
  CheckCircle2,
  FileVideo,
  FileWarning,
  Film,
  Fingerprint,
  Loader2,
  ScanSearch,
  Sparkles,
  Upload,
} from "lucide-react";
import { MediaForensicResult } from "@/lib/types/geointel";
import {
  buildSampleTacticalVideoBundle,
  ExtractedVideoBundle,
  extractVideoForensicsFromFile,
} from "@/lib/client/video-extractor";
import { apiUrl } from "@/lib/client/native-bridge";

interface MediaForensicsLabProps {
  initialHistory: MediaForensicResult[];
}

export default function MediaForensicsLab({
  initialHistory,
}: MediaForensicsLabProps) {
  const [mode, setMode] = useState<"VIDEO_FORENSICS" | "TEXT_OR_URL">(
    "VIDEO_FORENSICS"
  );
  const [claimText, setClaimText] = useState(
    "رصد ليلي عبر كاميرا ملاحة بحرية لانفجار قرب سفينة تجارية على بُعد 68 ميلًا بحريًا جنوب غرب الحديدة وفق بلاغ UKMTO."
  );
  const [sourceUrl, setSourceUrl] = useState(
    "https://www.ukmto.org/indian-ocean/recent-incidents"
  );
  const [claimedLocationAr, setClaimedLocationAr] = useState(
    "جنوب البحر الأحمر — مضيق باب المندب"
  );
  const [videoBundle, setVideoBundle] = useState<ExtractedVideoBundle | null>(
    null
  );
  const [extractingVideo, setExtractingVideo] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [currentResult, setCurrentResult] =
    useState<MediaForensicResult | null>(initialHistory[0] || null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleVideoFileChange = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setErrorMsg("");
    setExtractingVideo(true);
    try {
      const bundle = await extractVideoForensicsFromFile(file);
      setVideoBundle(bundle);
    } catch (err) {
      setErrorMsg(
        err instanceof Error ? err.message : "تعذر قراءة ملف الفيديو"
      );
    } finally {
      setExtractingVideo(false);
    }
  };

  const handleLoadSampleVideo = () => {
    setErrorMsg("");
    const sample = buildSampleTacticalVideoBundle();
    setVideoBundle(sample);
    setMode("VIDEO_FORENSICS");
    setClaimText(
      "لقطة بصرية ليلية توثق وميض انفجار بحري في محيط الممر الملاحي جنوب البحر الأحمر متزامن مع بلاغ UKMTO الرسمي."
    );
    setSourceUrl("https://www.ukmto.org/indian-ocean/recent-incidents");
    setClaimedLocationAr("جنوب البحر الأحمر — 14°12'N 42°10'E");
  };

  const handleLoadRumorPreset = () => {
    setErrorMsg("");
    setMode("TEXT_OR_URL");
    setVideoBundle(null);
    setClaimText(
      "شاهد قبل الحذف!! مصادر سرية غير معلنة تؤكد دمار شامل وإغراق 4 مدمرات حربية بالكامل خلال 5 دقائق الليلة!"
    );
    setSourceUrl("https://tiktok.com/@viral-clip-unverified/video/998811");
    setClaimedLocationAr("موقع غير محدد");
  };

  const handleRunAnalysis = async () => {
    setErrorMsg("");
    if (!claimText.trim()) {
      setErrorMsg("يرجى إدخال وصف المقطع أو نص الخبر المراد التحقق منه.");
      return;
    }

    setAnalyzing(true);
    try {
      const payload = {
        mode,
        claimText,
        sourceUrl,
        claimedLocationAr,
        videoMeta:
          mode === "VIDEO_FORENSICS" && videoBundle
            ? {
                fileName: videoBundle.fileName,
                fileSizeBytes: videoBundle.fileSizeBytes,
                durationSec: videoBundle.durationSec,
                width: videoBundle.width,
                height: videoBundle.height,
                mimeType: videoBundle.mimeType,
                sha256: videoBundle.sha256,
              }
            : undefined,
        frames:
          mode === "VIDEO_FORENSICS" && videoBundle
            ? videoBundle.frames
            : undefined,
      };

      const res = await fetch(apiUrl("/api/analyze-media"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const json = await res.json();
      if (!res.ok || !json.ok) {
        throw new Error(json.error || "حدث خطأ أثناء الفحص الجنائي");
      }
      setCurrentResult(json.result as MediaForensicResult);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "فشل الاتصال بالخادم");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="grid gap-5 lg:grid-cols-12">
      {/* Input Column */}
      <div className="space-y-4 rounded-2xl border border-slate-800 bg-[#0b1220] p-5 lg:col-span-6">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <ScanSearch className="h-5 w-5 text-cyan-400" />
            <div>
              <h2 className="text-base font-bold text-white">
                مختبر التحقق الجنائي من الفيديوهات والنصوص الحربية
              </h2>
              <p className="text-xs text-slate-400">
                فحص الإطارات البصرية، البصمة الرقمية SHA-256، ومطابقة النطاق مع المصادر الأم
              </p>
            </div>
          </div>
        </div>

        {/* Mode Switcher */}
        <div className="grid grid-cols-2 gap-2 rounded-xl border border-slate-800 bg-slate-950 p-1">
          <button
            type="button"
            onClick={() => setMode("VIDEO_FORENSICS")}
            className={`flex items-center justify-center gap-2 rounded-lg py-2 text-xs font-bold transition ${
              mode === "VIDEO_FORENSICS"
                ? "bg-cyan-500/20 text-cyan-200 border border-cyan-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Film className="h-4 w-4" />
            <span>تحليل فيديو حربي + نص</span>
          </button>

          <button
            type="button"
            onClick={() => setMode("TEXT_OR_URL")}
            className={`flex items-center justify-center gap-2 rounded-lg py-2 text-xs font-bold transition ${
              mode === "TEXT_OR_URL"
                ? "bg-emerald-500/20 text-emerald-200 border border-emerald-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <FileWarning className="h-4 w-4" />
            <span>التحقق من خبر / رابط عاجل</span>
          </button>
        </div>

        {/* Quick Test Scenarios */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-semibold text-slate-400">
            تجارب فورية:
          </span>
          <button
            type="button"
            onClick={handleLoadSampleVideo}
            className="rounded-lg border border-cyan-500/35 bg-cyan-500/10 px-2.5 py-1 text-[11px] font-semibold text-cyan-300 hover:bg-cyan-500/20"
          >
            عينة فيديو ليلي موثق (UKMTO)
          </button>
          <button
            type="button"
            onClick={handleLoadRumorPreset}
            className="rounded-lg border border-rose-500/35 bg-rose-500/10 px-2.5 py-1 text-[11px] font-semibold text-rose-300 hover:bg-rose-500/20"
          >
            اختبار كشف إشاعة حربية مضللة
          </button>
        </div>

        {/* Video Upload Box */}
        {mode === "VIDEO_FORENSICS" && (
          <div className="space-y-3 rounded-xl border border-dashed border-slate-700 bg-slate-950/60 p-4">
            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/webm,video/quicktime,video/*"
              onChange={handleVideoFileChange}
              className="hidden"
            />

            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <FileVideo className="h-6 w-6 text-cyan-400" />
                <div>
                  <p className="text-xs font-bold text-slate-200">
                    ارفع مقطع فيديو ميداني (.MP4 / .WEBM / .MOV)
                  </p>
                  <p className="text-[11px] text-slate-400">
                    يستخرج التطبيق 4 إطارات مرجعية ويحسب بصمة SHA-256 ويفحص الطيف الضوئي والأبعاد
                  </p>
                </div>
              </div>

              <button
                type="button"
                disabled={extractingVideo}
                onClick={() => fileInputRef.current?.click()}
                className="inline-flex items-center gap-1.5 rounded-xl border border-cyan-500/40 bg-cyan-500/15 px-3 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-500/25"
              >
                {extractingVideo ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Upload className="h-4 w-4" />
                )}
                <span>اختيار ملف فيديو</span>
              </button>
            </div>

            {videoBundle && (
              <div className="space-y-2.5 border-t border-slate-800 pt-3">
                <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-300">
                  <span className="font-mono text-emerald-300">
                    {videoBundle.fileName} ({videoBundle.width}×
                    {videoBundle.height} • {videoBundle.durationSec.toFixed(1)}s)
                  </span>
                  <span className="inline-flex items-center gap-1 font-mono text-slate-400">
                    <Fingerprint className="h-3.5 w-3.5 text-cyan-400" />
                    SHA256: {videoBundle.sha256.slice(0, 16)}...
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                  {videoBundle.frames.map((frame) => (
                    <div
                      key={frame.timestampSec}
                      className="overflow-hidden rounded-lg border border-slate-800 bg-black"
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={frame.dataUrl}
                        alt={`Frame ${frame.timestampSec}s`}
                        className="h-20 w-full object-cover"
                      />
                      <div className="flex items-center justify-between px-1.5 py-1 font-mono text-[10px] text-slate-300">
                        <span>{frame.timestampSec}s</span>
                        <span className="text-cyan-400">{frame.dominantTone}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Form Fields */}
        <div className="space-y-3">
          <div>
            <label className="mb-1 block text-xs font-semibold text-slate-300">
              النص الإخباري أو الادعاء المرافق للمقطع:
            </label>
            <textarea
              rows={3}
              value={claimText}
              onChange={(e) => setClaimText(e.target.value)}
              className="w-full rounded-xl border border-slate-800 bg-slate-950 p-3 text-xs leading-relaxed text-slate-100 focus:border-cyan-500 focus:outline-none"
              placeholder="ألصق نص الخبر المتداول أو وصف الفيديو..."
            />
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-300">
                رابط المصدر (للتحقق من أصالة النطاق الأم):
              </label>
              <input
                type="text"
                dir="ltr"
                value={sourceUrl}
                onChange={(e) => setSourceUrl(e.target.value)}
                placeholder="https://reuters.com/..."
                className="w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-300">
                الموقع الجغرافي المدّعى:
              </label>
              <input
                type="text"
                value={claimedLocationAr}
                onChange={(e) => setClaimedLocationAr(e.target.value)}
                placeholder="مثال: مضيق باب المندب / القرم"
                className="w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {errorMsg && (
          <div className="rounded-xl border border-rose-500/40 bg-rose-500/15 px-3 py-2 text-xs text-rose-200">
            {errorMsg}
          </div>
        )}

        <button
          type="button"
          disabled={analyzing}
          onClick={handleRunAnalysis}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-l from-emerald-500 to-cyan-600 py-3 text-sm font-extrabold text-slate-950 shadow-lg transition hover:opacity-95 disabled:opacity-50"
        >
          {analyzing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>جاري التحقق من المصادر الأم وفحص الوسائط...</span>
            </>
          ) : (
            <>
              <ScanSearch className="h-4 w-4" />
              <span>تشغيل الفحص الجنائي وإعادة الصياغة بالعربية</span>
            </>
          )}
        </button>
      </div>

      {/* Forensic Verdict Output Column */}
      <div className="rounded-2xl border border-slate-800 bg-[#0b1220] p-5 lg:col-span-6">
        {!currentResult ? (
          <div className="flex h-full flex-col items-center justify-center py-16 text-center text-slate-400">
            <ScanSearch className="h-12 w-12 text-slate-600" />
            <p className="mt-3 text-sm font-bold text-slate-300">
              جاهز لفحص الفيديوهات والادعاءات الجيوسياسية
            </p>
            <p className="mt-1 max-w-sm text-xs">
              اختر عينة فيديو أو ألصق أي خبر عاجل للتحقق من مصدره الأم وكشف التلاعب البصري أو التهويل الدعائي.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Verdict Banner */}
            <div
              className={`rounded-xl border p-4 ${
                currentResult.authenticityScore >= 80
                  ? "border-emerald-500/40 bg-emerald-500/10"
                  : currentResult.authenticityScore >= 60
                  ? "border-amber-500/40 bg-amber-500/10"
                  : "border-rose-500/45 bg-rose-500/15"
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  {currentResult.authenticityScore >= 75 ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  ) : (
                    <AlertOctagon className="h-5 w-5 text-rose-400" />
                  )}
                  <span className="text-sm font-extrabold text-white">
                    {currentResult.verdictLabelAr}
                  </span>
                </div>
                <span className="rounded-lg bg-slate-950/80 px-3 py-1 font-mono text-sm font-extrabold text-cyan-300">
                  درجة الموثوقية: {currentResult.authenticityScore}%
                </span>
              </div>
              <p className="mt-1.5 text-[11px] text-slate-300">
                محرك الفحص المستخدم: {currentResult.aiEngineUsed}
              </p>
            </div>

            {/* Verified Neutral Arabic Rewrite */}
            <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
              <div className="mb-1.5 flex items-center gap-1.5 text-xs font-bold text-emerald-300">
                <Sparkles className="h-4 w-4" />
                <span>الصياغة العربية المحققة الخالية من التضليل:</span>
              </div>
              <p className="text-xs leading-6 text-slate-200">
                {currentResult.arabicNeutralRewrite}
              </p>
            </div>

            {/* Strategic Interpretation */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
              <div className="mb-1 text-xs font-bold text-cyan-300">
                التفسير الجيوسياسي والعسكري:
              </div>
              <p className="text-xs leading-6 text-slate-300">
                {currentResult.strategicInterpretationAr}
              </p>
            </div>

            {/* Visual Frame Observations */}
            {currentResult.visualFrameObservationsAr &&
              currentResult.visualFrameObservationsAr.length > 0 && (
                <div className="rounded-xl border border-cyan-500/25 bg-cyan-500/5 p-3.5">
                  <div className="mb-1.5 text-xs font-bold text-cyan-300">
                    نتائج الفحص البصري لإطارات الفيديو:
                  </div>
                  <ul className="list-inside list-disc space-y-1 text-xs text-slate-200">
                    {currentResult.visualFrameObservationsAr.map((obs) => (
                      <li key={obs}>{obs}</li>
                    ))}
                  </ul>
                </div>
              )}

            {/* Findings & Red Flags */}
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3.5">
                <div className="mb-1.5 text-xs font-bold text-emerald-300">
                  مؤشرات التوثيق الإيجابية:
                </div>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {currentResult.findingsAr.map((f) => (
                    <li key={f}>✓ {f}</li>
                  ))}
                </ul>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3.5">
                <div className="mb-1.5 text-xs font-bold text-rose-300">
                  تحذيرات الدقة ومؤشرات الشبهة:
                </div>
                {currentResult.redFlagsAr.length === 0 ? (
                  <p className="text-xs text-emerald-300">
                    لم تُرصد مؤشرات تلاعب أو مصادر مشبوهة.
                  </p>
                ) : (
                  <ul className="space-y-1.5 text-xs text-rose-200/90">
                    {currentResult.redFlagsAr.map((rf) => (
                      <li key={rf}>⚠ {rf}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
