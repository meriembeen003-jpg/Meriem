import { NextResponse, NextRequest } from "next/server";
import { readFile, writeFile } from "fs/promises";
import path from "path";

export const runtime = "nodejs";

const STATE = path.join(process.cwd(), "archive", "state.json");

type State = { results: Record<string, { id: string; link: string | null; bytes: number; name: string }> };

async function read(): Promise<State> {
  try {
    return JSON.parse(await readFile(STATE, "utf8")) as State;
  } catch {
    return { results: {} };
  }
}

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);
  if (!body?.id || !body?.fileId) {
    return NextResponse.json({ ok: false }, { status: 400 });
  }
  const state = await read();
  state.results[body.id] = {
    id: body.fileId,
    link: body.link ?? null,
    bytes: body.bytes ?? 0,
    name: body.name ?? "",
  };
  await writeFile(STATE, JSON.stringify(state, null, 1), "utf8");
  return NextResponse.json({ ok: true, done: Object.keys(state.results).length });
}

export async function GET() {
  return NextResponse.json(await read());
}
