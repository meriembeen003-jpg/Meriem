import { CloudSentinelSettings, GeopoliticalDispatch } from "@/lib/types/geointel";

export async function dispatchCloudPushAlert(
  dispatch: GeopoliticalDispatch,
  settings: CloudSentinelSettings
): Promise<{ deliveredExternal: boolean; channel: string }> {
  const endpoint = settings.fcmServerKeyOrWebhook?.trim();
  if (!endpoint) {
    return { deliveredExternal: false, channel: "SSE_AND_NATIVE_FOREGROUND" };
  }

  try {
    // Supports ntfy.sh, custom Webhook, or FCM proxy gateway
    if (endpoint.startsWith("http://") || endpoint.startsWith("https://")) {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Title: `راصد [${dispatch.severity}]: ${dispatch.rootSourceNameAr}`,
          Priority: dispatch.severity === "CRITICAL" ? "urgent" : "high",
        },
        body: JSON.stringify({
          type: "RASED_GEOINTEL_ALERT",
          id: dispatch.id,
          severity: dispatch.severity,
          accuracyScore: dispatch.accuracy.overallScore,
          headlineAr: dispatch.headlineAr,
          flashSummaryAr: dispatch.flashSummaryAr,
          rootSource: dispatch.rootSourceNameAr,
          rootUrl: dispatch.rootSourceUrl,
          theaterId: dispatch.theaterId,
          locationAr: dispatch.locationAr,
          capturedAtUtc: dispatch.capturedAtUtc,
        }),
        signal: AbortSignal.timeout(8000),
      });
      return {
        deliveredExternal: res.ok,
        channel: "CLOUD_WEBHOOK_PUSH",
      };
    }

    // Legacy/Server Key FCM Topic broadcast ("rased_alerts_ar")
    const fcmRes = await fetch("https://fcm.googleapis.com/fcm/send", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `key=${endpoint}`,
      },
      body: JSON.stringify({
        to: "/topics/rased_alerts_ar",
        priority: "high",
        notification: {
          title: `🚨 راصد | ${dispatch.locationAr} (${dispatch.accuracy.overallScore}% دقة)`,
          body: dispatch.headlineAr,
          sound: "default",
          android_channel_id: "rased_critical_war_alerts",
        },
        data: {
          dispatchId: dispatch.id,
          severity: dispatch.severity,
          theaterId: dispatch.theaterId,
          rootSourceDomain: dispatch.rootSourceDomain,
        },
      }),
      signal: AbortSignal.timeout(8000),
    });

    return {
      deliveredExternal: fcmRes.ok,
      channel: "FIREBASE_FCM_TOPIC",
    };
  } catch (err) {
    console.warn("[RASED PUSH] External push warning:", err);
    return { deliveredExternal: false, channel: "SSE_FALLBACK" };
  }
}
