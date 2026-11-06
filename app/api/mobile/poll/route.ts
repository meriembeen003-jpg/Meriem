import { NextResponse } from "next/server";
import { getDb } from "@/lib/server/db";
import { getSentinelTelemetry } from "@/lib/server/sentinel-engine";

export const dynamic = "force-dynamic";

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}

/**
 * Lightweight polling endpoint used by the native Android Foreground Service
 * (SentinelForegroundService.java) to deliver instant Arabic heads-up alerts
 * with minimal battery and mobile data usage (< 2 KB payload when idle).
 */
export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const since = searchParams.get("since");
  const db = getDb();
  const telemetry = getSentinelTelemetry();

  const sinceMs = since ? new Date(since).getTime() : Date.now() - 60_000;

  const alerts = db.dispatches
    .filter((d) => {
      const capturedMs = new Date(d.capturedAtUtc).getTime();
      const passesAccuracy =
        d.accuracy.overallScore >= db.settings.minAccuracyForPush;
      const passesSeverity = db.settings.notifySeverities.includes(d.severity);
      return capturedMs > sinceMs && passesAccuracy && passesSeverity;
    })
    .slice(0, 5)
    .map((d) => ({
      id: d.id,
      severity: d.severity,
      accuracyScore: d.accuracy.overallScore,
      titleAr: `راصد | ${d.locationAr} (${d.accuracy.overallScore}% دقة)`,
      bodyAr: d.headlineAr,
      rootSourceAr: d.rootSourceNameAr,
      capturedAtUtc: d.capturedAtUtc,
    }));

  return NextResponse.json({
    ok: true,
    serverTimeUtc: new Date().toISOString(),
    status: telemetry.status,
    alerts,
  });
}
