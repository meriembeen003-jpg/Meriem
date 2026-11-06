import { NextResponse } from "next/server";
import { runRootSourcesScan } from "@/lib/server/sentinel-engine";

export const dynamic = "force-dynamic";

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}

export async function POST(req: Request) {
  try {
    const body = await req.json().catch(() => ({}));
    const includeDrill = Boolean(body?.drill);
    const result = await runRootSourcesScan(includeDrill);
    return NextResponse.json({
      ok: true,
      ...result,
    });
  } catch (err) {
    return NextResponse.json(
      { ok: false, error: String(err) },
      { status: 500 }
    );
  }
}
