import { NextResponse } from "next/server";
import { getDb, getSanitizedSettings, saveDb } from "@/lib/server/db";

export const dynamic = "force-dynamic";

export async function OPTIONS() {
  return new NextResponse(null, { status: 204 });
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const db = getDb();

    if (body.aiProvider) {
      db.settings.aiProvider = body.aiProvider;
    }
    if (
      typeof body.geminiApiKey === "string" &&
      !body.geminiApiKey.startsWith("••••")
    ) {
      db.settings.geminiApiKey = body.geminiApiKey.trim();
    }
    if (
      typeof body.openaiApiKey === "string" &&
      !body.openaiApiKey.startsWith("••••")
    ) {
      db.settings.openaiApiKey = body.openaiApiKey.trim();
    }
    if (
      typeof body.anthropicApiKey === "string" &&
      !body.anthropicApiKey.startsWith("••••")
    ) {
      db.settings.anthropicApiKey = body.anthropicApiKey.trim();
    }
    if (typeof body.fcmServerKeyOrWebhook === "string") {
      db.settings.fcmServerKeyOrWebhook = body.fcmServerKeyOrWebhook.trim();
    }
    if (typeof body.cloudServerPublicUrl === "string") {
      db.settings.cloudServerPublicUrl = body.cloudServerPublicUrl.trim();
    }
    if (typeof body.scanIntervalSeconds === "number") {
      db.settings.scanIntervalSeconds = Math.max(
        15,
        Math.min(600, body.scanIntervalSeconds)
      );
    }
    if (typeof body.minAccuracyForPush === "number") {
      db.settings.minAccuracyForPush = Math.max(
        50,
        Math.min(99, body.minAccuracyForPush)
      );
    }
    if (Array.isArray(body.notifySeverities)) {
      db.settings.notifySeverities = body.notifySeverities;
    }
    if (Array.isArray(body.watchedTheaters)) {
      db.settings.watchedTheaters = body.watchedTheaters;
    }
    if (typeof body.soundAlertsEnabled === "boolean") {
      db.settings.soundAlertsEnabled = body.soundAlertsEnabled;
    }

    saveDb(db);

    return NextResponse.json({
      ok: true,
      settings: getSanitizedSettings(db.settings),
    });
  } catch (err) {
    return NextResponse.json(
      { ok: false, error: String(err) },
      { status: 500 }
    );
  }
}
