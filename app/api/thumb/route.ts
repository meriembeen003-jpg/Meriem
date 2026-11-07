import { NextResponse, NextRequest } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

export const runtime = "nodejs";

const ROOT = path.join(process.cwd(), "archive");

export async function GET(req: NextRequest) {
  const name = req.nextUrl.searchParams.get("name") ?? "";
  const abs = path.resolve(ROOT, name);
  if (!abs.startsWith(ROOT + path.sep) || !abs.endsWith(".jpg")) {
    return NextResponse.json({ error: "bad path" }, { status: 400 });
  }
  try {
    const buf = await readFile(abs);
    return new NextResponse(new Uint8Array(buf), {
      headers: { "content-type": "image/jpeg", "cache-control": "public, max-age=3600" },
    });
  } catch {
    return NextResponse.json({ error: "not found" }, { status: 404 });
  }
}
