"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

type Task = {
  id: string;
  folder: string;
  name: string;
  path: string;
  bytes: number;
  science: string;
};

type Folder = { id: string; name: string; drive_id: string };

type Api = {
  root: string;
  folders: Folder[];
  tasks: Task[];
  results: Record<string, { id: string; link: string | null; bytes: number }>;
};

const mb = (n: number) => `${(n / 1e6).toFixed(1)} MB`;

const mime = (name: string) => {
  if (name.endsWith(".png")) return "image/png";
  if (name.endsWith(".jpg") || name.endsWith(".jpeg")) return "image/jpeg";
  if (name.endsWith(".fits")) return "application/fits";
  if (name.endsWith(".gz")) return "application/gzip";
  return "application/octet-stream";
};

export default function Uploader() {
  const [data, setData] = useState<Api | null>(null);
  const [done, setDone] = useState<Record<string, boolean>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const [running, setRunning] = useState(false);
  const [filter, setFilter] = useState("all");
  const stop = useRef(false);

  useEffect(() => {
    fetch("/api/tasks")
      .then((r) => r.json())
      .then((d: Api) => {
        setData(d);
        const already: Record<string, boolean> = {};
        for (const k of Object.keys(d.results ?? {})) already[k] = true;
        setDone(already);
      })
      .catch(() => setLog((l) => ["تعذّر تحميل قائمة المهام", ...l]));
  }, []);

  const runOne = useCallback(
    async (t: Task) => {
      setBusy(t.id);
      try {
        // 1. hand the original file to our API route, which relays it to Drive
        const fileRes = await fetch("/api/relay", {
          method: "POST",
          headers: {
            "content-type": "application/json",
            "x-file-path": t.path,
            "x-file-name": t.name,
            "x-file-mime": mime(t.name),
            "x-parent-id": (data?.folders ?? []).find((f) => f.id === t.folder)?.drive_id ?? "",
          },
        });
        const fileJson = await fileRes.json();
        if (!fileJson.ok) throw new Error(JSON.stringify(fileJson.detail ?? fileJson.error ?? fileJson).slice(0, 300));

        // 2. keep the ledger in sync
        await fetch("/api/log", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ id: t.id, fileId: fileJson.id, link: fileJson.link, bytes: fileJson.bytes, name: t.name }),
        });
        setDone((d) => ({ ...d, [t.id]: true }));
        setLog((l) => [`✔ ${t.name} → Drive ${fileJson.id ?? ""}`, ...l].slice(0, 500));
        // 3. attach the scientific caption as a Drive comment through the same connector
        if (fileJson.id) {
          try {
            const cres = await fetch("/api/comment", {
              method: "POST",
              headers: { "content-type": "application/json" },
              body: JSON.stringify({ id: t.id, fileId: fileJson.id }),
            });
            const cjs = await cres.json();
            setLog((l) => [
              cjs.ok ? `💬 تعليق مضاف: ${t.name}` : `⚠ تعليق فشل: ${t.name} — ${cjs.error ?? cres.status}`,
              ...l,
            ].slice(0, 500));
          } catch {
            setLog((l) => [`⚠ تعليق فشل: ${t.name}`, ...l].slice(0, 500));
          }
        }
        return fileJson.id as string;
      } catch (err) {
        setLog((l) => [`✖ ${t.name}: ${err instanceof Error ? err.message : String(err)}`, ...l].slice(0, 500));
        return null;
      } finally {
        setBusy(null);
      }
    },
    [data],
  );

  /** Copy a ready caption payload to the clipboard (paste it as a Drive comment). */
  const copyCaption = useCallback(async (t: Task) => {
    const res = await fetch(`/api/caption?id=${encodeURIComponent(t.id)}`);
    const js = await res.json();
    await navigator.clipboard.writeText(js.caption ?? "");
    setLog((l) => [`⧉ نُسخ تعليق ${t.name}`, ...l].slice(0, 500));
  }, []);

  const pending = useMemo(
    () => (data?.tasks ?? []).filter((t) => !done[t.id] && (filter === "all" || t.folder === filter)),
    [data, done, filter],
  );

  const runAll = useCallback(async () => {
    setRunning(true);
    stop.current = false;
    for (const t of pending) {
      if (stop.current) break;
      await runOne(t);
    }
    setRunning(false);
  }, [pending, runOne]);

  if (!data) return <div className="p-8 text-white/70">جارٍ تحميل قائمة الصور…</div>;

  const total = data.tasks.length;
  const finished = Object.keys(done).length;

  return (
    <div className="mx-auto max-w-5xl px-5 pb-24 pt-10 text-white">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold">رفع الأرشيف الفلكي إلى Google Drive</h1>
        <p className="mt-2 text-sm text-white/60">
          {finished} / {total} ملفاً مرفوعاً — كل صورة تُرفع ببايتاتها الأصلية داخل مجلدها الموضوعي.
        </p>
        <div className="mt-3 h-2 w-full overflow-hidden rounded bg-white/10">
          <div className="h-full bg-emerald-400 transition-all" style={{ width: `${(finished / total) * 100}%` }} />
        </div>
      </header>

      <div className="mb-5 flex flex-wrap items-center gap-2">
        <button
          onClick={runAll}
          disabled={running || pending.length === 0}
          className="rounded bg-emerald-500 px-4 py-2 text-sm font-medium text-black disabled:opacity-40"
        >
          {running ? "جارٍ الرفع…" : `ارفع المتبقي (${pending.length})`}
        </button>
        <button
          onClick={() => {
            stop.current = true;
            setRunning(false);
          }}
          disabled={!running}
          className="rounded border border-white/20 px-4 py-2 text-sm disabled:opacity-40"
        >
          إيقاف
        </button>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="rounded border border-white/20 bg-black/40 px-3 py-2 text-sm"
        >
          <option value="all">كل المجلدات</option>
          {data.folders.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name}
            </option>
          ))}
        </select>
        <span className="text-xs text-white/50">{mb(pending.reduce((a, t) => a + t.bytes, 0))} متبقية</span>
      </div>

      <ul className="divide-y divide-white/10 overflow-hidden rounded-lg border border-white/10">
        {data.tasks
          .filter((t) => filter === "all" || t.folder === filter)
          .map((t) => (
            <li key={t.id} className="flex items-center gap-3 bg-white/[0.03] px-4 py-3">
              <span
                className={`h-2.5 w-2.5 flex-none rounded-full ${
                  done[t.id] ? "bg-emerald-400" : busy === t.id ? "animate-pulse bg-amber-300" : "bg-white/25"
                }`}
              />
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm">{t.name}</div>
                <div className="truncate text-xs text-white/45">{t.science.slice(0, 110)}…</div>
              </div>
              <span className="flex-none text-xs text-white/40">{mb(t.bytes)}</span>
              <button
                onClick={() => copyCaption(t)}
                className="flex-none rounded border border-white/20 px-3 py-1 text-xs"
              >
                انسخ التعليق
              </button>
              <button
                onClick={() => runOne(t)}
                disabled={!!busy || done[t.id]}
                className="flex-none rounded border border-white/20 px-3 py-1 text-xs disabled:opacity-30"
              >
                {done[t.id] ? "تم" : "ارفع"}
              </button>
            </li>
          ))}
      </ul>

      {log.length > 0 && (
        <pre className="mt-6 max-h-64 overflow-auto rounded bg-black/60 p-3 text-[11px] leading-5 text-white/70">
          {log.join("\n")}
        </pre>
      )}
    </div>
  );
}
