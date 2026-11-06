"use client";

import { useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  ExternalLink,
  Filter,
  Globe,
  Layers,
  MapPin,
  Scale,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
} from "lucide-react";
import {
  AlertSeverity,
  GeopoliticalDispatch,
  WarTheater,
  WarTheaterId,
} from "@/lib/types/geointel";

interface DispatchFeedAndDetailProps {
  dispatches: GeopoliticalDispatch[];
  theaters: WarTheater[];
  selectedTheater: WarTheaterId | "ALL";
  onSelectTheater: (id: WarTheaterId | "ALL") => void;
}

const SEVERITY_META: Record<
  AlertSeverity,
  { label: string; badgeClass: string; dotClass: string }
> = {
  CRITICAL: {
    label: "إنذار حرج",
    badgeClass: "border-rose-500/50 bg-rose-500/15 text-rose-200",
    dotClass: "bg-rose-500",
  },
  HIGH: {
    label: "تأهب مرتفع",
    badgeClass: "border-amber-500/50 bg-amber-500/15 text-amber-200",
    dotClass: "bg-amber-500",
  },
  MEDIUM: {
    label: "متوسط",
    badgeClass: "border-cyan-500/40 bg-cyan-500/15 text-cyan-200",
    dotClass: "bg-cyan-400",
  },
  ROUTINE: {
    label: "رصد روتيني",
    badgeClass: "border-slate-600 bg-slate-800 text-slate-300",
    dotClass: "bg-slate-400",
  },
};

function formatArabicTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString("ar-MA", {
      hour: "2-digit",
      minute: "2-digit",
      day: "2-digit",
      month: "short",
    });
  } catch {
    return iso;
  }
}

export default function DispatchFeedAndDetail({
  dispatches,
  theaters,
  selectedTheater,
  onSelectTheater,
}: DispatchFeedAndDetailProps) {
  const [severityFilter, setSeverityFilter] = useState<AlertSeverity | "ALL">(
    "ALL"
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedId, setSelectedId] = useState<string>(
    dispatches[0]?.id || ""
  );

  const filtered = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return dispatches.filter((d) => {
      if (selectedTheater !== "ALL" && d.theaterId !== selectedTheater) {
        return false;
      }
      if (severityFilter !== "ALL" && d.severity !== severityFilter) {
        return false;
      }
      if (q) {
        const hay = `${d.headlineAr} ${d.flashSummaryAr} ${d.rootSourceNameAr} ${d.locationAr} ${d.tagsAr.join(
          " "
        )} ${d.originalHeadline}`.toLowerCase();
        return hay.includes(q);
      }
      return true;
    });
  }, [dispatches, selectedTheater, severityFilter, searchQuery]);

  const activeDispatch =
    filtered.find((d) => d.id === selectedId) || filtered[0] || null;

  return (
    <div className="space-y-4">
      {/* Filter & Search Bar */}
      <div className="rounded-2xl border border-slate-800 bg-[#0b1220] p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          {/* Theater Pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="ml-1 inline-flex items-center gap-1 text-xs font-semibold text-slate-400">
              <Filter className="h-3.5 w-3.5 text-cyan-400" />
              المسرح:
            </span>
            <button
              type="button"
              onClick={() => onSelectTheater("ALL")}
              className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold transition ${
                selectedTheater === "ALL"
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                  : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200"
              }`}
            >
              جميع المسارح ({dispatches.length})
            </button>
            {theaters.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => onSelectTheater(t.id)}
                className={`rounded-lg px-2.5 py-1.5 text-xs font-semibold transition ${
                  selectedTheater === t.id
                    ? "bg-cyan-500/20 text-cyan-200 border border-cyan-500/40"
                    : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200"
                }`}
              >
                {t.shortNameAr}
              </button>
            ))}
          </div>

          {/* Search & Severity */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative flex-1 sm:w-60">
              <Search className="pointer-events-none absolute right-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="ابحث بالمصدر، المضيق، المنظومة..."
                className="w-full rounded-xl border border-slate-800 bg-slate-950 py-2 pr-9 pl-3 text-xs text-slate-100 placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
              />
            </div>

            <select
              value={severityFilter}
              onChange={(e) =>
                setSeverityFilter(e.target.value as AlertSeverity | "ALL")
              }
              className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
            >
              <option value="ALL">كل درجات التأهب</option>
              <option value="CRITICAL">إنذار حرج فقط</option>
              <option value="HIGH">تأهب مرتفع</option>
              <option value="MEDIUM">متوسط</option>
            </select>
          </div>
        </div>
      </div>

      {/* Master-Detail Split */}
      <div className="grid gap-5 lg:grid-cols-12">
        {/* Left/Right List Column */}
        <div className="space-y-3 lg:col-span-5">
          {filtered.length === 0 ? (
            <div className="rounded-2xl border border-slate-800 bg-[#0b1220] p-8 text-center">
              <AlertTriangle className="mx-auto h-8 w-8 text-amber-400" />
              <p className="mt-2 text-sm font-semibold text-slate-200">
                لا توجد برقيات مطابقة لفلتر البحث الحالي
              </p>
              <p className="mt-1 text-xs text-slate-400">
                جرّب اختيار «جميع المسارح» أو اضغط «اختبار إنذار عاجل» في الشريط العلوي.
              </p>
            </div>
          ) : (
            filtered.map((item) => {
              const sev = SEVERITY_META[item.severity];
              const isSelected = activeDispatch?.id === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedId(item.id)}
                  className={`w-full rounded-2xl border p-4 text-right transition ${
                    isSelected
                      ? "border-emerald-500/60 bg-gradient-to-br from-[#101c30] to-[#0b1322] shadow-[0_0_24px_rgba(16,185,129,0.1)]"
                      : "border-slate-800/90 bg-[#0b1220] hover:border-slate-700"
                  }`}
                >
                  {/* Card Top Meta */}
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${sev.badgeClass}`}
                      >
                        <span
                          className={`h-1.5 w-1.5 rounded-full ${sev.dotClass}`}
                        />
                        {sev.label}
                      </span>
                      <span className="rounded-md border border-slate-700 bg-slate-900 px-2 py-0.5 font-mono text-[11px] font-semibold text-cyan-300">
                        {item.rootSourceDomain}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <span className="rounded-full border border-emerald-500/35 bg-emerald-500/15 px-2.5 py-0.5 font-mono text-[11px] font-bold text-emerald-300">
                        {item.accuracy.overallScore}% دقة
                      </span>
                    </div>
                  </div>

                  {/* Arabic Neutral Headline */}
                  <h3 className="mt-2.5 text-sm font-bold leading-relaxed text-slate-50">
                    {item.headlineAr}
                  </h3>

                  <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-400">
                    {item.flashSummaryAr}
                  </p>

                  {/* Footer Meta */}
                  <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-slate-800/70 pt-2.5 text-[11px] text-slate-400">
                    <span className="inline-flex items-center gap-1 text-slate-300">
                      <MapPin className="h-3 w-3 text-cyan-400" />
                      {item.locationAr}
                    </span>
                    <span className="inline-flex items-center gap-1 font-mono">
                      <Clock className="h-3 w-3" />
                      {formatArabicTime(item.capturedAtUtc)}
                    </span>
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Detailed Arabic Strategic Dossier Column */}
        <div className="lg:col-span-7">
          {activeDispatch && (
            <div className="sticky top-20 space-y-4 rounded-2xl border border-slate-800 bg-[#0b1220] p-5 shadow-2xl">
              {/* Top Provenance Banner */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold ${
                      SEVERITY_META[activeDispatch.severity].badgeClass
                    }`}
                  >
                    {SEVERITY_META[activeDispatch.severity].label}
                  </span>

                  <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/35 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-300">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    {activeDispatch.verificationBadge ===
                    "CONFIRMED_MULTI_PRIMARY"
                      ? "مؤكد من المصدر الأم + تقاطع مستقل"
                      : activeDispatch.verificationBadge ===
                        "OFFICIAL_BELLIGERENT_STATEMENT"
                      ? "بيان رسمي لطرف ذي صلة (خاضع للتقاطع)"
                      : "التقاط أولي مباشر من وكالة أم"}
                  </span>

                  <span className="rounded-full border border-slate-700 bg-slate-900 px-2.5 py-1 text-[11px] text-slate-300">
                    {activeDispatch.captureMode === "LIVE_RSS_VERIFIED"
                      ? "التقاط حي مباشر (RSS)"
                      : activeDispatch.captureMode === "MANUAL_VERIFIED_SCAN"
                      ? "فحص تأهب فوري"
                      : "سجل مرجعي موثق"}
                  </span>
                </div>

                <span className="font-mono text-xs text-slate-400">
                  {activeDispatch.coordinates.label}
                </span>
              </div>

              {/* Headline & Detailed Arabic Rewrite */}
              <div>
                <h2 className="text-lg font-extrabold leading-snug text-white sm:text-xl">
                  {activeDispatch.headlineAr}
                </h2>

                <div className="mt-3 rounded-xl border border-emerald-500/25 bg-emerald-500/5 p-4">
                  <div className="mb-1.5 flex items-center gap-1.5 text-xs font-bold text-emerald-300">
                    <Sparkles className="h-4 w-4" />
                    <span>الصياغة العربية الدقيقة (خالية من التهويل والانحياز)</span>
                  </div>
                  <p className="text-sm leading-7 text-slate-200">
                    {activeDispatch.detailedRewriteAr}
                  </p>
                </div>
              </div>

              {/* 4-Axis Accuracy & Verification Matrix */}
              <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-cyan-300">
                    <ShieldCheck className="h-4 w-4 text-emerald-400" />
                    <span>مصفوفة التحقق ومؤشر الدقة الصارم</span>
                  </div>
                  <span className="rounded-lg bg-emerald-500/20 px-2.5 py-1 font-mono text-sm font-extrabold text-emerald-300">
                    {activeDispatch.accuracy.overallScore}% / 100%
                  </span>
                </div>

                <div className="mt-3 grid gap-3 sm:grid-cols-2">
                  {[
                    {
                      label: "أصالة المصدر الأم (وزن 35%)",
                      val: activeDispatch.accuracy.rootAuthenticity,
                    },
                    {
                      label: "التقاطع المستقل للمصادر (وزن 30%)",
                      val: activeDispatch.accuracy.independentCorroboration,
                    },
                    {
                      label: "الاتساق الجغرافي والزمني (وزن 20%)",
                      val: activeDispatch.accuracy.geoTemporalConsistency,
                    },
                    {
                      label: "سلامة الوسائط والنص الأصلي (وزن 15%)",
                      val: activeDispatch.accuracy.mediaIntegrity,
                    },
                  ].map((axis) => (
                    <div key={axis.label}>
                      <div className="flex justify-between text-[11px] text-slate-300">
                        <span>{axis.label}</span>
                        <span className="font-mono font-bold text-emerald-400">
                          {axis.val}%
                        </span>
                      </div>
                      <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                        <div
                          className="h-full rounded-full bg-gradient-to-l from-emerald-400 to-cyan-500"
                          style={{ width: `${axis.val}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <p className="mt-3 text-xs text-slate-400">
                  <strong className="text-slate-200">مبرر التقييم: </strong>
                  {activeDispatch.accuracy.rationaleAr}
                </p>
              </div>

              {/* Verbatim Root Source & Cross-Corroboration Chain */}
              <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4 space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-200">
                    <Globe className="h-4 w-4 text-cyan-400" />
                    <span>المصدر الأم الملتقط منه الخبر: {activeDispatch.rootSourceNameAr}</span>
                  </div>
                  <a
                    href={activeDispatch.rootSourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-1 text-[11px] font-semibold text-cyan-300 hover:bg-cyan-500/20"
                  >
                    <span>فتح المصدر الأصلي ({activeDispatch.rootSourceDomain})</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>

                <div
                  dir="ltr"
                  className="rounded-lg border border-slate-800 bg-slate-950 p-3 font-mono text-xs leading-relaxed text-slate-300"
                >
                  <div className="font-bold text-cyan-300">
                    {activeDispatch.originalHeadline}
                  </div>
                  <p className="mt-1 text-slate-400">
                    &ldquo;{activeDispatch.originalExcerpt}&rdquo;
                  </p>
                </div>

                {activeDispatch.corroboratingSources.length > 0 && (
                  <div className="space-y-2 pt-1">
                    <div className="text-xs font-bold text-emerald-300">
                      المصادر الأم المستقلة المؤكدة للواقعة ({activeDispatch.corroboratingSources.length}):
                    </div>
                    {activeDispatch.corroboratingSources.map((cs) => (
                      <div
                        key={`${cs.sourceId}-${cs.timestampUtc}`}
                        className="flex flex-col gap-1 rounded-lg border border-slate-800 bg-slate-950/70 p-2.5 text-xs sm:flex-row sm:items-center sm:justify-between"
                      >
                        <div>
                          <span className="font-bold text-slate-200">
                            {cs.nameAr}
                          </span>{" "}
                          <span className="font-mono text-[11px] text-cyan-400">
                            ({cs.officialDomain})
                          </span>
                          <p className="mt-0.5 text-slate-400">
                            {cs.confirmationNoteAr}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Deep Geopolitical & Military Strategic Explanation */}
              <div className="space-y-3 rounded-xl border border-amber-500/25 bg-amber-500/[0.04] p-4">
                <div className="flex items-center gap-2 text-sm font-bold text-amber-300">
                  <Layers className="h-4 w-4" />
                  <span>التفسير العسكري والجيوسياسي المعمّق</span>
                </div>

                <div className="space-y-2 text-xs leading-6 text-slate-200">
                  <div>
                    <strong className="text-amber-200">
                      • الأهمية العملياتية والاستراتيجية:{" "}
                    </strong>
                    {activeDispatch.strategicExplanation.operationalImpactAr}
                  </div>

                  <div>
                    <strong className="text-cyan-200">
                      • ميزان الروايات وتحليل زاوية المصدر:{" "}
                    </strong>
                    <span className="inline-flex items-center gap-1">
                      <Scale className="inline h-3.5 w-3.5 text-cyan-400" />
                    </span>{" "}
                    {activeDispatch.strategicExplanation.narrativeBalanceAr}
                  </div>

                  <div>
                    <strong className="text-slate-100">
                      • الخلفية الجيوتاريخية:{" "}
                    </strong>
                    {activeDispatch.strategicExplanation.historicalContextAr}
                  </div>
                </div>

                {/* Military Systems */}
                <div className="pt-1">
                  <div className="mb-1.5 flex items-center gap-1.5 text-xs font-bold text-slate-300">
                    <Target className="h-3.5 w-3.5 text-rose-400" />
                    <span>المنظومات العسكرية والوسائط المرصودة:</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {activeDispatch.strategicExplanation.militarySystemsAr.map(
                      (sys) => (
                        <span
                          key={sys}
                          className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-[11px] text-slate-200"
                        >
                          {sys}
                        </span>
                      )
                    )}
                  </div>
                </div>

                {/* 24-72h Scenarios */}
                <div className="border-t border-slate-800/80 pt-2.5">
                  <div className="text-xs font-bold text-emerald-300">
                    السيناريوهات المحتملة خلال 24 – 72 ساعة القادمة:
                  </div>
                  <ul className="mt-1.5 list-inside list-disc space-y-1 text-xs text-slate-300">
                    {activeDispatch.strategicExplanation.scenarios24to72hAr.map(
                      (sc) => (
                        <li key={sc}>{sc}</li>
                      )
                    )}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
