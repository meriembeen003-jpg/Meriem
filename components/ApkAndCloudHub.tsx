"use client";

import { useState } from "react";
import {
  CheckCircle2,
  Cloud,
  Cpu,
  Download,
  KeyRound,
  Save,
  Server,
  Smartphone,
  Terminal,
} from "lucide-react";
import { AiProviderChoice, CloudSentinelSettings } from "@/lib/types/geointel";
import {
  apiUrl,
  getSavedCloudServerUrl,
  isRunningInsideAndroidApk,
  setSavedCloudServerUrl,
} from "@/lib/client/native-bridge";

interface ApkAndCloudHubProps {
  settings: CloudSentinelSettings & {
    hasGeminiKey?: boolean;
    hasOpenaiKey?: boolean;
    hasAnthropicKey?: boolean;
  };
  onRefreshState: () => void;
}

export default function ApkAndCloudHub({
  settings,
  onRefreshState,
}: ApkAndCloudHubProps) {
  const [aiProvider, setAiProvider] = useState<AiProviderChoice>(
    settings.aiProvider || "auto"
  );
  const [geminiApiKey, setGeminiApiKey] = useState(
    settings.geminiApiKey || ""
  );
  const [openaiApiKey, setOpenaiApiKey] = useState(
    settings.openaiApiKey || ""
  );
  const [anthropicApiKey, setAnthropicApiKey] = useState(
    settings.anthropicApiKey || ""
  );
  const [fcmServerKeyOrWebhook, setFcmServerKeyOrWebhook] = useState(
    settings.fcmServerKeyOrWebhook || ""
  );
  const [cloudUrlInput, setCloudUrlInput] = useState(
    getSavedCloudServerUrl() || settings.cloudServerPublicUrl || ""
  );
  const [scanIntervalSeconds, setScanIntervalSeconds] = useState(
    settings.scanIntervalSeconds || 45
  );
  const [minAccuracyForPush, setMinAccuracyForPush] = useState(
    settings.minAccuracyForPush || 78
  );
  const [saving, setSaving] = useState(false);
  const [savedBanner, setSavedBanner] = useState("");

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedBanner("");
    try {
      if (cloudUrlInput) {
        setSavedCloudServerUrl(cloudUrlInput);
      }
      const res = await fetch(apiUrl("/api/settings"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          aiProvider,
          geminiApiKey,
          openaiApiKey,
          anthropicApiKey,
          fcmServerKeyOrWebhook,
          cloudServerPublicUrl: cloudUrlInput,
          scanIntervalSeconds,
          minAccuracyForPush,
        }),
      });
      const json = await res.json();
      if (res.ok && json.ok) {
        setSavedBanner(
          "تم حفظ إعدادات الخادم السحابي ومحرك الذكاء الاصطناعي وقواعد الإنذار بنجاح."
        );
        onRefreshState();
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-12">
      {/* Android APK Build & Native Architecture Column */}
      <div className="space-y-5 lg:col-span-6">
        <div className="rounded-2xl border border-emerald-500/35 bg-gradient-to-br from-[#0e1b2e] to-[#09111e] p-5 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-emerald-500/40 bg-emerald-500/15">
              <Smartphone className="h-6 w-6 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-base font-extrabold text-white">
                تطبيق أندرويد الأصيل (APK) • راصد الجيوسياسي
              </h2>
              <p className="font-mono text-xs text-emerald-300">
                Package ID: com.rased.geointel • Android 8.0+ (API 26–35)
              </p>
            </div>
          </div>

          <div className="mt-4 space-y-2.5 text-xs leading-6 text-slate-300">
            <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3.5">
              <div className="font-bold text-cyan-300">
                ✓ خدمة تأهب أمامية دائمة في نظام أندرويد (SentinelForegroundService.java)
              </div>
              <p className="mt-1 text-slate-400">
                يعمل التطبيق في خلفية الهاتف على مدار الساعة حتى عند قفل الشاشة، ويتصل بنقطة{" "}
                <code className="text-emerald-300">/api/mobile/poll</code>{" "}
                لإطلاق إشعارات عربية فورية عالية الأولوية مع اهتزاز تكتيكي وصافرة تنبيه عند وقوع حدث حرج مؤكد.
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3.5">
              <div className="font-bold text-emerald-300">
                ✓ إعادة التشغيل التلقائي عند إقلاع الهاتف (BootCompletedReceiver)
              </div>
              <p className="mt-1 text-slate-400">
                يعيد تفعيل الارتباط بالخادم السحابي فور إعادة تشغيل جهاز الأندرويد دون الحاجة لفتح التطبيق يدويًا.
              </p>
            </div>
          </div>

          {/* Step-by-step APK Download Instructions via GitHub Actions */}
          <div className="mt-5 rounded-xl border border-cyan-500/30 bg-cyan-500/10 p-4">
            <div className="flex items-center gap-2 text-sm font-bold text-cyan-200">
              <Download className="h-4 w-4 text-cyan-400" />
              <span>طريقة استخراج وتحميل ملف APK الجاهز للتثبيت:</span>
            </div>
            <ol className="mt-2.5 list-inside list-decimal space-y-1.5 text-xs leading-relaxed text-slate-200">
              <li>
                تم تجهيز مشروع Android الكامل في مجلد{" "}
                <code className="font-mono text-emerald-300">android/</code>{" "}
                وملف البناء السحابي التلقائي{" "}
                <code className="font-mono text-emerald-300">
                  .github/workflows/build-apk.yml
                </code>
                .
              </li>
              <li>
                عند رفع الفرع أو فتح تبويب <strong>Actions</strong> في مستودع GitHub الخاص بك، يعمل سير العمل{" "}
                <strong>Build Rased Android APK</strong> تلقائيًا على خوادم GitHub (JDK 21 + Android SDK 35).
              </li>
              <li>
                خلال دقائق يظهر ملف{" "}
                <code className="font-mono font-bold text-amber-300">
                  Rased-GeoIntel-APK.apk
                </code>{" "}
                في قسم <strong>Artifacts</strong> جاهزًا للتحميل المباشر والتثبيت على هاتفك الأندرويد.
              </li>
            </ol>

            {isRunningInsideAndroidApk() && (
              <div className="mt-3 rounded-lg border border-emerald-500/40 bg-emerald-500/20 px-3 py-2 text-xs font-bold text-emerald-200">
                أنت تشغّل الآن نسخة تطبيق أندرويد (APK) الأصيلة المتصلة بالخدمة الخلفية!
              </div>
            )}
          </div>
        </div>

        {/* 24/7 Cloud Server Deployment Card */}
        <div className="rounded-2xl border border-slate-800 bg-[#0b1220] p-5">
          <div className="flex items-center gap-2.5 text-sm font-bold text-white">
            <Server className="h-5 w-5 text-cyan-400" />
            <span>نشر الخادم السحابي الدائم (24/7 Cloud Sentinel)</span>
          </div>
          <p className="mt-1.5 text-xs leading-relaxed text-slate-400">
            تم تضمين ملفات <code className="text-cyan-300">Dockerfile</code> و{" "}
            <code className="text-cyan-300">docker-compose.yml</code> و{" "}
            <code className="text-cyan-300">render.yaml</code> و{" "}
            <code className="text-cyan-300">railway.json</code> ليعمل الخادم بلا توقف ويرصد خلاصات رويترز وAP وUKMTO وIAEA والأمم المتحدة على مدار الساعة:
          </p>
          <div
            dir="ltr"
            className="mt-3 rounded-xl border border-slate-800 bg-slate-950 p-3 font-mono text-[11px] leading-relaxed text-emerald-300"
          >
            <div className="flex items-center gap-1.5 text-slate-400">
              <Terminal className="h-3.5 w-3.5" />
              <span># تشغيل الخادم السحابي الدائم عبر Docker</span>
            </div>
            <div className="mt-1">docker compose up -d --build</div>
            <div className="mt-1 text-cyan-300">
              # أو البناء المحلي لملف APK عند توفر Android SDK
            </div>
            <div>npm run build:apk</div>
          </div>
        </div>
      </div>

      {/* Cloud AI & Push Alert Settings Form */}
      <form
        onSubmit={handleSaveSettings}
        className="space-y-4 rounded-2xl border border-slate-800 bg-[#0b1220] p-5 lg:col-span-6"
      >
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
          <Cloud className="h-5 w-5 text-emerald-400" />
          <div>
            <h2 className="text-base font-bold text-white">
              إعدادات الخادم السحابي والذكاء الاصطناعي والإشعارات الفورية
            </h2>
            <p className="text-xs text-slate-400">
              يعمل المحرك المحلي المدمج فورًا بدون مفاتيح، ويمكنك ربط Gemini أو GPT-4o أو Claude لتعزيز تحليل الفيديو
            </p>
          </div>
        </div>

        {/* Cloud Server URL for Android APK */}
        <div>
          <label className="mb-1 block text-xs font-bold text-slate-200">
            رابط الخادم السحابي الدائم (لربط تطبيق APK بالخادم):
          </label>
          <input
            type="url"
            dir="ltr"
            value={cloudUrlInput}
            onChange={(e) => setCloudUrlInput(e.target.value)}
            placeholder="https://rased-sentinel.up.railway.app"
            className="w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-100 focus:border-cyan-500 focus:outline-none"
          />
        </div>

        {/* AI Provider Choice */}
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <label className="mb-1 flex items-center gap-1 text-xs font-bold text-slate-200">
              <Cpu className="h-3.5 w-3.5 text-cyan-400" />
              <span>مزود الذكاء الاصطناعي للصياغة والفيديو:</span>
            </label>
            <select
              value={aiProvider}
              onChange={(e) =>
                setAiProvider(e.target.value as AiProviderChoice)
              }
              className="w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-100 focus:border-cyan-500 focus:outline-none"
            >
              <option value="auto">تلقائي ذكي (يستخدم المفتاح المتوفر + المحرك المدمج)</option>
              <option value="gemini">Google Gemini 2.0/2.5 Flash (موصى به للفيديو)</option>
              <option value="openai">OpenAI GPT-4o Vision</option>
              <option value="anthropic">Anthropic Claude Sonnet</option>
              <option value="local">المحرك الجيوسياسي المدمج فقط (بدون API خارجي)</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-xs font-bold text-slate-200">
              دورة فحص المصادر الأم (بالثواني):
            </label>
            <input
              type="number"
              min={15}
              max={600}
              value={scanIntervalSeconds}
              onChange={(e) => setScanIntervalSeconds(Number(e.target.value))}
              className="w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-100 focus:border-cyan-500 focus:outline-none"
            />
          </div>
        </div>

        {/* API Keys */}
        <div className="space-y-2.5 rounded-xl border border-slate-800/90 bg-slate-950/60 p-3.5">
          <div className="flex items-center gap-1.5 text-xs font-bold text-amber-300">
            <KeyRound className="h-3.5 w-3.5" />
            <span>مفاتيح الذكاء الاصطناعي الاختيارية (تُحفظ مشفرة على الخادم فقط):</span>
          </div>

          <input
            type="password"
            dir="ltr"
            value={geminiApiKey}
            onChange={(e) => setGeminiApiKey(e.target.value)}
            placeholder="GEMINI_API_KEY (AIzaSy...)"
            className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
          />
          <input
            type="password"
            dir="ltr"
            value={openaiApiKey}
            onChange={(e) => setOpenaiApiKey(e.target.value)}
            placeholder="OPENAI_API_KEY (sk-...)"
            className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
          />
          <input
            type="password"
            dir="ltr"
            value={anthropicApiKey}
            onChange={(e) => setAnthropicApiKey(e.target.value)}
            placeholder="ANTHROPIC_API_KEY (sk-ant-...)"
            className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
          />
        </div>

        {/* Push Webhook / FCM & Minimum Accuracy Slider */}
        <div className="space-y-3">
          <div>
            <label className="mb-1 block text-xs font-bold text-slate-200">
              مفتاح Firebase FCM أو رابط إشعارات فورية (ntfy.sh / Webhook):
            </label>
            <input
              type="text"
              dir="ltr"
              value={fcmServerKeyOrWebhook}
              onChange={(e) => setFcmServerKeyOrWebhook(e.target.value)}
              placeholder="https://ntfy.sh/rased-private-war-alerts أو مفتاح FCM"
              className="w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold text-slate-200">
              <span>الحد الأدنى لمؤشر الدقة لإرسال إشعار فوري للهاتف:</span>
              <span className="font-mono text-emerald-400">
                {minAccuracyForPush}%
              </span>
            </div>
            <input
              type="range"
              min={50}
              max={95}
              value={minAccuracyForPush}
              onChange={(e) => setMinAccuracyForPush(Number(e.target.value))}
              className="mt-1.5 w-full accent-emerald-500"
            />
            <p className="text-[11px] text-slate-400">
              أي خبر تقل دقته عن {minAccuracyForPush}% يوضع تحت التدقيق ولا يزعجك بإشعار عاجل حتى يتأكد من مصدر أم.
            </p>
          </div>
        </div>

        {savedBanner && (
          <div className="flex items-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/15 p-3 text-xs text-emerald-200">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
            <span>{savedBanner}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={saving}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-l from-emerald-500 to-cyan-600 py-3 text-sm font-extrabold text-slate-950 shadow-lg transition hover:opacity-95 disabled:opacity-50"
        >
          <Save className="h-4 w-4" />
          <span>{saving ? "جاري الحفظ..." : "حفظ إعدادات التأهب السحابي"}</span>
        </button>
      </form>
    </div>
  );
}
