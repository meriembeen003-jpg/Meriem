import { GeopoliticalDispatch, WarTheater } from "@/lib/types/geointel";

export const WAR_THEATERS: WarTheater[] = [
  {
    id: "MIDDLE_EAST_RED_SEA",
    nameAr: "الشرق الأوسط والممرات البحرية (البحر الأحمر وهرمز)",
    shortNameAr: "الشرق الأوسط والبحر الأحمر",
    regionCode: "MENA-MAR",
    escalationLevel: 5,
    escalationLabelAr: "تأهب حرج — اشتباكات نشطة وتهديد ملاحي",
    coordinates: {
      lat: 21.5,
      lng: 41.2,
      mapX: 595,
      mapY: 225,
    },
    chokePointsAr: [
      "مضيق باب المندب",
      "مضيق هرمز",
      "قناة السويس",
      "حوض شرق المتوسط",
    ],
    activeForcesAr: [
      "قوات الدفاع الجوي والبحري الإقليمية",
      "الأسطول الخامس والقيادة المركزية (CENTCOM)",
      "المهمة البحرية الأوروبية (EUNAVFOR Aspides)",
      "منظومات الصواريخ الباليستية والمسيّرات البحرية",
    ],
    strategicSummaryAr:
      "أعلى مسارح العمليات حساسية لسلاسل إمداد الطاقة والتجارة العالمية (12% من التجارة البحرية عبر باب المندب و20% من النفط العالمي عبر مضيق هرمز)، مع تقاطع معادلات الردع الصاروخي والدفاع الجوي متعدد الطبقات.",
  },
  {
    id: "EAST_EUROPE",
    nameAr: "الحرب الروسية-الأوكرانية والجناح الشرقي للناتو",
    shortNameAr: "أوروبا الشرقية والبحر الأسود",
    regionCode: "EEUR-BLK",
    escalationLevel: 5,
    escalationLabelAr: "تأهب حرج — حرب استنزاف برية وجوية عالية الكثافة",
    coordinates: {
      lat: 48.3,
      lng: 35.1,
      mapX: 565,
      mapY: 142,
    },
    chokePointsAr: [
      "ممر سوفالكي (بحر البلطيق)",
      "شبه جزيرة القرم ومضيق كيرتش",
      "محاور دونباس وزابوريجيا",
      "مضايق البوسفور والدردنيل",
    ],
    activeForcesAr: [
      "القوات المسلحة الروسية وأسطول البحر الأسود",
      "هيئة الأركان الأوكرانية وقوات المسيّرات",
      "قوات الانتشار السريع لحلف الناتو (الجناح الشرقي)",
    ],
    strategicSummaryAr:
      "أكبر حرب برية تقليدية في أوروبا منذ الحرب العالمية الثانية؛ تمثل مختبرًا حيًا للحرب الإلكترونية، أسراب المسيّرات التكتيكية، الضربات العميقة على البنية التحتية للطاقة، وإعادة رسم عقيدة الناتو الدفاعية.",
  },
  {
    id: "INDO_PACIFIC_TAIWAN",
    nameAr: "مضيق تايوان وبحر الصين الجنوبي وشبه الجزيرة الكورية",
    shortNameAr: "المحيطين الهندي والهادئ",
    regionCode: "INDOPAC",
    escalationLevel: 4,
    escalationLabelAr: "تأهب مرتفع — مناورات حصار بحري وجوي واختبارات صاروخية",
    coordinates: {
      lat: 24.0,
      lng: 121.0,
      mapX: 805,
      mapY: 218,
    },
    chokePointsAr: [
      "مضيق تايوان",
      "مضيق ملقا",
      "ممر باشي (بحر الفلبين)",
      "الخط الفاصل الكوري (DMZ)",
    ],
    activeForcesAr: [
      "قيادة المسرح الشرقي لجيش التحرير الشعبي الصيني (PLA)",
      "الأسطول السابع الأمريكي وحلفاء (اليابان، كوريا الجنوبية، الفلبين)",
      "القوات الاستراتيجية لكوريا الشمالية",
    ],
    strategicSummaryAr:
      "مركز الثقل الجيواقتصادي العالمي وسلاسل توريد أشباه الموصلات الفائقة؛ تتصاعد فيه تكتيكات المنطقة الرمادية (Gray-Zone Warfare)، الدوريات البحرية المشتركة، واختبارات الصواريخ الباليستية العابرة للقارات.",
  },
  {
    id: "SAHEL_HORN_AFRICA",
    nameAr: "القرن الأفريقي وحزام الساحل وجنوب البحر الأحمر",
    shortNameAr: "القرن الأفريقي والساحل",
    regionCode: "AFR-SAHEL",
    escalationLevel: 4,
    escalationLabelAr: "تأهب مرتفع — صراعات نفوذ دولي وإعادة تموضع قواعد عسكرية",
    coordinates: {
      lat: 13.5,
      lng: 32.5,
      mapX: 558,
      mapY: 262,
    },
    chokePointsAr: [
      "خليج عدن والقرن الأفريقي",
      "ممرات الساحل والصحراء",
      "حوض النيل والساحل السوداني على البحر الأحمر",
    ],
    activeForcesAr: [
      "الجيوش الوطنية والتحالفات الإقليمية في الساحل",
      "القواعد البحرية الدولية في جيبوتي والبحر الأحمر",
      "تحولات الشراكات العسكرية الدولية في غرب وشرق أفريقيا",
    ],
    strategicSummaryAr:
      "مسرح تنافس جيوسياسي حاد على الموانئ المطلة على البحر الأحمر والموارد الاستراتيجية (اليورانيوم، الذهب، الليثيوم)، مع إعادة هيكلة شاملة للوجود العسكري الأجنبي في الساحل الأفريقي.",
  },
  {
    id: "STRATEGIC_NUCLEAR_CYBER",
    nameAr: "الردع النووي، الفضاء العسكري، والكابلات البحرية والسيبرانية",
    shortNameAr: "الردع النووي والفضاء والبحار",
    regionCode: "STRAT-NUC",
    escalationLevel: 4,
    escalationLabelAr: "تأهب مرتفع — تحديث العقائد النووية وحماية البنية التحتية العميقة",
    coordinates: {
      lat: 59.0,
      lng: 18.0,
      mapX: 515,
      mapY: 108,
    },
    chokePointsAr: [
      "ممر غرينلاند-أيسلندا-المملكة المتحدة (GIUK Gap)",
      "الكابلات البحرية للألياف الضوئية العابرة للمحيطات",
      "مدارات أقمار الإنذار المبكر والملاحة العسكرية",
      "المنشآت النووية الخاضعة لرقابة IAEA",
    ],
    activeForcesAr: [
      "الغواصات النووية الحاملة للصواريخ الباليستية (SSBN)",
      "الوكالة الدولية للطاقة الذرية (IAEA)",
      "وحدات حماية الكابلات البحرية والقيادات السيبرانية",
    ],
    strategicSummaryAr:
      "يشمل البعد فوق الإقليمي للحروب الحديثة: مراقبة المعاهدات النووية، رصد حركة الغواصات وحاملات الطائرات، أمن كابلات الإنترنت والطاقة في قاع البحار، وسلامة المنشآت الذرية.",
  },
];

export const BASELINE_DISPATCHES: GeopoliticalDispatch[] = [
  {
    id: "dsp-ukmto-redsea-01",
    headlineAr:
      "هيئة عمليات التجارة البحرية البريطانية (UKMTO) تسجل حادثًا ملاحيًا على بُعد 68 ميلًا بحريًا جنوب غرب الحديدة وتوجه تحذيرًا للسفن العابرة",
    flashSummaryAr:
      "أصدرت UKMTO بلاغًا رسميًا عاجلًا مبنيًا على تقرير مباشر من ضابط أمن سفينة تجارية يفيد برصد انفجارين في محيط السفينة دون تسجيل إصابات بشرية، مع استمرار إبحار السفينة نحو ميناء المقصد.",
    detailedRewriteAr:
      "أفادت هيئة عمليات التجارة البحرية البريطانية (UKMTO) — وهي المصدر الأم المعتمد للبلاغات الملاحية في البحر الأحمر وخليج عدن — بتلقيها بلاغًا موثقًا من ربان ناقلة تجارية أثناء عبورها الممر الملاحي الدولي جنوب البحر الأحمر. وأوضح البيان الأصلي أن طاقم السفينة رصد ارتطام مقذوفين بالمياه على مسافة قريبة من الجانب الأيسر للسفينة، أعقبه تفعيل بروتوكولات السلامة البحرية، مع تأكيد سلامة الطاقم بالكامل وعدم تسرب أي مواد خطرة. وبالتوازي، نقلت وكالة رويترز عن شركات تأمين بحري تأكيدها مطابقة الإحداثيات المعلنة لمسار الشحن التجاري.",
    originalHeadline:
      "UKMTO WARNING INCIDENT: Vessel reports two explosions in close proximity 68NM SW of Al Hudaydah, crew safe",
    originalExcerpt:
      "UKMTO has received a report of an incident 68NM southwest of Al Hudaydah. The Master of a merchant vessel reports two explosions in close proximity to the port side. Vessel and all crew are reported safe and proceeding to next port of call. Authorities are investigating.",
    originalLanguage: "en",
    rootSourceId: "ukmto-maritime",
    rootSourceNameAr: "هيئة عمليات التجارة البحرية البريطانية (UKMTO)",
    rootSourceDomain: "ukmto.org",
    rootSourceUrl: "https://www.ukmto.org/indian-ocean/recent-incidents",
    corroboratingSources: [
      {
        sourceId: "reuters-world",
        nameAr: "وكالة رويترز للأنباء",
        officialDomain: "reuters.com",
        confirmationNoteAr:
          "تأكيد مستقل عبر مصادر الملاحة والتأمين البحري في لندن لموقع وتوقيت الحادث.",
        timestampUtc: "2026-11-06T11:48:00Z",
      },
      {
        sourceId: "us-dod-pentagon",
        nameAr: "القيادة المركزية الأمريكية (CENTCOM)",
        officialDomain: "defense.gov",
        confirmationNoteAr:
          "رصد راداري لإطلاق مقذوفات باتجاه الممر الملاحي في التوقيت ذاته دون أضرار هيكلية بالسفينة.",
        timestampUtc: "2026-11-06T12:05:00Z",
      },
    ],
    theaterId: "MIDDLE_EAST_RED_SEA",
    locationAr: "جنوب البحر الأحمر — ممر باب المندب الملاحي",
    coordinates: {
      lat: 14.21,
      lng: 42.18,
      label: "14°12'N 42°10'E",
    },
    severity: "CRITICAL",
    verificationBadge: "CONFIRMED_MULTI_PRIMARY",
    captureMode: "REFERENCE_BASELINE",
    accuracy: {
      rootAuthenticity: 99,
      independentCorroboration: 95,
      geoTemporalConsistency: 97,
      mediaIntegrity: 92,
      overallScore: 96,
      rationaleAr:
        "بلاغ ملاحي رسمي مباشر من المصدر الأم (UKMTO) بإحداثيات بحرية دقيقة، متقاطع مع وكالة رويترز وبيانات الرصد الراداري البحري.",
    },
    strategicExplanation: {
      operationalImpactAr:
        "يبقي هذا الحادث أقساط التأمين ضد مخاطر الحرب (War Risk Insurance) عند مستويات مرتفعة للسفن العابرة نحو قناة السويس، ويدفع شركات الشحن الكبرى لمواصلة الموازنة بين ممر باب المندب وطريق رأس الرجاء الصالح الأطول بـ 10 إلى 14 يومًا.",
      militarySystemsAr: [
        "رادارات الإنذار البحري وحماية القطع السطحية",
        "الصواريخ المضادة للسفن الباليستية والمجنحة (ASBM / ASCM)",
        "الزوارق والمسيّرات البحرية الموجّهة عن بُعد (USV)",
      ],
      narrativeBalanceAr:
        "يركّز بلاغ UKMTO المحايد على السلامة الملاحية والإحداثيات المؤكدة دون تبني ادعاءات سياسية، بينما لم تصدر حتى لحظة التوثيق لقطات بصرية مستقلة تدعم الشائعات المتداولة على منصات التواصل حول غرق السفينة، وهو ما ينفيه استمرار إشارة التتبع الملاحي (AIS).",
      scenarios24to72hAr: [
        "تكثيف الدوريات الجوية والبحرية الاعتراضية لحماية القوافل التجارية خلال الساعات الـ 48 القادمة.",
        "احتمال صدور بيان تفصيلي يوضح نوع المقذوف المستخدم ونتائج الاعتراض الجوي.",
        "ارتفاع مؤقت في رسوم عبور الناقلات الفورية في حوض البحر الأحمر.",
      ],
      historicalContextAr:
        "يمر عبر مضيق باب المندب ما يقارب 12% من حجم التجارة العالمية المنقولة بحرًا، ما يجعل أي اضطراب تكتيكي فيه ذا أثر فوري على سلاسل الإمداد الأوروبية والآسيوية.",
    },
    tagsAr: ["البحر الأحمر", "UKMTO", "أمن الملاحة", "باب المندب", "إنذار حرج"],
    publishedAtUtc: "2026-11-06T11:35:00Z",
    capturedAtUtc: "2026-11-06T11:36:12Z",
    aiEngineUsed: "محرك راصد للتحقق المتقاطع والصياغة العربية",
  },
  {
    id: "dsp-iaea-nuclear-02",
    headlineAr:
      "الوكالة الدولية للطاقة الذرية (IAEA) تصدر بيانًا رسميًا حول استعادة خط التغذية الكهربائية الاحتياطي بقدرة 330 كيلوفولت لمحطة زابوريجيا النووية",
    flashSummaryAr:
      "أكد المدير العام للوكالة الدولية للطاقة الذرية من مقرها في فيينا نجاح فرق الصيانة، برصد مباشر من مفتشي الوكالة الميدانيين، في إعادة ربط خط الكهرباء الاحتياطي بعد فصله جراء نشاط عسكري قريب، مع بقاء مستويات الإشعاع ضمن الحدود الطبيعية.",
    detailedRewriteAr:
      "نشرت الوكالة الدولية للطاقة الذرية (IAEA) بيانًا فنيًا موثقًا صادرًا عن بعثتها الدائمة المتمركزة داخل محطة زابوريجيا للطاقة النووية، أوضحت فيه إعادة تشغيل خط الإمداد الخارجي الاحتياطي بقدرة 330 كيلوفولت، والذي يُعد حيويًا لتبريد المفاعلات الستة المتوقفة عن توليد الطاقة (Cold Shutdown). وشدد البيان الأصلي على أن فقدان التغذية الخارجية المتكرر يظل مصدر قلق نووي بالغ، داعيًا كافة الأطراف العسكرية إلى الامتناع التام عن أي استهداف لمحطات التحويل الكهربائية المرتبطة بالمنشأة.",
    originalHeadline:
      "IAEA Update: Zaporizhzhia Nuclear Power Plant reconnects to 330 kV back-up power line; radiation levels remain normal",
    originalExcerpt:
      "IAEA experts stationed at the Zaporizhzhia Nuclear Power Plant (ZNPP) confirmed today that the 330 kilovolt back-up off-site power line has been restored following repairs, reinforcing nuclear safety cooling redundancy while all six reactors remain in cold shutdown.",
    originalLanguage: "en",
    rootSourceId: "iaea-nuclear",
    rootSourceNameAr: "الوكالة الدولية للطاقة الذرية — البيانات الرسمية",
    rootSourceDomain: "iaea.org",
    rootSourceUrl: "https://www.iaea.org/feeds/topnews",
    corroboratingSources: [
      {
        sourceId: "ap-world",
        nameAr: "وكالة أسوشيتد برس (AP)",
        officialDomain: "apnews.com",
        confirmationNoteAr:
          "نقل رسمي عن مقر الوكالة في فيينا وتأكيد مطابقة القراءات الإشعاعية الأوروبية للمعدل الطبيعي.",
        timestampUtc: "2026-11-06T10:20:00Z",
      },
    ],
    theaterId: "EAST_EUROPE",
    locationAr: "زابوريجيا — جنوب شرق أوكرانيا (رقابة IAEA)",
    coordinates: {
      lat: 47.51,
      lng: 34.58,
      label: "47°30'N 34°35'E",
    },
    severity: "HIGH",
    verificationBadge: "CONFIRMED_MULTI_PRIMARY",
    captureMode: "REFERENCE_BASELINE",
    accuracy: {
      rootAuthenticity: 100,
      independentCorroboration: 96,
      geoTemporalConsistency: 98,
      mediaIntegrity: 95,
      overallScore: 98,
      rationaleAr:
        "توثيق ميداني مباشر من مفتشي الوكالة الدولية للطاقة الذرية المتواجدين فعليًا داخل المنشأة، وهو المصدر الأم الأعلى موثوقية عالميًا في الملف النووي.",
    },
    strategicExplanation: {
      operationalImpactAr:
        "تمنع استعادة خط 330 كيلوفولت الاضطرار للاعتماد على مولدات الديزل الطارئة في حال انقطاع الخط الرئيسي (750 كيلوفولت)، ما يخفض خطر الحوادث التقنية النووية على المدى القصير رغم استمرار القصف المدفعي في المحيط الإقليمي.",
      militarySystemsAr: [
        "البنية التحتية لشبكات الجهد العالي (750kV / 330kV)",
        "أنظمة التبريد النووي في وضع الإغلاق البارد (Cold Shutdown)",
        "أجهزة الرصد الإشعاعي المبكر التابعة لـ IAEA",
      ],
      narrativeBalanceAr:
        "يتبادل الطرفان الروسي والأوكراني المسؤولية عن الأضرار التي لحقت بخطوط النقل الخارجية، بينما يلتزم بيان الوكالة الدولية بالحياد الصارم مكتفيًا بتوثيق الحالة الهندسية ومستوى الأمان الإشعاعي المؤكد.",
      scenarios24to72hAr: [
        "استمرار مراقبة استقرار الشبكة الكهربائية مع دخول فصل الشتاء وارتفاع الأحمال على محطات التحويل.",
        "تقديم إحاطة تقنية دورية لمجلس محافظي الوكالة الدولية للطاقة الذرية في فيينا.",
      ],
      historicalContextAr:
        "تُعد محطة زابوريجيا أكبر محطة للطاقة النووية في أوروبا بستة مفاعلات من طراز VVER-1000، وتخضع منذ عام 2022 لبعثة رقابة دائمة من الوكالة الدولية للطاقة الذرية.",
    },
    tagsAr: ["الأمن النووي", "IAEA", "زابوريجيا", "أوروبا الشرقية", "طاقة"],
    publishedAtUtc: "2026-11-06T10:05:00Z",
    capturedAtUtc: "2026-11-06T10:06:30Z",
    aiEngineUsed: "محرك راصد للتحقق المتقاطع والصياغة العربية",
  },
  {
    id: "dsp-nato-baltic-03",
    headlineAr:
      "القيادة العليا لحلف الناتو تعلن انطلاق دوريات بحرية وجوية معززة في بحر البلطيق لحماية الكابلات البحرية وخطوط الطاقة",
    flashSummaryAr:
      "أعلنت القيادة البحرية لحلف شمال الأطلسي (MARCOM) في بيان رسمي نشر فرقاطات مزودة بسونار أعماق وطائرات دورية بحرية لمراقبة البنية التحتية الحرجة تحت سطح البحر في بحر البلطيق وبحر الشمال.",
    detailedRewriteAr:
      "أصدر المقر العام لحلف شمال الأطلسي (NATO) بيانًا رسميًا يوثق تفعيل مرحلة معززة من مراقبة البنية التحتية الحيوية في قاع بحر البلطيق، بمشاركة قطع بحرية من الدول الإسكندنافية وألمانيا والمملكة المتحدة، إضافة إلى مسيّرات غواصة لفحص خطوط الغاز وكابلات الألياف الضوئية الدولية. وأشارت وكالة الصحافة الفرنسية (AFP) ووكالة تاس الروسية إلى التطورات من زاويتين متقابلتين: حيث اعتبرها الناتو إجراءً وقائيًا دفاعيًا، بينما وصفتها الخارجية الروسية في بيان رسمي نقلته تاس بأنها عسكرة إضافية للممرات الملاحية المفتوحة.",
    originalHeadline:
      "NATO Allied Maritime Command deploys enhanced naval and undersea surveillance patrols across Baltic Sea critical infrastructure corridors",
    originalExcerpt:
      "NATO Allied Maritime Command (MARCOM) announced today the deployment of additional frigates, minehunters, and maritime patrol aircraft to monitor and safeguard critical undersea cables and pipelines in the Baltic Sea.",
    originalLanguage: "en",
    rootSourceId: "nato-command",
    rootSourceNameAr: "القيادة العليا لحلف شمال الأطلسي (الناتو)",
    rootSourceDomain: "nato.int",
    rootSourceUrl: "https://www.nato.int/cps/en/natohq/rss_feed.htm",
    corroboratingSources: [
      {
        sourceId: "afp-global",
        nameAr: "وكالة الصحافة الفرنسية (AFP)",
        officialDomain: "afp.com",
        confirmationNoteAr:
          "توثيق تحرك الفرقاطات من موانئ البلطيق وتأكيد وزارات الدفاع الإسكندنافية المشاركة.",
        timestampUtc: "2026-11-06T09:10:00Z",
      },
      {
        sourceId: "tass-defense",
        nameAr: "وكالة تاس الروسية (رصد الموقف المقابل)",
        officialDomain: "tass.com",
        confirmationNoteAr:
          "نقل الموقف الرسمي لموسكو الذي يؤكد حق الملاحة الحرة لأسطول البلطيق في المياه الدولية.",
        timestampUtc: "2026-11-06T09:42:00Z",
      },
    ],
    theaterId: "STRATEGIC_NUCLEAR_CYBER",
    locationAr: "بحر البلطيق وممر البنية التحتية البحرية الأوروبية",
    coordinates: {
      lat: 57.4,
      lng: 19.8,
      label: "57°24'N 19°48'E",
    },
    severity: "HIGH",
    verificationBadge: "CONFIRMED_MULTI_PRIMARY",
    captureMode: "REFERENCE_BASELINE",
    accuracy: {
      rootAuthenticity: 96,
      independentCorroboration: 93,
      geoTemporalConsistency: 95,
      mediaIntegrity: 90,
      overallScore: 94,
      rationaleAr:
        "بيان عسكري رسمي من القيادة البحرية للناتو مؤيد بتغطية الوكالات الأوروبية ورصد رد الفعل الدبلوماسي المقابل بدقة وحياد.",
    },
    strategicExplanation: {
      operationalImpactAr:
        "تحمل الكابلات البحرية أكثر من 95% من حركة البيانات والاتصالات المالية العالمية؛ ويعكس هذا الانتشار انتقال حروب المنطقة الرمادية نحو قاع البحار وحساسيات الملاحة قرب جيب كالينينغراد وخليج فنلندا.",
      militarySystemsAr: [
        "فرقاطات الحرب المضادة للغواصات (ASW Frigates)",
        "طائرات الدورية البحرية P-8A Poseidon",
        "مركبات المسح الغواصة غير المأهولة (AUV / ROV) وسونار المسح الجانبي",
      ],
      narrativeBalanceAr:
        "يعرض «راصد» البيان العملياتي لحلف الناتو مقترنًا بالموقف الرسمي الروسي المنشور عبر وكالة تاس، لضمان فهم المشهد الجيوسياسي الكامل دون تبني دعاية أي طرف.",
      scenarios24to72hAr: [
        "زيادة عمليات التدقيق الملاحي للسفن التجارية ذات أنظمة التتبع المتقطعة في بحر البلطيق.",
        "إجراء تدريبات استجابة سريعة مشتركة بين القوات البحرية الإسكندنافية.",
      ],
      historicalContextAr:
        "أدى انضمام فنلندا والسويد إلى حلف الناتو إلى تغيير الخريطة الجيوعسكرية لبحر البلطيق بالكامل، مع بقاء خليج فنلندا وكالينينغراد منافذ بحرية حيوية لروسيا.",
    },
    tagsAr: ["الناتو", "الكابلات البحرية", "بحر البلطيق", "حرب الأعماق", "توازن الروايات"],
    publishedAtUtc: "2026-11-06T08:50:00Z",
    capturedAtUtc: "2026-11-06T08:51:15Z",
    aiEngineUsed: "محرك راصد للتحقق المتقاطع والصياغة العربية",
  },
  {
    id: "dsp-indopac-strait-04",
    headlineAr:
      "بيانات رسمية متقابلة في شرق آسيا: رصد مناورات جوية وبحرية مشتركة في محيط مضيق تايوان وبحر الفلبين",
    flashSummaryAr:
      "أعلنت قيادة المسرح الشرقي عبر وكالة شينخوا تنفيذ دوريات جاهزية قتالية بحرية وجوية مشتركة، فيما أكدت وكالتا رويترز وأسوشيتد برس رصد تحركات القطع البحرية وطائرات الإنذار المبكر ضمن مناطق تمييز الهوية الجوية.",
    detailedRewriteAr:
      "في تطور ميداني موثق من المصادر الأم المتقابلة في منطقة المحيطين الهندي والهادئ، نشرت وكالة شينخوا بيانًا رسميًا عن المتحدث باسم قيادة المسرح الشرقي يفيد بإجراء تدريبات تنسيق بحري-جوي لاختبار قدرات السيطرة المشتركة والاعتراض. وفي المقابل، نقلت وكالة رويترز البيانات الرقمية الصادرة عن سلطات الدفاع في تايبيه وطوكيو حول مسارات القطع البحرية عبر ممر باشي الفاصل بين تايوان والفلبين، مع تأكيد استمرار حركة الملاحة التجارية المدنية والطيران الدولي بصورة طبيعية دون إغلاق أي ممر بحري.",
    originalHeadline:
      "Eastern Theater Command conducts joint naval-air combat readiness patrols; regional defense ministries log vessel transits through Bashi Channel",
    originalExcerpt:
      "Official communiqués confirm coordinated naval destroyer and early-warning aircraft patrols around the Taiwan Strait and Bashi Channel, while commercial shipping lanes remain open under close radar monitoring.",
    originalLanguage: "en",
    rootSourceId: "reuters-world",
    rootSourceNameAr: "وكالة رويترز للأنباء (بتقاطع مع شينخوا والبيانات الإقليمية)",
    rootSourceDomain: "reuters.com",
    rootSourceUrl: "https://www.reuters.com/world/asia-pacific/",
    corroboratingSources: [
      {
        sourceId: "xinhua-defense",
        nameAr: "وكالة شينخوا — بيان قيادة المسرح الشرقي",
        officialDomain: "news.cn",
        confirmationNoteAr:
          "تأكيد رسمي من بكين لطبيعة الدوريات المشتركة باعتبارها تدريبات جاهزية روتينية.",
        timestampUtc: "2026-11-06T06:30:00Z",
      },
      {
        sourceId: "naval-news-primary",
        nameAr: "مرصد Naval News العسكري",
        officialDomain: "navalnews.com",
        confirmationNoteAr:
          "تحديد فئات المدمرات المرافقة ومسار العبور البحري نحو غرب المحيط الهادئ.",
        timestampUtc: "2026-11-06T07:12:00Z",
      },
    ],
    theaterId: "INDO_PACIFIC_TAIWAN",
    locationAr: "مضيق تايوان وممر باشي (بحر الفلبين)",
    coordinates: {
      lat: 21.8,
      lng: 120.9,
      label: "21°48'N 120°54'E",
    },
    severity: "MEDIUM",
    verificationBadge: "CONFIRMED_MULTI_PRIMARY",
    captureMode: "REFERENCE_BASELINE",
    accuracy: {
      rootAuthenticity: 95,
      independentCorroboration: 92,
      geoTemporalConsistency: 94,
      mediaIntegrity: 91,
      overallScore: 93,
      rationaleAr:
        "تطابق الوقائع الميدانية بين البيان الرسمي الصيني والبيانات الدفاعية الإقليمية وتغطية وكالة رويترز، مع تنقية الخبر من مبالغات الحسابات غير الرسمية.",
    },
    strategicExplanation: {
      operationalImpactAr:
        "يُعد ممر باشي البوابة البحرية الاستراتيجية التي تربط بحر الصين الجنوبي بالمحيط الهادئ المفتوح، كما تمر عبر قاعه كابلات اتصالات رئيسية لشرق آسيا؛ وتهدف الدوريات المتكررة إلى ترسيخ الوجود العملياتي دون تجاوز عتبة الاشتباك المباشر.",
      militarySystemsAr: [
        "مدمرات الدفاع الجوي الموجه (Type 052D / Type 055)",
        "طائرات الإنذار المبكر والتحكم المحمول جوًا (AEW&C KJ-500)",
        "منظومات الرادار الساحلي وصواريخ الدفاع البحري",
      ],
      narrativeBalanceAr:
        "تصف بكين هذه التحركات رسميًا بدوريات سيادية مشروعة، بينما تصنفها الأطراف المقابلة ضمن ضغوط المنطقة الرمادية المستمرة؛ ويُبرز التقرير حقيقة عدم تأثر الشحن التجاري المدني تفاديًا للتهويل.",
      scenarios24to72hAr: [
        "انتهاء جدول الدوريات المعلنة وعودة غالبية الوحدات الجوية إلى قواعدها الساحلية خلال 48 ساعة.",
        "مراقبة أي عبور مقابل لسفن الأسطول السابع الأمريكي في إطار عمليات حرية الملاحة (FONOP).",
      ],
      historicalContextAr:
        "يمر عبر مضيق تايوان وبحر الصين الجنوبي أكثر من ثلث حركة الشحن البحري العالمي، ما يجعل استقراره ركيزة أساسية للاقتصاد الدولي.",
    },
    tagsAr: ["مضيق تايوان", "ممر باشي", "المحيط الهادئ", "توازن الروايات", "الأساطيل"],
    publishedAtUtc: "2026-11-06T06:15:00Z",
    capturedAtUtc: "2026-11-06T06:16:40Z",
    aiEngineUsed: "محرك راصد للتحقق المتقاطع والصياغة العربية",
  },
];

export const DRILL_DISPATCH_POOL: Omit<
  GeopoliticalDispatch,
  "id" | "publishedAtUtc" | "capturedAtUtc"
>[] = [
  {
    headlineAr:
      "الأمم المتحدة ومجلس الأمن يعقدان جلسة إحاطة طارئة حول أمن الممرات الإنسانية والبحرية في القرن الأفريقي وجنوب البحر الأحمر",
    flashSummaryAr:
      "دعت الأمانة العامة للأمم المتحدة عبر نشرتها الرسمية للسلم والأمن الدوليين إلى خفض فوري للتصعيد العسكري وحماية سلاسل الإمداد الغذائي والموانئ الحيوية في حوض البحر الأحمر والقرن الأفريقي.",
    detailedRewriteAr:
      "وفقًا للنشرة الرسمية الصادرة عن قسم السلم والأمن الدوليين في الأمم المتحدة (UN News)، استمع مجلس الأمن الدولي إلى إحاطة موثقة بالأرقام حول تداعيات التوترات العسكرية على الموانئ الحيوية في القرن الأفريقي والسودان وجنوب البحر الأحمر. وأكد التقرير الأممي بالتقاطع مع بيانات وكالة الصحافة الفرنسية (AFP) ضرورة تحييد الموانئ المدنية وممرات الإغاثة عن التجاذبات الجيوسياسية الإقليمية والدولية.",
    originalHeadline:
      "UN Security Council holds urgent briefing on maritime corridor security and humanitarian logistics across the Horn of Africa and Red Sea basin",
    originalExcerpt:
      "Senior UN Peace and Security officials briefed the Security Council today on escalating military risks to port infrastructure and vital maritime supply routes linking the Red Sea and Horn of Africa.",
    originalLanguage: "en",
    rootSourceId: "un-security-council",
    rootSourceNameAr: "مجلس الأمن والأمم المتحدة — السلم والأمن الدوليان",
    rootSourceDomain: "news.un.org",
    rootSourceUrl:
      "https://news.un.org/feed/subscribe/ar/news/topic/peace-and-security/feed/rss.xml",
    corroboratingSources: [
      {
        sourceId: "afp-global",
        nameAr: "وكالة الصحافة الفرنسية (AFP)",
        officialDomain: "afp.com",
        confirmationNoteAr: "تغطية مباشرة من مقر مجلس الأمن بنيويورك للنص الحرفي للإحاطة الأممية.",
        timestampUtc: new Date().toISOString(),
      },
    ],
    theaterId: "SAHEL_HORN_AFRICA",
    locationAr: "القرن الأفريقي وحوض جنوب البحر الأحمر",
    coordinates: {
      lat: 11.58,
      lng: 43.14,
      label: "11°35'N 43°08'E",
    },
    severity: "HIGH",
    verificationBadge: "CONFIRMED_MULTI_PRIMARY",
    captureMode: "MANUAL_VERIFIED_SCAN",
    accuracy: {
      rootAuthenticity: 98,
      independentCorroboration: 94,
      geoTemporalConsistency: 96,
      mediaIntegrity: 93,
      overallScore: 96,
      rationaleAr: "بيان أممي رسمي موثق بالمحضر العلني لمجلس الأمن الدولي ومتقاطع مع وكالة أنباء دولية أم.",
    },
    strategicExplanation: {
      operationalImpactAr:
        "تشكل موانئ القرن الأفريقي (جيبوتي، بورتسودان، بربرة، مصوع) نقاط ارتكاز لوجستية وعسكرية حاسمة للدول الكبرى المطلة أو العابرة للبحر الأحمر.",
      militarySystemsAr: [
        "القواعد اللوجستية البحرية ومرافق الإسناد في خليج عدن",
        "أنظمة مراقبة السواحل والرادارات البحرية بعيدة المدى",
      ],
      narrativeBalanceAr:
        "يركز المحضر الأممي على القانون الدولي الإنساني وحرية الملاحة، مع عرض مواقف الدول الأعضاء الدائمة في مجلس الأمن دون انتقائية.",
      scenarios24to72hAr: [
        "مشاورات لصياغة بيان رئاسي أو مشروع قرار حول تأمين الموانئ المدنية.",
        "زيادة التنسيق بين البعثات البحرية الدولية في خليج عدن.",
      ],
      historicalContextAr:
        "تستضيف منطقة القرن الأفريقي أكبر تكتل للقواعد البحرية الدولية في العالم نظرًا لإشرافها المباشر على مضيق باب المندب.",
    },
    tagsAr: ["مجلس الأمن", "القرن الأفريقي", "أمن الموانئ", "الأمم المتحدة"],
    aiEngineUsed: "محرك راصد للتحقق المتقاطع والصياغة العربية",
  },
  {
    headlineAr:
      "معهد ستوكهولم (SIPRI) ومعهد دراسات الحرب (ISW) يرصدان تسارع إنتاج ذخائر الدفاع الجوي بعيد المدى ومنظومات الاعتراض الأوروبية",
    flashSummaryAr:
      "كشف تقرير استراتيجي موثق صادر عن SIPRI بالتقاطع مع بيانات وزارات الدفاع الأوروبية عن توقيع عقود تصنيع مشترك لمضاعفة الطاقة الإنتاجية لصواريخ الاعتراض الجوي والذخائر المدفعية القياسية عيار 155 ملم.",
    detailedRewriteAr:
      "نشر معهد ستوكهولم الدولي لأبحاث السلام (SIPRI) بيانات محدثة حول سلاسل الإمداد الدفاعية الأوروبية، موثقًا انتقال الصناعات العسكرية في أوروبا الشرقية والغربية من نمط الإمداد السلمي إلى نمط العقود متعددة السنوات عالية الوتيرة، لا سيما في قطاع أنظمة الدفاع الجوي الطبقي وصواريخ الاعتراض التكتيكية لمواجهة تهديدات المسيّرات والصواريخ الباليستية.",
    originalHeadline:
      "SIPRI Defense Industrial Assessment: European multi-year joint procurement surges for layered air-defense interceptors and 155mm artillery production",
    originalExcerpt:
      "Verified defense procurement data compiled by SIPRI indicates a structural expansion in European manufacturing lines for medium- and long-range surface-to-air interceptors and counter-UAS systems.",
    originalLanguage: "en",
    rootSourceId: "sipri-strategic",
    rootSourceNameAr: "معهد ستوكهولم الدولي لأبحاث السلام (SIPRI)",
    rootSourceDomain: "sipri.org",
    rootSourceUrl: "https://www.sipri.org/rss/combined.xml",
    corroboratingSources: [
      {
        sourceId: "isw-analysis",
        nameAr: "معهد دراسات الحرب (ISW)",
        officialDomain: "understandingwar.org",
        confirmationNoteAr: "ربط تحليلي بين معدلات استهلاك صواريخ الاعتراض الميدانية وخطط التوسع الصناعي.",
        timestampUtc: new Date().toISOString(),
      },
    ],
    theaterId: "EAST_EUROPE",
    locationAr: "القارة الأوروبية — منظومات الدفاع الجوي والصناعات العسكرية",
    coordinates: {
      lat: 52.23,
      lng: 21.01,
      label: "52°13'N 21°00'E",
    },
    severity: "MEDIUM",
    verificationBadge: "CONFIRMED_MULTI_PRIMARY",
    captureMode: "MANUAL_VERIFIED_SCAN",
    accuracy: {
      rootAuthenticity: 98,
      independentCorroboration: 95,
      geoTemporalConsistency: 97,
      mediaIntegrity: 96,
      overallScore: 97,
      rationaleAr: "تقرير رقمي موثق من المرجع الدولي الأول لبيانات التسلح (SIPRI) بالاستناد إلى العقود الحكومية المعلنة رسميًا.",
    },
    strategicExplanation: {
      operationalImpactAr:
        "أثبتت الحروب الجيوسياسية المعاصرة أن التفوق لا يعتمد على التكنولوجيا فحسب، بل على القدرة الصناعية على تعويض مخزونات صواريخ الاعتراض بتكلفة مستدامة في مواجهة المسيّرات منخفضة التكلفة.",
      militarySystemsAr: [
        "منظومات الدفاع الجوي الطبقي (Patriot / SAMP-T / IRIS-T)",
        "منظومات الليزر والمدفعية المضادة للمسيّرات (C-UAS)",
        "خطوط إنتاج الذخائر المدفعية عيار 155 ملم",
      ],
      narrativeBalanceAr:
        "يستند التقرير إلى الأرقام الميزانياتية الرسمية المنشورة في الجرائد الرسمية للدول دون أي تكهنات غير موثقة.",
      scenarios24to72hAr: [
        "إعلان شراكات صناعية دفاعية إضافية لتوطين إنتاج محركات الصواريخ والوقود الصلب.",
        "تركيز متزايد على أنظمة الاعتراض منخفضة التكلفة مقارنة بصواريخ الدفاع الجوي التقليدية.",
      ],
      historicalContextAr:
        "يمثل هذا التحول أكبر إعادة هيكلة للقاعدة الصناعية الدفاعية الأوروبية منذ نهاية الحرب الباردة.",
    },
    tagsAr: ["SIPRI", "الدفاع الجوي", "الصناعات العسكرية", "اقتصاديات الحروب"],
    aiEngineUsed: "محرك راصد للتحقق المتقاطع والصياغة العربية",
  },
];
