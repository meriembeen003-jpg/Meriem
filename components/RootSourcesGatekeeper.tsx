"use client";

import { useState } from "react";
import {
  Ban,
  CheckCircle2,
  PlusCircle,
  Shield,
  ShieldAlert,
} from "lucide-react";
import {
  RejectedNoiseEntry,
  RootSource,
  SourceCategory,
} from "@/lib/types/geointel";
import { apiUrl } from "@/lib/client/native-bridge";

interface RootSourcesGatekeeperProps {
  rootSources: RootSource[];
  rejectedNoise: RejectedNoiseEntry[];
  onRefreshState: () => void;
}

const CATEGORY_LABELS: Record<SourceCategory | "ALL", string> = {
  ALL: "جميع المصادر الأم",
  GLOBAL_WIRE_AGENCY: "وكالات الأنباء الدولية الأم",
  DEFENSE_MINISTRY: "وزارات الدفاع والقيادات الرسمية",
  MARITIME_INTL_MONITOR: "هيئات الرقابة البحرية والنووية والأممية",
  STRATEGIC_INSTITUTE: "مراكز الرصد العسكري والتسلح",
};

export default function RootSourcesGatekeeper({
  rootSources,
  rejectedNoise,
  onRefreshState,
}: RootSourcesGatekeeperProps) {
  const [catFilter, setCatFilter] = useState<SourceCategory | "ALL">("ALL");
  const [newNameAr, setNewNameAr] = useState("");
  const [newShortCode, setNewShortCode] = useState("");
  const [newRssUrl, setNewRssUrl] = useState("");
  const [newCategory, setNewCategory] =
    useState<SourceCategory>("GLOBAL_WIRE_AGENCY");
  const [formMsg, setFormMsg] = useState<{
    type: "ok" | "err";
    text: string;
  } | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const visibleSources = rootSources.filter(
    (s) => catFilter === "ALL" || s.category === catFilter
  );

  const handleToggleSource = async (sourceId: string, enabled: boolean) => {
    await fetch(apiUrl("/api/sources"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "toggle", sourceId, enabled }),
    });
    onRefreshState();
  };

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormMsg(null);
    setSubmitting(true);
    try {
      const res = await fetch(apiUrl("/api/sources"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "add",
          nameAr: newNameAr,
          shortCode: newShortCode || "OFFICIAL",
          rssUrl: newRssUrl,
          category: newCategory,
        }),
      });
      const json = await res.json();
      if (!res.ok || !json.ok) {
        setFormMsg({
          type: "err",
          text: json.error || "تعذر قبول الرابط في بوابة المصادر الأم",
        });
        onRefreshState();
        return;
      }
      setFormMsg({
        type: "ok",
        text: "تم اعتماد المصدر الأم بنجاح وإدراجه في دورة الرصد السحابي المستمر.",
      });
      setNewNameAr("");
      setNewShortCode("");
      setNewRssUrl("");
      onRefreshState();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Strict Policy Banner */}
      <div className="rounded-2xl border border-emerald-500/35 bg-gradient-to-l from-emerald-500/10 to-[#0b1220] p-5">
        <div className="flex items-start gap-3">
          <Shield className="mt-0.5 h-6 w-6 shrink-0 text-emerald-400" />
          <div>
            <h2 className="text-base font-bold text-white">
              بروتوكول الدقة القصوى: الالتقاط من المصادر الأم فقط (Strict Root-Source Gatekeeper)
            </h2>
            <p className="mt-1 text-xs leading-relaxed text-slate-300">
              يرفض خادم «راصد» السحابي تلقائيًا أي خبر منقول عن حسابات التواصل المجهولة أو مدونات التجميع الثانوية. لا يُلتقط الخبر إلا من النطاقات الرسمية لوكالات الأنباء الأم، وزارات الدفاع، الأمم المتحدة، الوكالة الدولية للطاقة الذرية (IAEA)، وهيئات الملاحة الرسمية (UKMTO)، مع وضع وسم صريح على بيانات الأطراف المتحاربة وإخضاعها للتقاطع الميداني.
            </p>
          </div>
        </div>
      </div>

      {/* Category Filter + Add Official Feed */}
      <div className="grid gap-5 lg:grid-cols-12">
        <div className="space-y-4 lg:col-span-8">
          <div className="flex flex-wrap gap-1.5">
            {(Object.keys(CATEGORY_LABELS) as Array<SourceCategory | "ALL">).map(
              (key) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setCatFilter(key)}
                  className={`rounded-xl border px-3 py-1.5 text-xs font-semibold transition ${
                    catFilter === key
                      ? "border-cyan-500/50 bg-cyan-500/15 text-cyan-200"
                      : "border-slate-800 bg-[#0b1220] text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {CATEGORY_LABELS[key]}
                </button>
              )
            )}
          </div>

          {/* Sources Cards */}
          <div className="grid gap-3 sm:grid-cols-2">
            {visibleSources.map((src) => (
              <div
                key={src.id}
                className={`rounded-2xl border p-4 transition ${
                  src.enabled
                    ? "border-slate-800 bg-[#0b1220]"
                    : "border-slate-800/50 bg-slate-950/40 opacity-65"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="rounded-md bg-cyan-500/15 px-2 py-0.5 font-mono text-[11px] font-bold text-cyan-300">
                        {src.shortCode}
                      </span>
                      <span className="font-mono text-[11px] text-emerald-400">
                        {src.officialDomain}
                      </span>
                    </div>
                    <h3 className="mt-1.5 text-sm font-bold text-slate-100">
                      {src.nameAr}
                    </h3>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleToggleSource(src.id, !src.enabled)}
                    className={`rounded-lg border px-2.5 py-1 text-[11px] font-bold transition ${
                      src.enabled
                        ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-300"
                        : "border-slate-700 bg-slate-900 text-slate-400"
                    }`}
                  >
                    {src.enabled ? "قيد الرصد" : "متوقف"}
                  </button>
                </div>

                <p className="mt-2 text-xs leading-relaxed text-slate-400">
                  {src.biasNatureAr}
                </p>

                <div className="mt-3 flex items-center justify-between border-t border-slate-800/80 pt-2.5 text-[11px]">
                  <span className="text-slate-300">
                    الموثوقية التأسيسية:{" "}
                    <strong className="font-mono text-emerald-400">
                      {src.reliabilityBaseScore}%
                    </strong>
                  </span>
                  {src.requiresCrossCheck ? (
                    <span className="inline-flex items-center gap-1 text-amber-300">
                      <ShieldAlert className="h-3 w-3" />
                      يُشترط تقاطع محايد
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-emerald-300">
                      <CheckCircle2 className="h-3 w-3" />
                      مرجعي مستقل
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Side: Add Official Root Feed + Quarantined Noise Log */}
        <div className="space-y-5 lg:col-span-4">
          <form
            onSubmit={handleAddSource}
            className="space-y-3 rounded-2xl border border-slate-800 bg-[#0b1220] p-4"
          >
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <PlusCircle className="h-4 w-4 text-emerald-400" />
              <span>إضافة خلاصة RSS لمصدر أم رسمي</span>
            </div>
            <p className="text-[11px] text-slate-400">
              تُقبل النطاقات الحكومية أو الأممية أو وكالات الأنباء المعتمدة فقط (وسترفض البوابة تلقائيًا روابط Telegram/X/TikTok).
            </p>

            <input
              type="text"
              required
              value={newNameAr}
              onChange={(e) => setNewNameAr(e.target.value)}
              placeholder="اسم المصدر بالعربية (مثال: وزارة الدفاع الفرنسية)"
              className="w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-100 focus:border-cyan-500 focus:outline-none"
            />

            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={newShortCode}
                onChange={(e) => setNewShortCode(e.target.value)}
                placeholder="الرمز (مثال: FR-MOD)"
                dir="ltr"
                className="rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-100 focus:border-cyan-500 focus:outline-none"
              />
              <select
                value={newCategory}
                onChange={(e) =>
                  setNewCategory(e.target.value as SourceCategory)
                }
                className="rounded-xl border border-slate-800 bg-slate-950 px-2.5 py-2 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
              >
                <option value="GLOBAL_WIRE_AGENCY">وكالة أنباء أم</option>
                <option value="DEFENSE_MINISTRY">وزارة دفاع رسمية</option>
                <option value="MARITIME_INTL_MONITOR">رقابة دولية/ملاحية</option>
                <option value="STRATEGIC_INSTITUTE">معهد استراتيجي</option>
              </select>
            </div>

            <input
              type="url"
              required
              dir="ltr"
              value={newRssUrl}
              onChange={(e) => setNewRssUrl(e.target.value)}
              placeholder="https://official-agency.gov/rss.xml"
              className="w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-100 focus:border-cyan-500 focus:outline-none"
            />

            {formMsg && (
              <div
                className={`rounded-xl border p-2.5 text-xs ${
                  formMsg.type === "ok"
                    ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-200"
                    : "border-rose-500/40 bg-rose-500/15 text-rose-200"
                }`}
              >
                {formMsg.text}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-xl border border-emerald-500/40 bg-emerald-500/20 py-2.5 text-xs font-bold text-emerald-200 transition hover:bg-emerald-500/30 disabled:opacity-50"
            >
              فحص النطاق وإدراج المصدر الأم
            </button>
          </form>

          {/* Quarantined Secondary Rumors Log */}
          <div className="space-y-3 rounded-2xl border border-rose-500/25 bg-[#0b1220] p-4">
            <div className="flex items-center gap-2 text-sm font-bold text-rose-300">
              <Ban className="h-4 w-4" />
              <span>سجل الشائعات والمصادر الثانوية المحجوبة ({rejectedNoise.length})</span>
            </div>
            <div className="space-y-2.5">
              {rejectedNoise.slice(0, 6).map((rej) => (
                <div
                  key={rej.id}
                  className="rounded-xl border border-slate-800 bg-slate-950/70 p-3 text-xs"
                >
                  <div className="font-mono text-[11px] font-semibold text-rose-400">
                    ✗ {rej.originDomainOrHandle}
                  </div>
                  <div
                    dir="ltr"
                    className="mt-1 truncate font-mono text-[11px] text-slate-400"
                  >
                    {rej.rawHeadline}
                  </div>
                  <p className="mt-1.5 text-[11px] leading-relaxed text-slate-300">
                    {rej.rejectionReasonAr}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
