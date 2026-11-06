"use client";

import { Compass, Crosshair, Anchor, ShieldAlert, ArrowLeft } from "lucide-react";
import { GeopoliticalDispatch, WarTheater, WarTheaterId } from "@/lib/types/geointel";

interface WarMapRadarProps {
  theaters: WarTheater[];
  dispatches: GeopoliticalDispatch[];
  selectedTheater: WarTheaterId | "ALL";
  onSelectTheater: (id: WarTheaterId | "ALL") => void;
  onJumpToFeedWithTheater: (id: WarTheaterId) => void;
}

export default function WarMapRadar({
  theaters,
  dispatches,
  selectedTheater,
  onSelectTheater,
  onJumpToFeedWithTheater,
}: WarMapRadarProps) {
  const countByTheater = (id: WarTheaterId) =>
    dispatches.filter((d) => d.theaterId === id).length;

  const activeObj =
    selectedTheater === "ALL"
      ? theaters[0]
      : theaters.find((t) => t.id === selectedTheater) || theaters[0];

  return (
    <div className="space-y-5">
      {/* Top Strategic Map Card */}
      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-[#0b1220] shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 px-5 py-4">
          <div className="flex items-center gap-2.5">
            <Compass className="h-5 w-5 text-cyan-400" />
            <div>
              <h2 className="text-base font-bold text-slate-100">
                رادار مسارح الحروب الجيوسياسية والمضائق الاستراتيجية الحرجة
              </h2>
              <p className="text-xs text-slate-400">
                اضغط على أي بؤرة توتر على الخريطة لعرض توازن القوى والمضائق البحرية والبرقيات الموثقة من المصادر الأم
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 text-[11px]">
            <span className="inline-flex items-center gap-1.5 text-rose-300">
              <span className="h-2.5 w-2.5 rounded-full bg-rose-500" />
              مستوى 5 (اشتباك نشط / حرج)
            </span>
            <span className="inline-flex items-center gap-1.5 text-amber-300">
              <span className="h-2.5 w-2.5 rounded-full bg-amber-500" />
              مستوى 4 (تأهب عسكري مرتفع)
            </span>
          </div>
        </div>

        {/* SVG Tactical World Radar */}
        <div className="relative w-full bg-[#060a13] p-3 sm:p-5">
          <svg
            viewBox="0 0 1000 460"
            className="h-auto w-full rounded-xl border border-slate-800/70 bg-[#070d19]"
            role="img"
            aria-label="خريطة مسارح العمليات الجيوسياسية"
          >
            <defs>
              <pattern
                id="tacticalGrid"
                width="50"
                height="50"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M 50 0 L 0 0 0 50"
                  fill="none"
                  stroke="rgba(56, 189, 248, 0.07)"
                  strokeWidth="1"
                />
              </pattern>
              <radialGradient id="radarSweep" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="rgba(6, 182, 212, 0.14)" />
                <stop offset="100%" stopColor="rgba(6, 182, 212, 0)" />
              </radialGradient>
            </defs>

            <rect width="1000" height="460" fill="url(#tacticalGrid)" />

            {/* Equator & Tropics */}
            <line
              x1="0"
              y1="245"
              x2="1000"
              y2="245"
              stroke="rgba(148, 163, 184, 0.16)"
              strokeDasharray="6 6"
            />
            <line
              x1="500"
              y1="0"
              x2="500"
              y2="460"
              stroke="rgba(148, 163, 184, 0.12)"
              strokeDasharray="4 6"
            />

            {/* Stylized Continental Silhouettes for Tactical Orientation */}
            {/* North America */}
            <path
              d="M 95 75 L 255 68 L 305 135 L 245 205 L 185 225 L 120 165 Z"
              fill="#0f1b2e"
              stroke="#1e3a5f"
              strokeWidth="1.5"
            />
            {/* South America */}
            <path
              d="M 245 245 L 325 265 L 345 345 L 295 425 L 255 385 Z"
              fill="#0f1b2e"
              stroke="#1e3a5f"
              strokeWidth="1.5"
            />
            {/* Europe */}
            <path
              d="M 455 78 L 585 70 L 605 155 L 535 170 L 465 155 Z"
              fill="#122138"
              stroke="#254872"
              strokeWidth="1.5"
            />
            {/* Africa */}
            <path
              d="M 455 182 L 575 185 L 615 265 L 575 385 L 505 385 L 475 285 Z"
              fill="#111f35"
              stroke="#23446d"
              strokeWidth="1.5"
            />
            {/* Middle East & Asia */}
            <path
              d="M 585 82 L 875 85 L 895 215 L 810 265 L 710 255 L 625 230 L 585 175 Z"
              fill="#13233b"
              stroke="#284e7d"
              strokeWidth="1.5"
            />
            {/* Maritime Southeast Asia & Australia */}
            <path
              d="M 780 315 L 895 315 L 910 395 L 805 405 Z"
              fill="#0f1b2e"
              stroke="#1e3a5f"
              strokeWidth="1.5"
            />

            {/* Strategic Maritime & Subsea Corridors */}
            <polyline
              points="515,108 565,142 595,225 805,218"
              fill="none"
              stroke="rgba(6, 182, 212, 0.32)"
              strokeWidth="1.5"
              strokeDasharray="5 5"
            />
            <polyline
              points="558,262 595,225"
              fill="none"
              stroke="rgba(244, 63, 94, 0.4)"
              strokeWidth="1.5"
              strokeDasharray="3 4"
            />

            {/* Choke Point Labels */}
            <g className="text-[10px]" fill="#94a3b8" fontFamily="monospace">
              <text x="612" y="242">BAB EL-MANDEB / HORMUZ</text>
              <text x="572" y="132">BLACK SEA / DONBAS</text>
              <text x="815" y="205">TAIWAN STRAIT</text>
              <text x="435" y="98">GIUK / BALTIC</text>
            </g>

            {/* Interactive Theater Nodes */}
            {theaters.map((t) => {
              const isSelected = activeObj?.id === t.id;
              const isCritical = t.escalationLevel >= 5;
              const mainColor = isCritical ? "#f43f5e" : "#f59e0b";
              const count = countByTheater(t.id);

              return (
                <g
                  key={t.id}
                  onClick={() => onSelectTheater(t.id)}
                  className="cursor-pointer"
                >
                  <circle
                    cx={t.coordinates.mapX}
                    cy={t.coordinates.mapY}
                    r={isSelected ? 34 : 24}
                    fill={
                      isCritical
                        ? "rgba(244, 63, 94, 0.15)"
                        : "rgba(245, 158, 11, 0.14)"
                    }
                    stroke={mainColor}
                    strokeOpacity={isSelected ? 0.9 : 0.45}
                    strokeWidth={isSelected ? 2 : 1}
                  />
                  <circle
                    cx={t.coordinates.mapX}
                    cy={t.coordinates.mapY}
                    r="8"
                    fill={mainColor}
                  />
                  <rect
                    x={t.coordinates.mapX - 16}
                    y={t.coordinates.mapY + 12}
                    width="32"
                    height="16"
                    rx="4"
                    fill="#050811"
                    stroke={mainColor}
                    strokeWidth="1"
                  />
                  <text
                    x={t.coordinates.mapX}
                    y={t.coordinates.mapY + 23}
                    textAnchor="middle"
                    fill="#f8fafc"
                    fontSize="10"
                    fontFamily="monospace"
                    fontWeight="bold"
                  >
                    {count} خبر
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      </div>

      {/* Selected Theater Deep Brief + All Theaters Grid */}
      {activeObj && (
        <div className="rounded-2xl border border-cyan-500/30 bg-gradient-to-br from-[#0d1729] to-[#09101d] p-5 shadow-lg">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${
                    activeObj.escalationLevel >= 5
                      ? "border border-rose-500/40 bg-rose-500/20 text-rose-300"
                      : "border border-amber-500/40 bg-amber-500/20 text-amber-300"
                  }`}
                >
                  درجة التصعيد {activeObj.escalationLevel}/5 •{" "}
                  {activeObj.escalationLabelAr}
                </span>
                <span className="font-mono text-xs text-slate-400">
                  [{activeObj.regionCode}]
                </span>
              </div>
              <h3 className="mt-2 text-lg font-bold text-white">
                {activeObj.nameAr}
              </h3>
              <p className="mt-1.5 max-w-3xl text-sm leading-relaxed text-slate-300">
                {activeObj.strategicSummaryAr}
              </p>
            </div>

            <button
              type="button"
              onClick={() => onJumpToFeedWithTheater(activeObj.id)}
              className="inline-flex items-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/15 px-4 py-2.5 text-xs font-bold text-emerald-300 transition hover:bg-emerald-500/25"
            >
              <span>عرض برقيات هذا المسرح ({countByTheater(activeObj.id)})</span>
              <ArrowLeft className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-4 grid gap-4 pt-3 border-t border-slate-800/80 md:grid-cols-2">
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-3.5">
              <div className="flex items-center gap-2 text-xs font-bold text-cyan-300">
                <Anchor className="h-4 w-4" />
                <span>المضائق البحرية ومحاور الارتكاز الحرجة</span>
              </div>
              <div className="mt-2.5 flex flex-wrap gap-1.5">
                {activeObj.chokePointsAr.map((cp) => (
                  <span
                    key={cp}
                    className="rounded-lg border border-slate-700/80 bg-slate-800/80 px-2.5 py-1 text-xs text-slate-200"
                  >
                    {cp}
                  </span>
                ))}
              </div>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-3.5">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-300">
                <ShieldAlert className="h-4 w-4" />
                <span>القوات والمنظومات العسكرية الفاعلة في المسرح</span>
              </div>
              <ul className="mt-2 space-y-1 text-xs text-slate-300">
                {activeObj.activeForcesAr.map((f) => (
                  <li key={f} className="flex items-center gap-1.5">
                    <Crosshair className="h-3 w-3 shrink-0 text-amber-400" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Quick Theater Selector Cards */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {theaters.map((t) => {
          const active = activeObj?.id === t.id;
          return (
            <button
              key={t.id}
              type="button"
              onClick={() => onSelectTheater(t.id)}
              className={`rounded-xl border p-3.5 text-right transition ${
                active
                  ? "border-cyan-400/60 bg-cyan-500/10 shadow-md"
                  : "border-slate-800 bg-[#0b1220] hover:border-slate-700"
              }`}
            >
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-mono text-slate-400">{t.regionCode}</span>
                <span
                  className={`rounded-full px-2 py-0.5 font-bold ${
                    t.escalationLevel >= 5
                      ? "bg-rose-500/20 text-rose-300"
                      : "bg-amber-500/20 text-amber-300"
                  }`}
                >
                  {countByTheater(t.id)} برقية
                </span>
              </div>
              <p className="mt-1.5 text-xs font-bold text-slate-100">
                {t.shortNameAr}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
