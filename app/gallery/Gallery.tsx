"use client";

import { useEffect, useMemo, useState } from "react";

type Task = {
  id: string;
  folder: string;
  name: string;
  path: string;
  bytes: number;
  caption: string;
  science: string;
  thumb: string | null;
};

type Folder = { id: string; name: string; drive_id: string };

type Api = {
  root: string;
  folders: Folder[];
  tasks: Task[];
  results: Record<string, { id: string; link: string | null }>;
};

const mb = (n: number) => `${(n / 1e6).toFixed(1)} MB`;

export default function Gallery() {
  const [data, setData] = useState<Api | null>(null);
  const [folder, setFolder] = useState("all");
  const [q, setQ] = useState("");
  const [open, setOpen] = useState<Task | null>(null);

  useEffect(() => {
    fetch("/api/tasks")
      .then((r) => r.json())
      .then(setData);
  }, []);

  const items = useMemo(() => {
    if (!data) return [];
    return data.tasks.filter(
      (t) =>
        (folder === "all" || t.folder === folder) &&
        (q.trim() === "" || t.name.toLowerCase().includes(q.toLowerCase()) || t.id.includes(q.toLowerCase())),
    );
  }, [data, folder, q]);

  if (!data) return <div className="p-10 text-white/60">جارٍ التحميل…</div>;

  const uploaded = Object.keys(data.results ?? {}).length;
  const folders = data.folders.filter((f) => data.tasks.some((t) => t.folder === f.id));

  return (
    <div className="mx-auto max-w-[1400px] px-6 pb-28 pt-10 text-white">
      <header className="mb-8 border-b border-white/10 pb-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">الأرشيف الفلكي الشامل — صور الكون</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-white/60">
              {data.tasks.length} صورة ورصداً وملفاً علمياً عبر كامل الطيف الكهرومغناطيسي: راديوي، تحت
              مليمتري، تحت أحمر، مرئي، فوق بنفسجي، سيني، وغاما. كل مدخل يحمل تفسيره العلمي وخصائصه
              المرصودة وطوله الموجي ومصدره وحقوق نسبه.
            </p>
          </div>
          <div className="text-right text-xs text-white/50">
            <div>{mb(data.tasks.reduce((a, t) => a + t.bytes, 0))} إجمالي البيانات</div>
            <div>
              {uploaded} / {data.tasks.length} مرفوع إلى Drive
            </div>
            <a
              className="mt-2 inline-block text-emerald-300 hover:underline"
              href="https://drive.google.com/drive/folders/1JTJwVP-dhjA1_pAb2k1psJPCNrUiqt-i"
              target="_blank"
              rel="noreferrer"
            >
              افتح المجلد في Drive ↗
            </a>
          </div>
        </div>
      </header>

      <div className="mb-6 flex flex-wrap items-center gap-2">
        <button
          onClick={() => setFolder("all")}
          className={`rounded-full border px-3 py-1.5 text-xs ${
            folder === "all" ? "border-emerald-400 bg-emerald-400/10 text-emerald-200" : "border-white/15 text-white/70"
          }`}
        >
          الكل ({data.tasks.length})
        </button>
        {folders.map((f) => (
          <button
            key={f.id}
            onClick={() => setFolder(f.id)}
            className={`rounded-full border px-3 py-1.5 text-xs ${
              folder === f.id ? "border-emerald-400 bg-emerald-400/10 text-emerald-200" : "border-white/15 text-white/70"
            }`}
          >
            {f.name} ({data.tasks.filter((t) => t.folder === f.id).length})
          </button>
        ))}
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="ابحث…"
          className="ms-auto w-44 rounded-full border border-white/15 bg-white/5 px-4 py-1.5 text-xs outline-none focus:border-emerald-400/60"
        />
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {items.map((t) => (
          <button
            key={t.id}
            onClick={() => setOpen(t)}
            className="group overflow-hidden rounded-xl border border-white/10 bg-white/[0.03] text-start transition hover:border-white/25"
          >
            <div className="relative aspect-[4/3] bg-black">
              {t.thumb ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={`/api/thumb?name=${encodeURIComponent(t.thumb)}`}
                  alt={t.name}
                  className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.03]"
                  loading="lazy"
                />
              ) : (
                <div className="flex h-full items-center justify-center text-xs text-white/40">FITS data product</div>
              )}
            </div>
            <div className="space-y-1 p-3">
              <div className="truncate text-sm">{t.name}</div>
              <div className="line-clamp-2 text-[11px] leading-5 text-white/45">{t.science}</div>
              <div className="text-[10px] text-white/30">{mb(t.bytes)}</div>
            </div>
          </button>
        ))}
      </div>

      {open && (
        <div className="fixed inset-0 z-50 flex items-start justify-center overflow-auto bg-black/85 p-4" onClick={() => setOpen(null)}>
          <div
            className="w-full max-w-5xl rounded-2xl border border-white/10 bg-[#0a0c14] p-5"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-3 flex items-start justify-between gap-4">
              <h2 className="text-lg">{open.name}</h2>
              <button onClick={() => setOpen(null)} className="rounded border border-white/20 px-3 py-1 text-xs">
                إغلاق
              </button>
            </div>
            {open.thumb && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={`/api/thumb?name=${encodeURIComponent(open.thumb)}`} alt={open.name} className="mb-4 w-full rounded-lg" />
            )}
            <p className="whitespace-pre-wrap text-sm leading-7 text-white/80">{open.caption}</p>
          </div>
        </div>
      )}
    </div>
  );
}
