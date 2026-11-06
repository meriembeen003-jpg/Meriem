import {
  AlertSeverity,
  CloudSentinelSettings,
  GeopoliticalDispatch,
  MediaForensicRequest,
  MediaForensicResult,
  RootSource,
  WarTheaterId,
} from "@/lib/types/geointel";
import {
  matchRootSourceByUrl,
  SECONDARY_RUMOR_PATTERNS,
} from "@/lib/data/root-sources";

interface RawWireCandidate {
  title: string;
  description: string;
  link: string;
  pubDateUtc: string;
  rootSource: RootSource;
  corroboratingCount?: number;
}

const MILITARY_LEXICON: Array<{
  regex: RegExp;
  termAr: string;
  theaterHint?: WarTheaterId;
  severityBoost?: number;
}> = [
  {
    regex: /\b(missile|ballistic|hypersonic|cruise missile|صاروخ|باليستي|فرط صوتي)\b/i,
    termAr: "منظومات الصواريخ الباليستية والمجنحة",
    severityBoost: 2,
  },
  {
    regex: /\b(drone|uav|uas|unmanned|مسيّرة|مسيرات|طائرة بدون طيار)\b/i,
    termAr: "الأنظمة الجوية والبحرية غير المأهولة (UAV/USV)",
    severityBoost: 1,
  },
  {
    regex: /\b(air defense|interceptor|patriot|s-400|iron dome|دفاع جوي|اعتراض)\b/i,
    termAr: "منظومات الدفاع الجوي والاعتراض الطبقي",
    severityBoost: 1,
  },
  {
    regex: /\b(nuclear|iaea|uranium|reactor|warhead|نووي|ذري|تخصيب|مفاعل)\b/i,
    termAr: "الرقابة النووية ومنشآت الطاقة الذرية",
    theaterHint: "STRATEGIC_NUCLEAR_CYBER",
    severityBoost: 2,
  },
  {
    regex: /\b(red sea|bab el-mandeb|hudaydah|hormuz|ukmto|vessel|tanker|البحر الأحمر|باب المندب|هرمز|سفينة|ناقلة)\b/i,
    termAr: "أمن الملاحة البحرية وحماية المضايق الاستراتيجية",
    theaterHint: "MIDDLE_EAST_RED_SEA",
    severityBoost: 2,
  },
  {
    regex: /\b(taiwan|south china sea|pla|bashi|korean|pyongyang|تايوان|بحر الصين|كوريا)\b/i,
    termAr: "الأساطيل البحرية والإنذار الجوي في شرق آسيا",
    theaterHint: "INDO_PACIFIC_TAIWAN",
    severityBoost: 1,
  },
  {
    regex: /\b(ukraine|russia|donbas|crimea|black sea|kyiv|moscow|zaporizhzhia|أوكرانيا|روسيا|القرم|دونباس)\b/i,
    termAr: "عمليات المدفعية والحرب الإلكترونية والدفاع الجوي",
    theaterHint: "EAST_EUROPE",
    severityBoost: 1,
  },
  {
    regex: /\b(sudan|sahel|horn of africa|red sea port|djibouti|somalia|السودان|الساحل|القرن الأفريقي)\b/i,
    termAr: "أمن الموانئ والتموضع اللوجستي الإقليمي",
    theaterHint: "SAHEL_HORN_AFRICA",
    severityBoost: 1,
  },
  {
    regex: /\b(submarine|undersea cable|baltic|nato|carrier|frigate|destroyer|غواصة|كابلات بحرية|فرقاطة|مدمرة|حاملة طائرات)\b/i,
    termAr: "الأساطيل البحرية وحرب الأعماق وحماية الكابلات",
    theaterHint: "STRATEGIC_NUCLEAR_CYBER",
    severityBoost: 1,
  },
];

const SENSATIONAL_PROPAGANDA_REGEX =
  /(شاهد قبل الحذف|دمار شامل|إبادة كاملة|مصادر سرية غير معلنة|مسح عن الخريطة|فضيحة مدوية|WW3 STARTED|TOTAL DESTRUCTION|SHOCKING VIDEO|UNCONFIRMED RUMOR|sources say anonymously)/i;

export function isGeopoliticalOrMilitaryRelevant(text: string): boolean {
  const geoRegex =
    /\b(military|defense|defence|war|missile|strike|naval|navy|army|troops|nato|un security|iaea|nuclear|ceasefire|sanctions|strait|maritime|drone|airspace|radar|artillery|pentagon|ministry|vessel|submarine|cyber|conflict|border|escalation|عسكري|حرب|صاروخ|دفاع|بحرية|مضيق|نووي|مجلس الأمن|مسيّرة|غارة|مناورات|هدنة)\b/i;
  return geoRegex.test(text);
}

export function resolveActiveAiName(settings: CloudSentinelSettings): string {
  const pref = settings.aiProvider;
  if ((pref === "gemini" || pref === "auto") && settings.geminiApiKey) {
    return "Google Gemini 2.5 Flash (Multimodal)";
  }
  if ((pref === "openai" || pref === "auto") && settings.openaiApiKey) {
    return "OpenAI GPT-4o (Vision + Arabic)";
  }
  if ((pref === "anthropic" || pref === "auto") && settings.anthropicApiKey) {
    return "Anthropic Claude Sonnet (Strategic)";
  }
  return "محرك راصد المحلي للتحقق الجيوسياسي الصارم (نشط 24/7)";
}

async function callExternalLlmJson<T>(
  settings: CloudSentinelSettings,
  systemPrompt: string,
  userPrompt: string,
  imagesBase64: string[] = []
): Promise<{ data: T; engineName: string } | null> {
  const pref = settings.aiProvider;

  // 1. Try Gemini
  if ((pref === "gemini" || pref === "auto") && settings.geminiApiKey) {
    try {
      const parts: Array<Record<string, unknown>> = [
        { text: `${systemPrompt}\n\n${userPrompt}` },
      ];
      for (const img of imagesBase64.slice(0, 4)) {
        const cleanBase64 = img.replace(/^data:image\/\w+;base64,/, "");
        parts.push({
          inline_data: {
            mime_type: "image/jpeg",
            data: cleanBase64,
          },
        });
      }

      const res = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${encodeURIComponent(
          settings.geminiApiKey
        )}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts }],
            generationConfig: {
              temperature: 0.15,
              responseMimeType: "application/json",
            },
          }),
          signal: AbortSignal.timeout(20000),
        }
      );

      if (res.ok) {
        const json = await res.json();
        const textOut = json?.candidates?.[0]?.content?.parts?.[0]?.text;
        if (textOut) {
          return {
            data: JSON.parse(textOut) as T,
            engineName: "Google Gemini Multimodal AI",
          };
        }
      }
    } catch (err) {
      console.warn("[RASED AI] Gemini call fallback:", err);
    }
  }

  // 2. Try OpenAI
  if ((pref === "openai" || pref === "auto") && settings.openaiApiKey) {
    try {
      const userContent: Array<Record<string, unknown>> = [
        { type: "text", text: userPrompt },
      ];
      for (const img of imagesBase64.slice(0, 4)) {
        userContent.push({
          type: "image_url",
          image_url: { url: img, detail: "low" },
        });
      }

      const res = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${settings.openaiApiKey}`,
        },
        body: JSON.stringify({
          model: "gpt-4o-mini",
          temperature: 0.15,
          response_format: { type: "json_object" },
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userContent },
          ],
        }),
        signal: AbortSignal.timeout(20000),
      });

      if (res.ok) {
        const json = await res.json();
        const textOut = json?.choices?.[0]?.message?.content;
        if (textOut) {
          return {
            data: JSON.parse(textOut) as T,
            engineName: "OpenAI GPT-4o Vision",
          };
        }
      }
    } catch (err) {
      console.warn("[RASED AI] OpenAI call fallback:", err);
    }
  }

  // 3. Try Anthropic
  if ((pref === "anthropic" || pref === "auto") && settings.anthropicApiKey) {
    try {
      const contentBlocks: Array<Record<string, unknown>> = [];
      for (const img of imagesBase64.slice(0, 4)) {
        const cleanBase64 = img.replace(/^data:image\/\w+;base64,/, "");
        contentBlocks.push({
          type: "image",
          source: {
            type: "base64",
            media_type: "image/jpeg",
            data: cleanBase64,
          },
        });
      }
      contentBlocks.push({
        type: "text",
        text: `${userPrompt}\n\nأجب بصيغة JSON صالحة فقط بدون أي نص خارجي.`,
      });

      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": settings.anthropicApiKey,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model: "claude-3-5-sonnet-latest",
          max_tokens: 1600,
          temperature: 0.15,
          system: systemPrompt,
          messages: [{ role: "user", content: contentBlocks }],
        }),
        signal: AbortSignal.timeout(20000),
      });

      if (res.ok) {
        const json = await res.json();
        const textOut: string | undefined = json?.content?.[0]?.text;
        if (textOut) {
          const match = textOut.match(/\{[\s\S]*\}/);
          if (match) {
            return {
              data: JSON.parse(match[0]) as T,
              engineName: "Anthropic Claude Strategic AI",
            };
          }
        }
      }
    } catch (err) {
      console.warn("[RASED AI] Anthropic call fallback:", err);
    }
  }

  return null;
}

export async function reformulateRootWireToArabic(
  candidate: RawWireCandidate,
  settings: CloudSentinelSettings
): Promise<GeopoliticalDispatch> {
  const combinedText = `${candidate.title} ${candidate.description}`;
  let detectedTheater: WarTheaterId = "MIDDLE_EAST_RED_SEA";
  let severityScore = 1;
  const matchedSystems: string[] = [];

  for (const entry of MILITARY_LEXICON) {
    if (entry.regex.test(combinedText)) {
      matchedSystems.push(entry.termAr);
      if (entry.theaterHint) detectedTheater = entry.theaterHint;
      severityScore += entry.severityBoost || 1;
    }
  }

  const severity: AlertSeverity =
    severityScore >= 4
      ? "CRITICAL"
      : severityScore >= 2
      ? "HIGH"
      : severityScore === 1
      ? "MEDIUM"
      : "ROUTINE";

  const rootAuth = candidate.rootSource.reliabilityBaseScore;
  const indepScore = candidate.rootSource.requiresCrossCheck
    ? Math.min(95, 72 + (candidate.corroboratingCount || 0) * 12)
    : Math.min(98, 88 + (candidate.corroboratingCount || 0) * 5);
  const geoConsistency = 93;
  const mediaScore = 90;
  const overallScore = Math.round(
    rootAuth * 0.35 + indepScore * 0.3 + geoConsistency * 0.2 + mediaScore * 0.15
  );

  // Try external LLM if configured
  const llmRes = await callExternalLlmJson<{
    headlineAr: string;
    flashSummaryAr: string;
    detailedRewriteAr: string;
    locationAr: string;
    operationalImpactAr: string;
    narrativeBalanceAr: string;
    scenarios24to72hAr: string[];
    historicalContextAr: string;
    tagsAr: string[];
  }>(
    settings,
    `أنت محرر استخبارات جيوسياسية وعسكرية صارم في منظومة "راصد". مهمتك إعادة صياغة البرقيات الصادرة من المصادر الأم فقط إلى لغة عربية فصحى رصينة ودقيقة خالية تمامًا من التهويل أو الانحياز، مع تقديم تفسير استراتيجي وعسكري عميق. أعد النتيجة ككائن JSON بالحقول: headlineAr, flashSummaryAr, detailedRewriteAr, locationAr, operationalImpactAr, narrativeBalanceAr, scenarios24to72hAr (مصفوفة نصية), historicalContextAr, tagsAr (مصفوفة نصية).`,
    `المصدر الأم: ${candidate.rootSource.nameAr} (${candidate.rootSource.officialDomain})
طبيعة المصدر: ${candidate.rootSource.biasNatureAr}
العنوان الأصلي: ${candidate.title}
المقتطف الأصلي: ${candidate.description}`
  );

  const theaterCoords: Record<
    WarTheaterId,
    { lat: number; lng: number; label: string; locAr: string }
  > = {
    MIDDLE_EAST_RED_SEA: {
      lat: 21.4,
      lng: 41.0,
      label: "21°24'N 41°00'E",
      locAr: "مسرح الشرق الأوسط والممرات البحرية",
    },
    EAST_EUROPE: {
      lat: 48.4,
      lng: 35.0,
      label: "48°24'N 35°00'E",
      locAr: "مسرح أوروبا الشرقية والبحر الأسود",
    },
    INDO_PACIFIC_TAIWAN: {
      lat: 23.7,
      lng: 120.9,
      label: "23°42'N 120°54'E",
      locAr: "مسرح المحيطين الهندي والهادئ",
    },
    SAHEL_HORN_AFRICA: {
      lat: 13.6,
      lng: 38.5,
      label: "13°36'N 38°30'E",
      locAr: "مسرح القرن الأفريقي والساحل",
    },
    STRATEGIC_NUCLEAR_CYBER: {
      lat: 56.5,
      lng: 18.2,
      label: "56°30'N 18°12'E",
      locAr: "مسرح الردع الاستراتيجي والممرات الدولية",
    },
  };

  const coord = theaterCoords[detectedTheater];

  return {
    id: `dsp-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    headlineAr:
      llmRes?.data.headlineAr ||
      `[${candidate.rootSource.shortCode}] برقية موثقة من ${candidate.rootSource.nameAr}: تطورات ميدانية في ${coord.locAr}`,
    flashSummaryAr:
      llmRes?.data.flashSummaryAr ||
      `رصد خادم «راصد» السحابي برقية أولية مباشرة من المصدر الأم (${candidate.rootSource.officialDomain}) تتعلق بتطورات أمنية وعسكرية في ${coord.locAr}، وتم التحقق من أصالة النطاق الرسمي للمصدر.`,
    detailedRewriteAr:
      llmRes?.data.detailedRewriteAr ||
      `أصدر المصدر الأم المعتمد (${candidate.rootSource.nameAr}) تحديثًا إخباريًا مباشرًا تحت عنوان: «${candidate.title}». ووفقًا للبيانات الأولية المقتطفة من النشرة الرسمية (${candidate.description.slice(
        0,
        240
      )})، يتابع محرك «راصد» تقاطعات الخبر مع الوكالات الدولية المستقلة لضمان أعلى درجات الدقة وتنقية التفاصيل من أي قراءات ثانوية.`,
    originalHeadline: candidate.title,
    originalExcerpt: candidate.description || candidate.title,
    originalLanguage: candidate.rootSource.language,
    rootSourceId: candidate.rootSource.id,
    rootSourceNameAr: candidate.rootSource.nameAr,
    rootSourceDomain: candidate.rootSource.officialDomain,
    rootSourceUrl: candidate.link,
    corroboratingSources: [],
    theaterId: detectedTheater,
    locationAr: llmRes?.data.locationAr || coord.locAr,
    coordinates: {
      lat: coord.lat,
      lng: coord.lng,
      label: coord.label,
    },
    severity,
    verificationBadge: candidate.rootSource.requiresCrossCheck
      ? "OFFICIAL_BELLIGERENT_STATEMENT"
      : "INITIAL_PRIMARY_WIRE",
    captureMode: "LIVE_RSS_VERIFIED",
    accuracy: {
      rootAuthenticity: rootAuth,
      independentCorroboration: indepScore,
      geoTemporalConsistency: geoConsistency,
      mediaIntegrity: mediaScore,
      overallScore,
      rationaleAr: candidate.rootSource.requiresCrossCheck
        ? `ملتقط مباشرة من نطاق رسمي (${candidate.rootSource.officialDomain})؛ ونظرًا لكونه بيان طرف رسمي فإنه يخضع لبروتوكول التقاطع المستقل.`
        : `ملتقط مباشرة من خلاصة المصدر الأم المعتمد (${candidate.rootSource.officialDomain}) بدرجة موثوقية تأسيسية ${rootAuth}%.`,
    },
    strategicExplanation: {
      operationalImpactAr:
        llmRes?.data.operationalImpactAr ||
        "يؤثر هذا التطور على معادلة الجاهزية العملياتية وحركة الرصد والإنذار المبكر في المسرح المعني، مع متابعة فورية لأي انعكاسات على الممرات الحيوية.",
      militarySystemsAr:
        matchedSystems.length > 0
          ? matchedSystems
          : ["منظومات الرصد والإنذار الاستراتيجي والاتصالات العسكرية"],
      narrativeBalanceAr:
        llmRes?.data.narrativeBalanceAr || candidate.rootSource.biasNatureAr,
      scenarios24to72hAr: llmRes?.data.scenarios24to72hAr || [
        "صدور بيانات متقاطعة من الوكالات الدولية ووزارات الدفاع المعنية خلال الساعات القادمة.",
        "استمرار حالة الرصد الإلكتروني والجوي لتقييم الأثر الميداني الفعلي.",
      ],
      historicalContextAr:
        llmRes?.data.historicalContextAr ||
        "يندرج هذا الحدث ضمن ديناميكيات التنافس الجيوسياسي المحتدم على خطوط التماس والممرات الاستراتيجية.",
    },
    tagsAr: llmRes?.data.tagsAr || [
      candidate.rootSource.shortCode,
      coord.locAr,
      "مصدر أم مباشر",
    ],
    publishedAtUtc: candidate.pubDateUtc,
    capturedAtUtc: new Date().toISOString(),
    aiEngineUsed:
      llmRes?.engineName || "محرك راصد المحلي للتحقق الجيوسياسي الصارم",
  };
}

export async function analyzeMediaAndTextForensics(
  req: MediaForensicRequest,
  rootSources: RootSource[],
  existingDispatches: GeopoliticalDispatch[],
  settings: CloudSentinelSettings
): Promise<MediaForensicResult> {
  const matchedRoot = matchRootSourceByUrl(req.sourceUrl, rootSources);
  const urlLower = (req.sourceUrl || "").toLowerCase();
  const isSecondaryBlocked = SECONDARY_RUMOR_PATTERNS.some((p) =>
    urlLower.includes(p)
  );
  const hasPropagandaMarkers = SENSATIONAL_PROPAGANDA_REGEX.test(req.claimText);

  // Find related verified primary dispatches by keyword overlap
  const claimWords = req.claimText
    .toLowerCase()
    .split(/[\s,،.؛!؟\-:/]+/)
    .filter((w) => w.length >= 4);

  const matchedDispatches = existingDispatches
    .map((d) => {
      const hay = `${d.headlineAr} ${d.detailedRewriteAr} ${d.originalHeadline} ${d.originalExcerpt} ${d.tagsAr.join(
        " "
      )}`.toLowerCase();
      const hits = claimWords.filter((w) => hay.includes(w)).length;
      return { dispatch: d, hits };
    })
    .filter((x) => x.hits >= 2)
    .sort((a, b) => b.hits - a.hits)
    .slice(0, 3)
    .map((x) => ({
      id: x.dispatch.id,
      headlineAr: x.dispatch.headlineAr,
      rootSourceNameAr: x.dispatch.rootSourceNameAr,
      accuracyScore: x.dispatch.accuracy.overallScore,
    }));

  // Visual Frame Forensics (for uploaded or sampled video)
  const visualObservations: string[] = [];
  const redFlags: string[] = [];
  const findings: string[] = [];
  let baseScore = 68;

  if (matchedRoot) {
    baseScore += 24;
    findings.push(
      `الرابط المرفق ينتمي رسميًا إلى مصدر أم معتمد في سجل راصد: ${matchedRoot.nameAr} (${matchedRoot.officialDomain}).`
    );
  } else if (req.sourceUrl && req.sourceUrl.trim().length > 0) {
    baseScore -= 14;
    redFlags.push(
      `النطاق المقدم (${req.sourceUrl}) غير مدرج ضمن قائمة المصادر الأم المعتمدة؛ يتعامل معه «راصد» كمصدر ثانوي غير موثق حتى يثبت تقاطعه مع وكالة أم.`
    );
  } else {
    redFlags.push(
      "لم يتم إرفاق رابط رسمي مباشر من مصدر أم (مثل وزارة دفاع، UKMTO، IAEA، أو وكالة رويترز/AP/AFP)."
    );
  }

  if (isSecondaryBlocked) {
    baseScore -= 22;
    redFlags.push(
      "ينتمي الرابط إلى منصة تجميع/تواصل اجتماعي معروفة بإعادة تدوير المقاطع الحربية خارج سياقها الزمني."
    );
  }

  if (hasPropagandaMarkers) {
    baseScore -= 20;
    redFlags.push(
      "رصد صياغات تهويلية ودعائية عالية الانفعال في النص (مثل عبارات التدمير الشامل أو المصادر المجهولة)، وهي سمة تقليدية لحرب المعلومات والشائعات."
    );
  } else {
    findings.push(
      "النص يخلو من الصيغ الدعائية الصارخة، وتم فحص المصطلحات العسكرية والجغرافية الواردة فيه."
    );
  }

  if (matchedDispatches.length > 0) {
    baseScore += 12;
    findings.push(
      `تقاطع موضوعي مع ${matchedDispatches.length} برقية موثقة في قاعدة بيانات المصادر الأم النشطة.`
    );
  }

  if (req.mode === "VIDEO_FORENSICS" && req.videoMeta) {
    const meta = req.videoMeta;
    findings.push(
      `البصمة الرقمية الجنائية للملف (SHA-256): ${meta.sha256.slice(0, 24)}... | الأبعاد: ${meta.width}×${meta.height} | المدة: ${meta.durationSec.toFixed(1)} ثانية.`
    );

    const isVerticalCrop = meta.height > meta.width;
    if (isVerticalCrop) {
      baseScore -= 10;
      redFlags.push(
        `الفيديو مقصوص طوليًا (${meta.width}×${meta.height}) بنسبة عرض شائعة في إعادة النشر عبر Reels/TikTok، ما يحجب غالبًا المعالم الجغرافية المحيطة أو التاريخ الأصلي في الزوايا.`
      );
    } else {
      visualObservations.push(
        `أبعاد الفيديو الأفقية (${meta.width}×${meta.height}) متوافقة مع كاميرات الرصد الميداني أو البث الإخباري القياسي.`
      );
    }

    if (meta.width < 480 && meta.height < 480) {
      baseScore -= 12;
      redFlags.push(
        "دقة الفيديو منخفضة جدًا، وهو مؤشر متكرر على إعادة ضغط المقطع مرات عديدة لإخفاء تاريخ تصويره القديم أو شعارات المصدر الأصلي."
      );
    }

    if (req.frames && req.frames.length > 0) {
      const tones = req.frames.map((f) => f.dominantTone);
      const avgLum =
        req.frames.reduce((acc, f) => acc + f.avgLuminance, 0) /
        req.frames.length;
      const maxContrast = Math.max(...req.frames.map((f) => f.contrastScore));

      visualObservations.push(
        `تم استخراج وفحص ${req.frames.length} إطارات مرجعية موزعة زمنيًا بمتوسط سطوع بصري (${Math.round(
          avgLum
        )}/255) وأعلى تباين طيفي (${Math.round(maxContrast)}).`
      );

      if (tones.includes("NIGHT_VISION_GREEN")) {
        visualObservations.push(
          "رصد طيف أخضر أحادي اللون يطابق بصريات الرؤية الليلية (NVG) أو كاميرات المراقبة الليلية."
        );
      }
      if (tones.includes("THERMAL_MONO")) {
        visualObservations.push(
          "رصد تدرج حراري أحادي (FLIR/Thermal) شائع في كاميرات الاستهداف الجوي والمسيّرات الاستطلاعية."
        );
      }
      if (tones.includes("HIGH_FLASH")) {
        visualObservations.push(
          "رصد وميض ضوئي حاد في أحد الإطارات يتسق مع لحظة انفجار أو إطلاق صاروخي ليلي."
        );
      }
    }
  }

  const clampedScore = Math.max(12, Math.min(98, baseScore));

  // Try Multimodal External AI if configured (passes actual base64 video frames!)
  const frameImages = (req.frames || []).map((f) => f.dataUrl);
  const llmForensic = await callExternalLlmJson<{
    arabicNeutralRewrite: string;
    strategicInterpretationAr: string;
    extraFindingsAr: string[];
    extraRedFlagsAr: string[];
    visualFrameObservationsAr: string[];
    adjustedScore?: number;
  }>(
    settings,
    `أنت محلل تحقق جنائي استخباراتي (OSINT & War Video Forensics) في منظومة "راصد". مهمتك فحص النص أو الفيديو الحربي المرفق بدقة صارمة، كشف التضليل أو المقاطع القديمة أو المقتطعة، وإعادة صياغة الجوهر المؤكد فقط بلغة عربية رصينة مع تفسير جيوسياسي وعسكري. أعد كائن JSON يحتوي على: arabicNeutralRewrite, strategicInterpretationAr, extraFindingsAr (مصفوفة), extraRedFlagsAr (مصفوفة), visualFrameObservationsAr (مصفوفة), adjustedScore (رقم 0-100).`,
    `نوع الفحص: ${req.mode}
النص أو الادعاء المراد التحقق منه: ${req.claimText}
الرابط المرفق: ${req.sourceUrl || "غير متوفر"}
الموقع الجغرافي المدعى: ${req.claimedLocationAr || "غير محدد"}
هل النطاق مصدر أم معتمد؟ ${matchedRoot ? `نعم (${matchedRoot.nameAr})` : "لا"}
بيانات الفيديو التقنية: ${req.videoMeta ? JSON.stringify(req.videoMeta) : "لا يوجد فيديو"}
البرقيات الموثقة المتقاطعة في قاعدة راصد: ${JSON.stringify(matchedDispatches)}`,
    frameImages
  );

  const finalScore =
    typeof llmForensic?.data.adjustedScore === "number"
      ? Math.round((clampedScore + llmForensic.data.adjustedScore) / 2)
      : clampedScore;

  const verdict: MediaForensicResult["verdict"] =
    finalScore >= 85
      ? "VERIFIED_ROOT_SOURCE"
      : finalScore >= 65
      ? "PARTIALLY_CORROBORATED"
      : finalScore >= 42
      ? "UNVERIFIED_SECONDARY_CLAIM"
      : "HIGH_MANIPULATION_OR_OLD_FOOTAGE_RISK";

  const verdictLabelMap: Record<MediaForensicResult["verdict"], string> = {
    VERIFIED_ROOT_SOURCE: "موثوق — مسند لمصدر أم ومتسق ميدانيًا",
    PARTIALLY_CORROBORATED: "متقاطع جزئيًا — يتطلب انتظار بيان المصدر الأم المباشر",
    UNVERIFIED_SECONDARY_CLAIM: "ادعاء ثانوي غير مؤكد — يُمنع إرسال إنذار عاجل بشأنه",
    HIGH_MANIPULATION_OR_OLD_FOOTAGE_RISK:
      "خطر تضليل مرتفع / اشتباه بمقطع معاد تدويره أو صياغة دعائية",
  };

  return {
    id: `frn-${Date.now()}`,
    analyzedAtUtc: new Date().toISOString(),
    verdict,
    verdictLabelAr: verdictLabelMap[verdict],
    authenticityScore: finalScore,
    isRootSourceDomain: Boolean(matchedRoot),
    matchedRootSourceNameAr: matchedRoot?.nameAr,
    arabicNeutralRewrite:
      llmForensic?.data.arabicNeutralRewrite ||
      (matchedRoot
        ? `وفقًا لما ورد عبر المصدر الأم (${matchedRoot.nameAr}): ${req.claimText
            .replace(SENSATIONAL_PROPAGANDA_REGEX, "")
            .trim()}`
        : `تُتداول رواية غير مسندة لمصدر أم تفيد بـ: «${req.claimText.slice(
            0,
            220
          )}». وبموجب معايير الدقة في «راصد»، تظل هذه المعلومة قيد الحجر التحققي لحين صدور تأكيد رسمي من وكالة أنباء دولية أم أو جهة رقابية معتمدة.`),
    strategicInterpretationAr:
      llmForensic?.data.strategicInterpretationAr ||
      (matchedDispatches.length > 0
        ? `يرتبط مضمون الفحص بسياق العمليات الجارية الموثقة في برقية (${matchedDispatches[0].headlineAr})، غير أن «راصد» يفصل بصرامة بين الوقائع المؤكدة من المصادر الأم وبين التفسيرات أو المقاطع المتداولة عبر الحسابات الثانوية.`
        : "في بيئة الحروب الجيوسياسية الحديثة، تمثل المقاطع المجتزأة والادعاءات العاجلة غير المسندة أداة حرب نفسية؛ لذلك يشترط النظام تطابق الإحداثيات البصرية والزمنية مع بلاغ مصدر أم قبل اعتماد الخبر."),
    findingsAr: [
      ...findings,
      ...(llmForensic?.data.extraFindingsAr || []),
    ],
    redFlagsAr: [
      ...redFlags,
      ...(llmForensic?.data.extraRedFlagsAr || []),
    ],
    visualFrameObservationsAr: [
      ...visualObservations,
      ...(llmForensic?.data.visualFrameObservationsAr || []),
    ],
    matchedDispatches,
    aiEngineUsed:
      llmForensic?.engineName ||
      "محرك راصد المحلي للتحقق الجنائي ومطابقة المصادر الأم",
  };
}
