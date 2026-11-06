import { NextResponse } from "next/server";
import { getDb, saveDb } from "@/lib/server/db";
import { analyzeMediaAndTextForensics } from "@/lib/server/ai-engine";
import { MediaForensicRequest } from "@/lib/types/geointel";

export const dynamic = "force-dynamic";

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as MediaForensicRequest;
    if (!body?.claimText || body.claimText.trim().length < 4) {
      return NextResponse.json(
        {
          ok: false,
          error: "يرجى إدخال نص الخبر أو الادعاء أو وصف الفيديو المراد التحقق منه.",
        },
        { status: 400 }
      );
    }

    const db = getDb();
    const result = await analyzeMediaAndTextForensics(
      body,
      db.rootSources,
      db.dispatches,
      db.settings
    );

    db.forensicHistory = [result, ...db.forensicHistory].slice(0, 25);
    saveDb(db);

    return NextResponse.json({
      ok: true,
      result,
    });
  } catch (err) {
    return NextResponse.json(
      { ok: false, error: String(err) },
      { status: 500 }
    );
  }
}
