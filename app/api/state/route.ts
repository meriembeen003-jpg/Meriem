import { NextResponse } from "next/server";
import { getDb, getSanitizedSettings } from "@/lib/server/db";
import { getSentinelTelemetry } from "@/lib/server/sentinel-engine";
import { WAR_THEATERS } from "@/lib/data/war-theaters";

export const dynamic = "force-dynamic";

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}

export async function GET() {
  const db = getDb();
  const telemetry = getSentinelTelemetry();

  return NextResponse.json({
    ok: true,
    telemetry,
    theaters: WAR_THEATERS,
    dispatches: db.dispatches,
    rootSources: db.rootSources,
    rejectedNoise: db.rejectedNoise,
    forensicHistory: db.forensicHistory.slice(0, 15),
    settings: getSanitizedSettings(db.settings),
  });
}
