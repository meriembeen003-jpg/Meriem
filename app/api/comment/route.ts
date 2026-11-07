import { NextResponse, NextRequest } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

/**
 * Posts the archive's scientific caption for a task as a Google Drive comment on
 * the uploaded file, using the connector relay.
 */
export const runtime = "nodejs";
export const maxDuration = 120;

const ROOT = process.cwd();
const TASKS = path.join(ROOT, "archive", "tasks.json");
const RELAY = process.env.DRIVE_COMMENT_RELAY_URL ?? "https://api.arena.ai/v1/tools/google_drive/create_comment";

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  if (!body?.id || !body?.fileId) {
    return NextResponse.json({ ok: false, error: "id and fileId required" }, { status: 400 });
  }
  const data = JSON.parse(await readFile(TASKS, "utf8")) as { tasks: { id: string; caption: string }[] };
  const task = data.tasks.find((t) => t.id === body.id);
  if (!task) return NextResponse.json({ ok: false, error: "unknown task" }, { status: 404 });

  let status = 0;
  let json: { error?: unknown; comment?: { id?: string } } = {};
  try {
    const res = await fetch(RELAY, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        ...(process.env.ARENA_TOKEN ? { authorization: `Bearer ${process.env.ARENA_TOKEN}` } : {}),
      },
      body: JSON.stringify({ input: { file_id: body.fileId, content: task.caption.slice(0, 4000) } }),
    });
    status = res.status;
    json = await res.json().catch(() => ({}));
    if (!res.ok || json?.error) {
      return NextResponse.json({ ok: false, status, detail: json }, { status: 502 });
    }
  } catch (err) {
    return NextResponse.json({ ok: false, error: err instanceof Error ? err.message : String(err) }, { status: 500 });
  }
  return NextResponse.json({ ok: true, commentId: json?.comment?.id ?? null });
}
