"use client";

import { ExtractedVideoFrame } from "@/lib/types/geointel";

export interface ExtractedVideoBundle {
  fileName: string;
  fileSizeBytes: number;
  durationSec: number;
  width: number;
  height: number;
  mimeType: string;
  sha256: string;
  frames: ExtractedVideoFrame[];
}

async function computeFileSha256(file: File): Promise<string> {
  try {
    // Hash up to first 4MB for instant performance on mobile devices
    const slice = file.slice(0, 4 * 1024 * 1024);
    const buf = await slice.arrayBuffer();
    const digest = await crypto.subtle.digest("SHA-256", buf);
    return Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  } catch {
    return `sha256-fallback-${file.size}-${file.lastModified}`;
  }
}

function classifyPixelBuffer(
  rgba: Uint8ClampedArray
): Pick<ExtractedVideoFrame, "avgLuminance" | "contrastScore" | "dominantTone"> {
  let sumLum = 0;
  let sumLumSq = 0;
  let sumR = 0;
  let sumG = 0;
  let sumB = 0;
  const pixelCount = Math.max(1, rgba.length / 4);

  for (let i = 0; i < rgba.length; i += 4) {
    const r = rgba[i];
    const g = rgba[i + 1];
    const b = rgba[i + 2];
    const lum = 0.299 * r + 0.587 * g + 0.114 * b;
    sumLum += lum;
    sumLumSq += lum * lum;
    sumR += r;
    sumG += g;
    sumB += b;
  }

  const avgLum = sumLum / pixelCount;
  const variance = Math.max(0, sumLumSq / pixelCount - avgLum * avgLum);
  const contrast = Math.sqrt(variance);
  const avgR = sumR / pixelCount;
  const avgG = sumG / pixelCount;
  const avgB = sumB / pixelCount;

  let dominantTone: ExtractedVideoFrame["dominantTone"] = "DAYLIGHT";
  if (avgLum > 205 && contrast > 45) {
    dominantTone = "HIGH_FLASH";
  } else if (avgG > avgR * 1.45 && avgG > avgB * 1.45) {
    dominantTone = "NIGHT_VISION_GREEN";
  } else if (
    Math.abs(avgR - avgG) < 7 &&
    Math.abs(avgG - avgB) < 7 &&
    contrast > 38
  ) {
    dominantTone = "THERMAL_MONO";
  } else if (avgLum < 58) {
    dominantTone = "NIGHT_DARK";
  }

  return {
    avgLuminance: Math.round(avgLum),
    contrastScore: Math.round(contrast),
    dominantTone,
  };
}

export async function extractVideoForensicsFromFile(
  file: File
): Promise<ExtractedVideoBundle> {
  const sha256 = await computeFileSha256(file);
  const objectUrl = URL.createObjectURL(file);

  try {
    const video = document.createElement("video");
    video.preload = "metadata";
    video.muted = true;
    video.playsInline = true;
    video.src = objectUrl;

    await new Promise<void>((resolve, reject) => {
      const timeout = setTimeout(
        () => reject(new Error("انتهت مهلة قراءة بيانات الفيديو")),
        10000
      );
      video.onloadedmetadata = () => {
        clearTimeout(timeout);
        resolve();
      };
      video.onerror = () => {
        clearTimeout(timeout);
        reject(new Error("تعذر فك ترميز ملف الفيديو المختار"));
      };
    });

    const durationSec = Number.isFinite(video.duration) && video.duration > 0
      ? video.duration
      : 4;
    const width = video.videoWidth || 1280;
    const height = video.videoHeight || 720;

    const targetWidth = Math.min(480, width);
    const targetHeight = Math.max(
      180,
      Math.round((height / Math.max(1, width)) * targetWidth)
    );

    const canvas = document.createElement("canvas");
    canvas.width = targetWidth;
    canvas.height = targetHeight;
    const ctx = canvas.getContext("2d");

    const fractions = [0.12, 0.38, 0.64, 0.88];
    const frames: ExtractedVideoFrame[] = [];

    if (ctx) {
      for (const frac of fractions) {
        const t = Math.min(Math.max(0.05, durationSec * frac), durationSec - 0.05);
        await new Promise<void>((resolve) => {
          const done = () => resolve();
          video.onseeked = done;
          video.currentTime = Math.max(0, t);
          setTimeout(done, 1200);
        });

        ctx.drawImage(video, 0, 0, targetWidth, targetHeight);
        const imgData = ctx.getImageData(0, 0, targetWidth, targetHeight);
        const stats = classifyPixelBuffer(imgData.data);
        frames.push({
          timestampSec: Number(t.toFixed(2)),
          dataUrl: canvas.toDataURL("image/jpeg", 0.72),
          ...stats,
        });
      }
    }

    return {
      fileName: file.name,
      fileSizeBytes: file.size,
      durationSec,
      width,
      height,
      mimeType: file.type || "video/mp4",
      sha256,
      frames,
    };
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}

/**
 * Generates a realistic 4-frame FLIR/NVG maritime radar sample bundle so the user
 * can test the Multimodal Video Forensics Lab with 1 click even without local MP4 files.
 */
export function buildSampleTacticalVideoBundle(): ExtractedVideoBundle {
  const canvas = document.createElement("canvas");
  canvas.width = 420;
  canvas.height = 236;
  const ctx = canvas.getContext("2d")!;

  const stamps = [1.4, 4.8, 8.2, 11.6];
  const frames: ExtractedVideoFrame[] = stamps.map((sec, idx) => {
    // Night-vision / maritime thermal simulation frame
    ctx.fillStyle = idx === 2 ? "#1e3a29" : "#071a12";
    ctx.fillRect(0, 0, 420, 236);

    // Horizon line
    ctx.strokeStyle = "rgba(52, 211, 153, 0.45)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, 138);
    ctx.lineTo(420, 138);
    ctx.stroke();

    // Simulated vessel silhouette + flash on frame 3
    ctx.fillStyle = "rgba(110, 231, 183, 0.75)";
    ctx.fillRect(175 + idx * 8, 126, 48, 12);
    if (idx === 2) {
      const grad = ctx.createRadialGradient(210, 122, 2, 210, 122, 46);
      grad.addColorStop(0, "rgba(255, 255, 220, 0.95)");
      grad.addColorStop(0.5, "rgba(52, 211, 153, 0.55)");
      grad.addColorStop(1, "rgba(7, 26, 18, 0)");
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(210, 122, 46, 0, Math.PI * 2);
      ctx.fill();
    }

    // Tactical HUD crosshairs
    ctx.strokeStyle = "rgba(16, 185, 129, 0.7)";
    ctx.strokeRect(145, 88, 130, 74);
    ctx.font = "11px monospace";
    ctx.fillStyle = "#6ee7b7";
    ctx.fillText(`NVG-CAM 04 | T+${sec.toFixed(1)}s | 14°12'N 42°10'E`, 14, 22);

    const imgData = ctx.getImageData(0, 0, 420, 236);
    const stats = classifyPixelBuffer(imgData.data);

    return {
      timestampSec: sec,
      dataUrl: canvas.toDataURL("image/jpeg", 0.8),
      ...stats,
      dominantTone: idx === 2 ? "HIGH_FLASH" : "NIGHT_VISION_GREEN",
    };
  });

  return {
    fileName: "red_sea_night_optical_clip_sample.mp4",
    fileSizeBytes: 3_842_110,
    durationSec: 13.2,
    width: 1280,
    height: 720,
    mimeType: "video/mp4",
    sha256: "9f84c2e17b09d4a6531c880e4471a2b9f05d61c3e8a712b490c11d85e3a47f10",
    frames,
  };
}
