"use client";

import { Capacitor, registerPlugin } from "@capacitor/core";
import { LocalNotifications } from "@capacitor/local-notifications";
import { Haptics, ImpactStyle } from "@capacitor/haptics";
import { AlertSeverity, GeopoliticalDispatch } from "@/lib/types/geointel";

interface SentinelNativePlugin {
  startForegroundVigilance(options: {
    serverUrl: string;
    pollSeconds?: number;
  }): Promise<{ started: boolean }>;
  stopForegroundVigilance(): Promise<{ stopped: boolean }>;
}

const SentinelNative = registerPlugin<SentinelNativePlugin>("SentinelNative");

export function isRunningInsideAndroidApk(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return Capacitor.isNativePlatform();
  } catch {
    return false;
  }
}

export function getSavedCloudServerUrl(): string {
  if (typeof window === "undefined") return "";
  return (localStorage.getItem("rased_cloud_server_url") || "").replace(/\/+$/, "");
}

export function setSavedCloudServerUrl(url: string): void {
  if (typeof window === "undefined") return;
  const clean = url.trim().replace(/\/+$/, "");
  localStorage.setItem("rased_cloud_server_url", clean);
  if (isRunningInsideAndroidApk() && clean) {
    void startAndroidForegroundSentinel(clean);
  }
}

export function apiUrl(path: string): string {
  if (isRunningInsideAndroidApk()) {
    const remote = getSavedCloudServerUrl();
    if (remote) {
      return `${remote}${path}`;
    }
  }
  // Always relative URL on web / live preview
  return path;
}

export async function requestAlertPermissions(): Promise<{
  granted: boolean;
  mode: "ANDROID_NATIVE" | "WEB_NOTIFICATION" | "UNSUPPORTED";
}> {
  if (typeof window === "undefined") {
    return { granted: false, mode: "UNSUPPORTED" };
  }

  if (isRunningInsideAndroidApk()) {
    try {
      const perm = await LocalNotifications.requestPermissions();
      const granted = perm.display === "granted";
      const cloudUrl = getSavedCloudServerUrl();
      if (granted && cloudUrl) {
        await startAndroidForegroundSentinel(cloudUrl);
      }
      return { granted, mode: "ANDROID_NATIVE" };
    } catch {
      return { granted: false, mode: "ANDROID_NATIVE" };
    }
  }

  if ("Notification" in window) {
    if (Notification.permission === "granted") {
      return { granted: true, mode: "WEB_NOTIFICATION" };
    }
    const res = await Notification.requestPermission();
    return { granted: res === "granted", mode: "WEB_NOTIFICATION" };
  }

  return { granted: false, mode: "UNSUPPORTED" };
}

export async function startAndroidForegroundSentinel(
  serverUrl: string
): Promise<boolean> {
  if (!isRunningInsideAndroidApk() || !serverUrl) return false;
  try {
    await SentinelNative.startForegroundVigilance({
      serverUrl,
      pollSeconds: 30,
    });
    return true;
  } catch (err) {
    console.warn("[RASED APK] Native foreground service note:", err);
    return false;
  }
}

export function playTacticalAlertTone(severity: AlertSeverity): void {
  if (typeof window === "undefined") return;
  try {
    const AudioCtx =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof AudioContext })
        .webkitAudioContext;
    if (!AudioCtx) return;

    const ctx = new AudioCtx();
    const now = ctx.currentTime;

    const pulses =
      severity === "CRITICAL"
        ? [
            { freq: 880, start: 0, dur: 0.14 },
            { freq: 1174.66, start: 0.18, dur: 0.14 },
            { freq: 880, start: 0.36, dur: 0.22 },
          ]
        : [
            { freq: 659.25, start: 0, dur: 0.12 },
            { freq: 880, start: 0.16, dur: 0.18 },
          ];

    for (const p of pulses) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = severity === "CRITICAL" ? "sawtooth" : "triangle";
      osc.frequency.setValueAtTime(p.freq, now + p.start);

      gain.gain.setValueAtTime(0.0001, now + p.start);
      gain.gain.exponentialRampToValueAtTime(0.14, now + p.start + 0.02);
      gain.gain.exponentialRampToValueAtTime(
        0.0001,
        now + p.start + p.dur
      );

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + p.start);
      osc.stop(now + p.start + p.dur + 0.02);
    }
  } catch {
    // Audio blocked prior to user gesture
  }
}

export async function fireInstantArabicNotification(
  dispatch: GeopoliticalDispatch,
  soundEnabled = true
): Promise<void> {
  if (soundEnabled) {
    playTacticalAlertTone(dispatch.severity);
  }

  const title = `🚨 راصد [${
    dispatch.severity === "CRITICAL" ? "إنذار حرج" : "تأهب عالي"
  }] — دقة ${dispatch.accuracy.overallScore}%`;
  const body = `${dispatch.headlineAr}\nالمصدر الأم: ${dispatch.rootSourceNameAr}`;

  if (isRunningInsideAndroidApk()) {
    try {
      await Haptics.impact({
        style:
          dispatch.severity === "CRITICAL"
            ? ImpactStyle.Heavy
            : ImpactStyle.Medium,
      });
      await LocalNotifications.schedule({
        notifications: [
          {
            id: Math.floor(Date.now() % 2147483000),
            title,
            body,
            schedule: { at: new Date(Date.now() + 200) },
            extra: { dispatchId: dispatch.id },
          },
        ],
      });
      return;
    } catch {
      // Fallback to web notification
    }
  }

  if (typeof window !== "undefined" && "Notification" in window) {
    if (Notification.permission === "granted") {
      try {
        new Notification(title, {
          body,
          dir: "rtl",
          lang: "ar",
          tag: dispatch.id,
        });
      } catch {
        // Ignore on restricted mobile browsers
      }
    }
  }
}
