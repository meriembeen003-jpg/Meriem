const chapters = [
  {
    n: "01", era: "قبل 13.8 مليار سنة ← أول أجزاء الثانية", topic: "الكون", tone: "violet",
    title: "التمدد الكوني: إلى أقدم حدّ تصفه الفيزياء",
    summary: "تُظهر القياسات أن الكون يتمدّد، وأنه كان في الماضي أشد حرارة وكثافة. «الانفجار العظيم» وصف لتطور الكون من حالة مبكرة حارة ومتمددة، لا انفجار لمادة داخل فراغ سابق.",
    evidence: "الاستقراء إلى الخلف يعطي عمراً يقارب 13.8 مليار سنة ضمن نموذج ΛCDM. لكن اللحظة t=0 ليست رصداً مباشراً: التفرد نتيجة استقراء النسبية العامة إلى مجال تفشل فيه النظرية. التضخم الكوني مدعوم بقرائن غير مباشرة، لكن آليته وتفاصيله غير محسومة.",
    test: "تعارض متين بين قياسات مستقلة للتمدد وتاريخ التمدد وبنية الكون وتنبؤات النموذج—بعد فحص المعايرة والبدائل—يفرض تعديله. لا يختبر النموذج ما «قبل» حد صلاحية الفيزياء المعروفة.",
    papers: [["Hubble (1929) — علاقة المسافة بسرعة التباعد، PNAS", "https://doi.org/10.1073/pnas.15.3.168"], ["Planck Collaboration (2020) — إرث بلانك الكوني، A&A", "https://doi.org/10.1051/0004-6361/201833880"]],
    image: ["رسم تسلسل عمر الكون · NASA/ESA", "https://science.nasa.gov/asset/hubble/universe-timeline/"],
    media: ["مرئيات لبدايات الكون · NASA SVS", "https://svs.gsfc.nasa.gov/10128/"],
    sim: ["أرشيف صور ومحاكاة تطور الكون · NASA", "https://imagine.gsfc.nasa.gov/educators/programs/cosmictimes/universe_mashup/archive/complete_archive.html"],
    date: "أقدم حقبة غير مرصودة مباشرة؛ تبدأ الاختبارات الكمية من آثار لاحقة"
  },
  {
    n: "02", era: "الثواني والدقائق الأولى؛ ثم نحو 380 ألف سنة", topic: "المادة", tone: "blue",
    title: "العناصر الأولى ثم أقدم ضوء حرّ",
    summary: "حسابات التخليق النووي البدائي تتنبأ بنسب الهيدروجين والهيليوم والديوتيريوم والليثيوم. وبعدما برد الكون لتتكون ذرات متعادلة، انطلق إشعاع الخلفية الكونية الميكروي (CMB) الذي نرصده اليوم.",
    evidence: "تقارن وفرة النظائر الخفيفة المرصودة بحسابات التفاعلات النووية؛ وطيف CMB قريب للغاية من طيف الجسم الأسود، مع لا تجانس صغير يرسم بذور البنية الكونية. اتفاق BBN وCMB اختبار مستقل قوي، مع بقاء توتر الليثيوم مشكلة مفتوحة.",
    test: "انحرافات موثقة في وفرة نظائر متعددة أو في شكل طيف CMB، لا تفسرها أخطاء القياس أو الفيزياء المعروفة، ستضعف النموذج. مشكلة الليثيوم مثال على موضع اختبار وتوتر يجب إظهاره لا إخفاؤه.",
    papers: [["Penzias & Wilson (1965) — قياس حرارة الخلفية، ApJ", "https://doi.org/10.1086/148307"], ["Coc & Vangioni (2017) — التخليق النووي البدائي", "https://doi.org/10.1142/S0218301317410026"], ["Planck Collaboration (2020) — قيود النموذج الكوني", "https://doi.org/10.1051/0004-6361/201833880"]],
    image: ["خرائط الخلفية الكونية · NASA/ESA", "https://imagine.gsfc.nasa.gov/educators/programs/cosmictimes/universe_mashup/archive/complete_archive.html"],
    media: ["مرئيات الخلفية وتاريخ رصدها · NASA", "https://map.gsfc.nasa.gov/"],
    sim: ["استكشاف بيانات الخلفية الكونية · NASA LAMBDA", "https://lambda.gsfc.nasa.gov/"],
    date: "نحو 3 دقائق: التخليق البدائي · 380 ألف سنة: انطلاق CMB"
  },
  {
    n: "03", era: "بعد مئات ملايين السنين من البداية", topic: "البُنى", tone: "cyan",
    title: "من سحب الغاز إلى النجوم والمجرات",
    summary: "تجذب الجاذبية الغاز والمادة المظلمة إلى مناطق أكثف؛ تتكوّن النجوم الأولى، ثم تتجمع النجوم والغاز في مجرات تتطور عبر الاندماج والتغذية الراجعة. التلسكوبات العميقة ترصد ضوء مجرات مبكرة كما انطلق قديماً.",
    evidence: "تُختبر النماذج عبر إحصاءات المجرات والانزياح الأحمر والعدسات وخصائص الغاز. صور JWST مشاهدات للضوء، أما أفلام تطور المجرات فهي محاكاة بيانات وليست تصويراً متصلاً لمليارات السنين.",
    test: "تُراجع المحاكاة إذا أخفقت على نحو منهجي في إعادة إنتاج أحجام المجرات وألوانها وكتلها ومعدلات تكوّن النجوم وتطورها. صورة منفردة لا تكفي؛ المهم اختبارات كمية متعددة.",
    papers: [["Planck Collaboration (2020) — النموذج الكوني وقيود البنية", "https://doi.org/10.1051/0004-6361/201833880"], ["Springel et al. (2005) — محاكاة تشكّل المجرات وتطورها، Nature", "https://doi.org/10.1038/nature03597"]],
    image: ["خط زمني للمجرات البعيدة · NASA/ESA", "https://science.nasa.gov/asset/hubble/universe-timeline/"],
    media: ["مرئيات تجميع مجرة شبيهة بدرب التبانة · NASA/JWST", "https://svs.gsfc.nasa.gov/gallery/jwst/"],
    sim: ["تطور الكون والمجرات · NASA SVS", "https://svs.gsfc.nasa.gov/10656/"],
    date: "من مئات ملايين السنين الأولى إلى المجرات المعاصرة"
  },
  {
    n: "04", era: "أجيال نجمية عبر مليارات السنين", topic: "العناصر", tone: "amber",
    title: "أفران النجوم: العناصر التي ستصنع الكواكب",
    summary: "تدمج النجوم عناصر خفيفة بتفاعلات نووية؛ وتنتج النجوم المتطورة والانفجارات عناصر أثقل. وتؤكد رصود اندماج النجوم النيوترونية أن البيئات الكونية القصوى تصنع بعض العناصر الثقيلة بعملية التقاط النيوترونات السريع.",
    evidence: "تُقاس البصمات الطيفية للعناصر في النجوم والسدم وتُقارن بوفرتها في النيازك والأرض. في GW170817 ارتبطت موجات الجاذبية بإشعاع كيلونوفا؛ قدم ذلك اختباراً متعدد الرسل لدور الاندماج في التخليق النووي، لكنه لا يحسم وحده مساهمة كل مصدر لكل عنصر.",
    test: "تتطلب الفرضيات اتساق أطياف النجوم والمستعرات والكيلونوفا مع وفرة العناصر ونظائرها. غياب السمات المتوقعة أو اختلاف المردود المقاس يقيد المساهمات ويجبر النماذج على التحديث.",
    papers: [["Burbidge et al. (1957) — تخليق العناصر في النجوم", "https://doi.org/10.1103/RevModPhys.29.547"], ["Kasen et al. (2017) — العناصر الثقيلة في اندماج نجمي نيوتروني، Nature", "https://doi.org/10.1038/nature24453"], ["Drout et al. (2017) — منحنيات ضوء GW170817", "https://doi.org/10.1126/science.aaq0049"]],
    image: ["صور حدث GW170817 متعدد الرسل · LIGO", "https://www.ligo.caltech.edu/page/press-release-gw170817"],
    media: ["محاكاة تطور المستعر الأعظم 1987A · NASA/ESA", "https://svs.gsfc.nasa.gov/30863/"],
    sim: ["شرح أطياف الأشعة السينية والعناصر · NASA", "https://imagine.gsfc.nasa.gov/educators/lessons/xray_spectra/"],
    date: "أجيال نجمية سبقت تشكّل الشمس؛ للعناصر تاريخ كوني سابق"
  },
  {
    n: "05", era: "قبل نحو 4.6–4.5 مليار سنة", topic: "الكواكب", tone: "orange",
    title: "سحابة شمسية، قرص كوكبي، وأرض فتية",
    summary: "انهارت سحابة جزيئية مخصّبة بعناصر أجيال نجمية سابقة، وتكوّنت الشمس داخل قرص دوار من الغاز والغبار. تراكمت حبيبات القرص إلى أجسام أكبر ثم كواكب. ترصد ALMA أقراصاً حول نجوم فتية، وتؤرخ النيازك أقدم مواد نظامنا.",
    evidence: "تظهر صور الأقراص حلقات وفجوات متوافقة مع تفاعل الكواكب الناشئة والقرص، لكنها لا تثبت بمفردها وجود كوكب بعينه. وتكشف النيازك والتأريخ النظائري أعماراً مبكرة. المحاكاة تقارن تنبؤاتها ببنى الأقراص ومدارات الكواكب.",
    test: "تتغير تفاصيل النماذج إذا لم تفسر الأعمار النظائرية وكيمياء النيازك وبنية الأقراص والمدارات وتنوع الكواكب. فجوة قرص منفردة قد تنتج من آليات مختلفة.",
    papers: [["ALMA Partnership (2015) — قرص HL Tau عالي الدقة", "https://doi.org/10.1088/2041-8205/808/1/L3"], ["Andrews (2020) — أقراص تشكّل الكواكب: مراجعة", "https://doi.org/10.1146/annurev-astro-031220-010302"]],
    image: ["صورة قرص HL Tau · ESO/ALMA", "https://www.eso.org/public/images/eso1436a/"],
    media: ["كيف تولد الكواكب؟ · NASA SVS", "https://svs.gsfc.nasa.gov/12278/"],
    sim: ["جولة قرص كوكبي وولادة نظام شمسي · NASA", "https://science.nasa.gov/resource/protoplanetary-disk/"],
    date: "الشمس والنظام الشمسي: نحو 4.6 مليار سنة · الأرض: نحو 4.54 مليار سنة"
  },
  {
    n: "06", era: "بعد تشكّل الأرض وقبل أقدم سجل حياة محفوظ", topic: "الكيمياء", tone: "green",
    title: "على الأرض الفتية: كيمياء قبل الأحياء",
    summary: "تُظهر التجارب أن بعض لبنات الجزيئات الحيوية يمكن أن تتكوّن من مواد أبسط بوجود مصادر طاقة. تجربة ميلر–يوري برهنت إمكان تصنيع أحماض أمينية ضمن شروطها المختبرية الخاصة؛ لم تُنشئ خلية ولم تثبت أن الغلاف الجوي البدائي كان مطابقاً للخليط المستخدم.",
    evidence: "يختبر الباحثون تفاعلات في بيئات محتملة—برك، أسطح معدنية، فتحات مائية حرارية وغيرها—ويقيسون النواتج والشروط. موقع البداية ومسارات تكوين البوليمرات والوراثة والغشاء ما تزال موضوع بحث؛ لا توجد رواية مكتملة مثبتة لنشأة الحياة.",
    test: "كل مسار مقترح عليه تحديد مركبات أولية وطاقة وظروف جيولوجية قابلة للاختبار، ثم إنتاج نواتج متوقعة بانتقائية معقولة. فشل التجارب المضبوطة أو عدم اتساق الشروط مع الأرض المبكرة يضعف المسار بعينه.",
    papers: [["Miller (1953) — إنتاج أحماض أمينية في شروط بدائية محتملة", "https://doi.org/10.1126/science.117.3046.528"], ["Sutherland (2009) — تخليق مكونات RNA في ظروف أرضية بدائية", "https://doi.org/10.1038/nature08013"], ["Patel et al. (2015) — شبكات كيمياء ما قبل الحياة", "https://doi.org/10.1038/nchem.2202"]],
    image: ["رسم توضيحي لتجربة ميلر–يوري · Beloit College", "https://chemistry.beloit.edu/Origins/pages/spark.html"],
    media: ["إعادة فعلية مسرّعة لتجربة التفريغ الكهربائي · Beloit College", "https://chemistry.beloit.edu/Origins/pages/spark.html"],
    sim: ["محاكاة تفاعلية لتجربة ميلر–يوري · Carleton College", "https://serc.carleton.edu/marsforearthlings/examples/miller_urey_experiment_Mars.html"],
    date: "قبل أقدم دليل جيولوجي واضح على الحياة؛ تاريخ البداية غير معروف"
  },
  {
    n: "07", era: "الحياة موجودة قبل 3.5 مليار سنة على الأقل", topic: "الحياة", tone: "teal",
    title: "من الكيمياء إلى الحياة: الدليل أوضح من الآلية",
    summary: "تُظهر الصخور القديمة أن حياة ميكروبية كانت موجودة منذ مليارات السنين؛ لكن الانتقال من كيمياء غير حية إلى أول نظام حي لم يُشاهد مباشرة وما تزال آليته غير محسومة. فرضية عالم RNA مسار بحثي مؤثر، لا حقيقة نهائية مكتملة.",
    evidence: "تجمع الأدلة بين بنى شبيهة بالستروماتوليت وأنسجة مجهرية وسياق جيوكيميائي ونظائري. ادعاءات أقدم، مثل بعض صخور غرينلاند، محل نقاش بسبب التشوه والتحول؛ رواسب Dresser الأسترالية (~3.48 مليار سنة) من أقوى شواهد الحياة المبكرة، مع اختبار البصمات الحيوية مقابل بدائل غير حيوية.",
    test: "تُختبر دعوى البصمة الحيوية بسياق جيولوجي مؤرخ وبنى أو أنماط كيميائية متوافقة مع الحياة وباستبعاد بدائل لاأحيائية. وفرضية منشأ محددة تحتاج تجارب تعيد بناء خطواتها وتنبؤات تميزها عن المنافسين.",
    papers: [["Gilbert (1986) — فرضية عالم RNA، Nature", "https://doi.org/10.1038/319618a0"], ["Allwood et al. (2006) — ستروماتوليتات قديمة من Pilbara", "https://doi.org/10.1038/nature04764"], ["Djokic et al. (2017) — دلائل حياة في ينابيع حارة قديمة", "https://doi.org/10.1038/ncomms15263"]],
    image: ["صور وشرح رواسب Dresser وبصمات الحياة", "https://www.nature.com/articles/ncomms15263"],
    media: ["قصة مصوّرة عن كيمياء ما قبل الحياة · NASA Astrobiology", "https://astrobiology.nasa.gov/uploads/filer_public/e2/24/e2247808-b5c6-4e49-b2f0-4ce9c89fc43b/issue7_mobile.pdf"],
    sim: ["موارد تعليمية عن أصل الحياة · NASA Astrobiology", "https://astrobiology.nasa.gov/education/alp/where-lifes-building-blocks-come-from/"],
    date: "على الأقل قبل 3.5 مليار سنة؛ لا نعرف بدقة متى وكيف حدثت الخطوة الأولى"
  },
  {
    n: "08", era: "من أقدم حياة إلى الحاضر", topic: "التطور", tone: "lime",
    title: "التطور: تغير الجماعات وتفرّع شجرة الحياة",
    summary: "التطور البيولوجي هو تغير صفات موروثة في جماعات عبر الأجيال. الطفرات وإعادة التركيب تولدان تنوعاً؛ والانتقاء الطبيعي والانحراف الوراثي وتدفق الجينات تغيّر تواترات المتغيرات. تراكم التفرع يفسر أنماط القرابة والتنوع.",
    evidence: "تتلاقى أدلة مستقلة: أحافير مرتبة زمنياً، تشابهات تشريحية وجزيئية، جينومات وشجرات قرابة، توزيع جغرافي، ورصد مباشر للتغير والتكيف. التطور لا يعني أن الأفراد يتغيرون عبر حياتهم، ولا أن كل سلالة تسير نحو غاية أو تعقيد أعلى.",
    test: "تنبؤات الشجرة الوراثية والتأريخ الطبقي والوراثة قابلة للفحص. أحفورة موثقة في طبقة أقدم على نحو لا يمكن تفسيره أو تناقض جينومي متكرر سيجبر النماذج التاريخية على المراجعة. تجارب التطور تقيس تغيرات متوقعة في الزمن الحقيقي.",
    papers: [["Darwin (1859) — الطبعة الأولى من أصل الأنواع، مصدر تاريخي أولي", "https://www.biodiversitylibrary.org/item/135954"], ["Lenski et al. (1991) — تطور E. coli عبر 2000 جيل", "https://doi.org/10.1086/285289"], ["Lenski & Travisano (1994) — التكيف والتمايز عبر 10,000 جيل", "https://doi.org/10.1073/pnas.91.15.6808"]],
    image: ["شجرة الحياة التفاعلية · OneZoom", "https://www.onezoom.org/"],
    media: ["محاكاة تطور الفأر الصخري بالانتقاء · HHMI", "https://www.hhmi.org/biointeractive/simulating-evolution-rock-pocket-mouse-population"],
    sim: ["تفاعل تغيّر جماعة فأر صخري عبر الأجيال · HHMI", "https://www.hhmi.org/biointeractive/simulating-evolution-rock-pocket-mouse-population"],
    date: "تفرّع متواصل منذ الحياة المبكرة؛ تغيرات مرصودة خلال أجيال بشرية"
  },
  {
    n: "09", era: "التطور مستمر الآن؛ الإنسان العاقل ~300 ألف سنة", topic: "التحقق", tone: "rose",
    title: "اختبارات اليوم: من المختبر إلى شجرة القرابة",
    summary: "تُختبر نظرية التطور اليوم ببيانات الجينوم والتجارب والمشاهدات والسجل الأحفوري. الإنسان فرع حديث من شجرة الحياة وله أسلاف مشتركون مع سائر الرئيسيات؛ لم ينحدر من القردة المعاصرة.",
    evidence: "تسجل تجربة Lenski تغيرات وراثية وتكيفاً في جماعات بكتيرية محفوظة الأجيال. وتُقارن شجرات الجينات بصفات الكائنات والسجل الجيولوجي. تاريخ الإنسان مبني من عينات أحفورية وجزيئية، وتواريخه تقريبية تتغير مع الاكتشافات.",
    test: "يُختبر كل استنتاج محدد: أثر طفرة في اللياقة، أو صلة قرابة متوقعة في الجينوم، أو توقّع زمني لأحفورة. النتائج السلبية أو التعارض تعدّل الفروع والتواريخ والآليات؛ لا يعتمد الإطار كله على ادعاء منفرد.",
    papers: [["Good et al. (2017) — التطور الجزيئي عبر 60 ألف جيل", "https://doi.org/10.1038/nature24287"], ["Lenski (2017) — التكيف بالانتقاء الطبيعي، PLOS Genetics", "https://doi.org/10.1371/journal.pgen.1006668"], ["Hublin et al. (2017) — حفريات Homo sapiens من جبل إيغود، المغرب", "https://doi.org/10.1038/nature22336"]],
    image: ["شجرة الحياة التفاعلية · OneZoom", "https://www.onezoom.org/"],
    media: ["تجربة التطور طويلة الأمد · HHMI", "https://www.hhmi.org/biointeractive/evolution-constant-change-and-common-threads"],
    sim: ["محاكاة أثر الطفرات والانتقاء · HHMI", "https://www.hhmi.org/biointeractive/simulating-evolution-rock-pocket-mouse-population"],
    date: "الإنسان العاقل ظهر قبل نحو 300 ألف سنة؛ التطور البيولوجي مستمر"
  }
];

function ResourceLink({ label, href, kind }: { label: string; href: string; kind: string }) {
  return <a className="resource-link" href={href} target="_blank" rel="noreferrer"><span className="resource-kind">{kind}</span><span>{label}</span><span className="arrow">↗</span></a>;
}

export default function Home() {
  return (
    <main dir="rtl">
      <header className="topbar"><a href="#top" className="brand"><span className="brand-mark">م</span><span>مدار <i>·</i> أطلس الدليل</span></a><a className="top-link" href="https://drive.google.com/drive/folders/1l1BFAthMXtRTBsxT4q3rH1tGrbpo5rDA" target="_blank" rel="noreferrer">مكتبة Drive <span>↗</span></a></header>
      <section className="hero" id="top">
        <div className="hero-stars" aria-hidden="true"><span/><span/><span/><span/><span/><span/><span/><span/></div>
        <div className="hero-inner">
          <div className="eyebrow"><span className="live-dot"/> خريطة زمنية للأدلة العلمية <span className="eyebrow-date">نسخة 2026</span></div>
          <h1>من أقدم كونٍ<br/><em>نرصده، إلى الحياة.</em></h1>
          <p className="hero-copy">مسار بحثي واحد، من التمدد الكوني إلى تنوّع الأحياء. أوراق محكّمة، مشاهدات، محاكاة، وأسئلة تُبيّن ما نعرفه وما لا نعرفه بعد.</p>
          <a className="begin-button" href="#chapter-01">ابدئي الرحلة <span>↓</span></a>
          <div className="hero-meta"><span>09 محطات زمنية</span><span className="meta-divider"/><span>الأقدم ← الأحدث</span><span className="meta-divider"/><span>مصادر أولية ومؤسسية</span></div>
        </div>
        <div className="hero-orbit orbit-one"/><div className="hero-orbit orbit-two"/><div className="hero-sun"/>
        <div className="hero-caption">مخطط تصوري — لا مقياس مكاني</div>
      </section>

      <section className="orientation" id="method">
        <div className="section-kicker">قبل البداية <span>01 / 02</span></div>
        <div className="orientation-grid">
          <div><h2>الدليل ليس<br/><em>تسليماً مسبقاً.</em></h2><p>اقرئي كل محطة بهذا الترتيب: الادعاء، ما يدعمه رصدياً، ثم ما الذي قد يضعفه. قوة الدليل لا تعني أن كل تفصيل محسوم؛ والجزء المفتوح لا يمحو ما اختُبر فعلاً.</p></div>
          <div className="caution-card"><div className="caution-icon">i</div><div><h3>حدّان يستحقان الوضوح</h3><p><b>الانفجار العظيم:</b> وصف لتطور الكون المبكر؛ لا نملك رصداً مباشراً للحظة صفر ولا نظرية مكتملة لما قبل حد الفيزياء المعروفة.</p><p><b>نشأة الحياة:</b> ليست هي التطور. الأدلة على الحياة القديمة قوية، أما آلية الانتقال الأولى من الكيمياء إلى الحياة فما تزال غير محسومة.</p></div></div>
        </div>
        <div className="progress-strip"><span>التسلسل الزمني</span><div className="progress-line"><i/></div><span>09 مراحل · من الأقدم إلى الأحدث</span></div>
      </section>

      <section className="timeline" aria-label="التسلسل الزمني للمراحل">
        {chapters.map((c, idx) => (
          <article className={`chapter tone-${c.tone}`} id={`chapter-${c.n}`} key={c.n}>
            <div className="rail"><span className="rail-dot">{c.n}</span>{idx < chapters.length - 1 && <span className="rail-line"/>}</div>
            <div className="chapter-body">
              <div className="chapter-head"><div><div className="chapter-label"><span className="chapter-topic">{c.topic}</span><span className="chapter-time">{c.era}</span></div><h2>{c.title}</h2></div><span className="chapter-number">{c.n}</span></div>
              <p className="chapter-summary">{c.summary}</p>
              <div className="evidence-grid"><div className="evidence-box"><span className="box-label"><i className="mini-dot"/> ما الذي نرصده؟</span><p>{c.evidence}</p></div><div className="test-box"><span className="box-label"><i className="test-icon">?</i> ما الذي قد يضعفه؟</span><p>{c.test}</p></div></div>
              <div className="time-note"><span className="time-icon">◷</span><span>{c.date}</span></div>
              <div className="resources"><div className="resource-head"><span>مواد للاستكشاف</span><span>أبحاث · صور · مرئيات</span></div><div className="resource-columns"><div className="paper-list"><span className="resource-heading">أوراق ومصادر أولية</span>{c.papers.map(([label, href]) => <ResourceLink key={href} label={label} href={href} kind="ورقة"/>)}</div><div className="media-list"><span className="resource-heading">صور ومرئيات</span><ResourceLink label={c.image[0]} href={c.image[1]} kind="صورة"/><ResourceLink label={c.media[0]} href={c.media[1]} kind="فيديو"/><ResourceLink label={c.sim[0]} href={c.sim[1]} kind="محاكاة"/></div></div></div>
            </div>
          </article>
        ))}
      </section>

      <section className="closing"><div className="closing-index">نهاية المسار <span>09 / 09</span></div><div className="closing-content"><div className="closing-symbol">✳</div><div><h2>المعرفة تتقدم<br/><em>حين تُختبر.</em></h2><p>هذا الخط الزمني إطار للمراجعة، لا كلمة أخيرة. عودي إلى المنهج والبيانات في كل ورقة، وميّزي بين نتيجة مقاسة وتفسيرها، وبين نموذج راسخ وتفصيل ما زال قيد البحث.</p><a href="#top">العودة إلى البداية ↑</a></div></div></section>
      <footer><span>مدار · أطلس الدليل العلمي</span><span>أُعدّ كمسار قراءة بحثي عربي · أكتوبر 2026</span><a href="https://doi.org/" target="_blank" rel="noreferrer">الروابط إلى المصادر الأصلية ↗</a></footer>
    </main>
  );
}
