import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

export const runtime = "nodejs";

const ROOT = process.cwd();
const TASKS = path.join(ROOT, "archive", "tasks.json");
const STATE = path.join(ROOT, "archive", "state.json");

async function readJson<T>(p: string, fallback: T): Promise<T> {
  try {
    return JSON.parse(await readFile(p, "utf8")) as T;
  } catch {
    return fallback;
  }
}

export async function GET() {
  const tasks = await readJson<{ root: string; folders: unknown[]; tasks: unknown[] }>(TASKS, {
    root: "",
    folders: [],
    tasks: [],
  });
  const state = await readJson<{ results: Record<string, { id: string; link: string | null; bytes: number }> }>(
    STATE,
    { results: {} },
  );
  return NextResponse.json({ ...tasks, results: state.results ?? {} });
}
