import { NextResponse, NextRequest } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

export const runtime = "nodejs";

const TASKS = path.join(process.cwd(), "archive", "tasks.json");

export async function GET(req: NextRequest) {
  const id = req.nextUrl.searchParams.get("id");
  try {
    const data = JSON.parse(await readFile(TASKS, "utf8")) as {
      tasks: { id: string; name: string; caption: string }[];
    };
    const task = data.tasks.find((t) => t.id === id);
    if (!task) return NextResponse.json({ ok: false, error: "unknown id" }, { status: 404 });
    return NextResponse.json({ ok: true, name: task.name, caption: task.caption });
  } catch (err) {
    return NextResponse.json({ ok: false, error: String(err) }, { status: 500 });
  }
}
