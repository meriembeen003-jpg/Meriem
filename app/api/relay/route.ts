import { NextResponse, NextRequest } from "next/server";
import { readFile, stat } from "fs/promises";
import path from "path";

/**
 * Relays one staged archive file to Google Drive.
 *
 *   POST /api/relay
 *   x-file-path: archive/upload/07_smacs.png   (relative to the repo root)
 *   x-file-name: 07_smacs.png
 *   x-file-mime: image/png
 *   x-parent-id: <Drive folder id>
 *
 * The upload is performed by the connector relay, so the bytes never need to
 * leave this machine except through the authorised tool endpoint.
 */
export const runtime = "nodejs";
export const maxDuration = 300;

const ROOT = process.cwd();
const RELAY = process.env.DRIVE_RELAY_URL ?? "https://api.arena.ai/v1/tools/google_drive/upload_file";

export async function POST(req: NextRequest) {
  const rel = req.headers.get("x-file-path") ?? "";
  const name = req.headers.get("x-file-name") ?? path.basename(rel);
  const mime = req.headers.get("x-file-mime") ?? "application/octet-stream";
  const parent = req.headers.get("x-parent-id") ?? "";

  const abs = path.resolve(ROOT, rel);
  if (!abs.startsWith(ROOT + path.sep)) {
    return NextResponse.json({ ok: false, error: "path outside repository" }, { status: 400 });
  }
  const info = await stat(abs).catch(() => null);
  if (!info?.isFile()) {
    return NextResponse.json({ ok: false, error: `not found: ${rel}` }, { status: 404 });
  }
  const bytes = await readFile(abs);

  const form = new FormData();
  form.append("name", name);
  form.append("mime_type", mime);
  form.append("parents", JSON.stringify(parent ? [parent] : []));
  form.append("file", new Blob([new Uint8Array(bytes)], { type: mime }), name);

  try {
    const res = await fetch(RELAY, {
      method: "POST",
      headers: process.env.ARENA_TOKEN ? { authorization: `Bearer ${process.env.ARENA_TOKEN}` } : undefined,
      body: form,
    });
    const json = await res.json().catch(() => ({}));
    if (!res.ok || json?.error) {
      return NextResponse.json({ ok: false, stage: "relay", status: res.status, detail: json }, { status: 502 });
    }
    const file = json.file ?? json;
    return NextResponse.json({ ok: true, id: file?.id ?? null, link: file?.web_view_link ?? null, bytes: info.size });
  } catch (err) {
    return NextResponse.json(
      { ok: false, stage: "relay", error: err instanceof Error ? err.message : String(err) },
      { status: 500 },
    );
  }
}
