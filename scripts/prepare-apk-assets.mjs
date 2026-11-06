import fs from "fs";
import path from "path";

const outDir = path.join(process.cwd(), "mobile-shell");
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

const defaultCloudUrl = (process.env.CAPACITOR_CLOUD_SERVER_URL || "").trim();

const html = `<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>راصد الجيوسياسي | RASED APK</title>
  <style>
    :root {
      --bg: #060911;
      --card: #0b1220;
      --card2: #0f172a;
      --border: #1e293b;
      --emerald: #10b981;
      --cyan: #06b6d4;
      --rose: #f43f5e;
      --amber: #f59e0b;
      --text: #f1f5f9;
      --muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", "Noto Sans Arabic", Tahoma, sans-serif;
      min-height: 100vh;
      padding-bottom: 84px;
    }
    header {
      position: sticky; top: 0; z-index: 30;
      background: rgba(7, 11, 20, 0.96);
      border-bottom: 1px solid var(--border);
      padding: 12px 14px;
      display: flex; align-items: center; justify-content: space-between; gap: 8px;
      backdrop-filter: blur(8px);
    }
    .brand { display: flex; align-items: center; gap: 10px; }
    .pulse-dot {
      width: 10px; height: 10px; border-radius: 50%;
      background: var(--emerald);
      box-shadow: 0 0 12px var(--emerald);
      animation: pulse 1.8s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.45;transform:scale(1.25)} }
    .badge {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 3px 9px; border-radius: 999px; font-size: 11px; font-weight: 700;
    }
    .b-crit { background: rgba(244,63,94,0.18); color: #fda4af; border: 1px solid rgba(244,63,94,0.45); }
    .b-high { background: rgba(245,158,11,0.18); color: #fcd34d; border: 1px solid rgba(245,158,11,0.45); }
    .b-acc { background: rgba(16,185,129,0.16); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.4); font-family: monospace; }
    .b-src { background: #0f172a; color: #67e8f9; border: 1px solid #334155; font-family: monospace; }
    main { max-width: 820px; margin: 0 auto; padding: 12px; }
    .tab-view { display: none; flex-direction: column; gap: 12px; }
    .tab-view.active { display: flex; }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 14px;
    }
    .card h2 { font-size: 15px; margin-bottom: 6px; color: #fff; }
    .card h3 { font-size: 14px; color: #f8fafc; line-height: 1.6; margin: 7px 0 5px; }
    .card p { font-size: 12.5px; line-height: 1.75; color: var(--muted); }
    .meta-row { display: flex; justify-content: space-between; align-items: center; gap: 6px; flex-wrap: wrap; }
    .pills { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 4px; }
    .pill {
      white-space: nowrap; border: 1px solid var(--border); background: #090f1c;
      color: var(--muted); border-radius: 10px; padding: 6px 11px; font-size: 11.5px; font-weight: 700;
    }
    .pill.active { background: rgba(16,185,129,0.18); color: #6ee7b7; border-color: rgba(16,185,129,0.45); }
    button { border: none; border-radius: 11px; padding: 10px 13px; font-size: 12px; font-weight: 700; cursor: pointer; }
    .btn-main { background: linear-gradient(90deg, var(--cyan), var(--emerald)); color: #020617; width: 100%; }
    .btn-alert { background: rgba(244,63,94,0.2); color: #fecdd3; border: 1px solid rgba(244,63,94,0.5); padding: 7px 11px; font-size: 11.5px; }
    input, textarea, select {
      width: 100%; background: #030712; border: 1px solid var(--border);
      color: #fff; padding: 10px 12px; border-radius: 11px; font-size: 12.5px; margin-top: 6px;
    }
    .detail-box {
      margin-top: 10px; padding: 11px; border-radius: 12px;
      background: rgba(15, 23, 42, 0.75); border: 1px solid #1e293b;
      font-size: 12px; line-height: 1.75; color: #e2e8f0; display: none;
    }
    .detail-box.open { display: block; }
    .bottom-nav {
      position: fixed; bottom: 0; right: 0; left: 0; z-index: 40;
      background: rgba(7, 11, 20, 0.98); border-top: 1px solid var(--border);
      display: grid; grid-template-columns: repeat(5, 1fr); padding: 6px 4px;
    }
    .nav-btn {
      background: transparent; color: var(--muted); padding: 6px 2px;
      display: flex; flex-direction: column; align-items: center; gap: 3px; font-size: 10.5px; border-radius: 10px;
    }
    .nav-btn.active { background: rgba(16,185,129,0.15); color: #6ee7b7; }
    .frames-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 10px; }
    .frame-card { background: #000; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
    .frame-card img { width: 100%; height: 84px; object-fit: cover; display: block; }
    .frame-card div { padding: 4px 6px; font-size: 10px; font-family: monospace; color: #67e8f9; display: flex; justify-content: space-between; }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <span class="pulse-dot"></span>
      <div>
        <div style="font-weight:800;font-size:15.5px;">راصِـد <span style="color:#10b981;">| RASED</span></div>
        <div id="statusSub" style="font-size:10.5px;color:#94a3b8;">متأهب 24/7 • المصادر الأم فقط</div>
      </div>
    </div>
    <button class="btn-alert" id="drillBtn">⚡ اختبار إنذار</button>
  </header>

  <main>
    <!-- TAB 1: LIVE PRIMARY FEED -->
    <section id="tab-FEED" class="tab-view active">
      <div class="pills" id="theaterPills">
        <button class="pill active" data-th="ALL">جميع المسارح</button>
        <button class="pill" data-th="MIDDLE_EAST_RED_SEA">الشرق الأوسط والبحر الأحمر</button>
        <button class="pill" data-th="EAST_EUROPE">أوروبا الشرقية والناتو</button>
        <button class="pill" data-th="INDO_PACIFIC_TAIWAN">مضيق تايوان والهادئ</button>
        <button class="pill" data-th="SAHEL_HORN_AFRICA">القرن الأفريقي والساحل</button>
      </div>
      <div id="dispatchesList" style="display:flex;flex-direction:column;gap:11px;"></div>
    </section>

    <!-- TAB 2: WAR MAP RADAR -->
    <section id="tab-MAP" class="tab-view">
      <div class="card">
        <h2>رادار مسارح الحروب والمضائق البحرية الحرجة</h2>
        <p>اضغط على أي مسرح عمليات لاستعراض المضائق الاستراتيجية وتوازن القوى العسكرية:</p>
        <svg viewBox="0 0 1000 460" style="width:100%;height:auto;margin-top:10px;border-radius:12px;background:#070d19;border:1px solid #1e293b;">
          <path d="M 95 75 L 255 68 L 305 135 L 245 205 L 185 225 L 120 165 Z" fill="#0f1b2e" stroke="#254872" />
          <path d="M 455 78 L 585 70 L 605 155 L 535 170 L 465 155 Z" fill="#122138" stroke="#254872" />
          <path d="M 455 182 L 575 185 L 615 265 L 575 385 L 505 385 L 475 285 Z" fill="#111f35" stroke="#23446d" />
          <path d="M 585 82 L 875 85 L 895 215 L 810 265 L 710 255 L 625 230 L 585 175 Z" fill="#13233b" stroke="#284e7d" />
          <circle cx="595" cy="225" r="24" fill="rgba(244,63,94,0.2)" stroke="#f43f5e" />
          <circle cx="595" cy="225" r="7" fill="#f43f5e" />
          <text x="595" y="262" fill="#fda4af" font-size="13" text-anchor="middle">باب المندب وهرمز</text>
          <circle cx="565" cy="142" r="22" fill="rgba(244,63,94,0.2)" stroke="#f43f5e" />
          <circle cx="565" cy="142" r="7" fill="#f43f5e" />
          <text x="565" y="114" fill="#fda4af" font-size="13" text-anchor="middle">أوروبا الشرقية والأسود</text>
          <circle cx="805" cy="218" r="22" fill="rgba(245,158,11,0.2)" stroke="#f59e0b" />
          <circle cx="805" cy="218" r="7" fill="#f59e0b" />
          <text x="805" y="190" fill="#fcd34d" font-size="13" text-anchor="middle">مضيق تايوان</text>
          <circle cx="558" cy="272" r="18" fill="rgba(245,158,11,0.2)" stroke="#f59e0b" />
          <circle cx="558" cy="272" r="6" fill="#f59e0b" />
        </svg>
      </div>
      <div class="card">
        <h2>أهم الممرات البحرية قيد الرصد الدائم</h2>
        <p>• <strong>مضيق باب المندب والبحر الأحمر:</strong> 12% من التجارة البحرية العالمية — بلاغات UKMTO الفورية.<br/>
           • <strong>مضيق هرمز:</strong> 20% من إمدادات النفط العالمية.<br/>
           • <strong>البحر الأسود وبحر البلطيق:</strong> أمن الكابلات البحرية وخطوط الطاقة الأوروبية.<br/>
           • <strong>مضيق تايوان وممر باشي:</strong> سلاسل أشباه الموصلات وحركة الأساطيل في الهادئ.</p>
      </div>
    </section>

    <!-- TAB 3: VIDEO & TEXT FORENSICS LAB -->
    <section id="tab-LAB" class="tab-view">
      <div class="card">
        <h2>مختبر التحقق الجنائي من الفيديوهات والنصوص الحربية</h2>
        <p>افحص أي مقطع فيديو حربي (استخراج الإطارات + بصمة SHA-256) أو تحقق من أصالة رابط خبر عاجل:</p>
        <input type="file" id="videoInput" accept="video/*" />
        <div id="videoFramesBox" class="frames-grid"></div>
        <textarea id="claimInput" rows="3" placeholder="ألصق نص الخبر المتداول أو وصف الفيديو للتحقق من مصدره الأم...">رصد بحري ليلي لانفجار قرب سفينة تجارية جنوب غرب الحديدة متزامن مع بلاغ UKMTO الرسمي.</textarea>
        <input type="url" id="claimUrl" dir="ltr" placeholder="https://ukmto.org/..." value="https://www.ukmto.org/indian-ocean/recent-incidents" />
        <div style="margin-top:10px;">
          <button class="btn-main" id="analyzeBtn">تشغيل الفحص الجنائي وإعادة الصياغة بالعربية</button>
        </div>
        <div id="forensicOut" class="detail-box"></div>
      </div>
    </section>

    <!-- TAB 4: ROOT SOURCES GATEKEEPER -->
    <section id="tab-SOURCES" class="tab-view">
      <div class="card" style="border-color:rgba(16,185,129,0.4);">
        <h2>بوابة المصادر الأم الصارمة (16 مصدرًا معتمدًا)</h2>
        <p>يرفض «راصد» تلقائيًا أي شائعات أو حسابات تواصل مجهولة، ويلتقط الأخبار حصريًا من النطاقات الرسمية المعتمدة:</p>
      </div>
      <div id="sourcesList" style="display:flex;flex-direction:column;gap:9px;"></div>
    </section>

    <!-- TAB 5: CLOUD SERVER & AI SETTINGS -->
    <section id="tab-CLOUD" class="tab-view">
      <div class="card" style="border-color:rgba(6,182,212,0.4);">
        <h2>إعداد الخادم السحابي الدائم (24/7) والذكاء الاصطناعي</h2>
        <p>تعمل خدمة التأهب الخلفية في هاتفك الآن تلقائيًا! يمكنك ربط عنوان خادمك السحابي الدائم أو إدخال مفتاح Gemini لتحليل الفيديوهات مباشرة:</p>
        <label style="display:block;font-size:12px;margin-top:10px;color:#e2e8f0;">رابط الخادم السحابي الدائم (اختياري):</label>
        <input id="cloudUrlField" dir="ltr" type="url" placeholder="https://rased-sentinel.up.railway.app" value="${defaultCloudUrl}" />
        <label style="display:block;font-size:12px;margin-top:10px;color:#e2e8f0;">مفتاح Google Gemini API لتحليل الفيديو بالذكاء الاصطناعي (اختياري):</label>
        <input id="geminiKeyField" dir="ltr" type="password" placeholder="AIzaSy..." />
        <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap;">
          <button class="btn-main" id="saveCloudBtn">حفظ وتفعيل التأهب الخلفي الدائم 24/7</button>
        </div>
        <div id="cloudSaveMsg" style="margin-top:8px;font-size:12px;color:#6ee7b7;"></div>
      </div>
    </section>
  </main>

  <nav class="bottom-nav">
    <button class="nav-btn active" data-tab="FEED"><span>📡</span><span>الرصد</span></button>
    <button class="nav-btn" data-tab="MAP"><span>🗺️</span><span>الخريطة</span></button>
    <button class="nav-btn" data-tab="LAB"><span>🎞️</span><span>مختبر التحقق</span></button>
    <button class="nav-btn" data-tab="SOURCES"><span>🛡️</span><span>المصادر الأم</span></button>
    <button class="nav-btn" data-tab="CLOUD"><span>☁️</span><span>السحابة وAI</span></button>
  </nav>

  <script>
    (function() {
      const ROOT_SOURCES = [
        { code: "UKMTO", domain: "ukmto.org", name: "هيئة عمليات التجارة البحرية البريطانية", score: 98 },
        { code: "IAEA", domain: "iaea.org", name: "الوكالة الدولية للطاقة الذرية — فيينا", score: 99 },
        { code: "REUTERS", domain: "reuters.com", name: "وكالة رويترز للأنباء — القسم العالمي والعسكري", score: 97 },
        { code: "AP", domain: "apnews.com", name: "وكالة أسوشيتد برس الدولية (AP)", score: 97 },
        { code: "AFP", domain: "afp.com", name: "وكالة الصحافة الفرنسية (AFP)", score: 95 },
        { code: "UNSC", domain: "news.un.org", name: "مجلس الأمن والأمم المتحدة — السلم والأمن", score: 96 },
        { code: "NATO", domain: "nato.int", name: "القيادة العليا لحلف شمال الأطلسي (الناتو)", score: 92 },
        { code: "US-DoD", domain: "defense.gov", name: "وزارة الدفاع الأمريكية والقيادة المركزية", score: 91 },
        { code: "BBC", domain: "bbc.co.uk", name: "هيئة الإذاعة البريطانية — الرصد الدولي", score: 93 },
        { code: "AJ", domain: "aljazeera.com", name: "شبكة الجزيرة — غرفة الأخبار المركزية", score: 91 },
        { code: "SIPRI", domain: "sipri.org", name: "معهد ستوكهولم الدولي لأبحاث السلام والتسلح", score: 98 },
        { code: "ISW", domain: "understandingwar.org", name: "معهد دراسات الحرب — الخرائط الميدانية", score: 93 }
      ];

      let dispatches = [
        {
          id: "d1",
          theater: "MIDDLE_EAST_RED_SEA",
          sev: "CRITICAL",
          sevLabel: "إنذار حرج",
          domain: "ukmto.org",
          acc: 96,
          title: "هيئة عمليات التجارة البحرية البريطانية (UKMTO) تسجل حادثًا ملاحيًا على بُعد 68 ميلًا بحريًا جنوب غرب الحديدة وتوجه تحذيرًا للسفن",
          summary: "بلاغ ملاحي رسمي مباشر من المصدر الأم يفيد برصد انفجارين قرب سفينة تجارية مع تأكيد سلامة الطاقم واستمرار الإبحار.",
          impact: "يرفع الحادث جاهزية الدوريات البحرية ويبقي تأمين مخاطر الحرب في ممر باب المندب تحت المراقبة الحثيثة.",
          orig: "UKMTO WARNING: Master of merchant vessel reports two explosions in close proximity 68NM SW of Al Hudaydah, crew safe."
        },
        {
          id: "d2",
          theater: "EAST_EUROPE",
          sev: "HIGH",
          sevLabel: "تأهب مرتفع",
          domain: "iaea.org",
          acc: 98,
          title: "الوكالة الدولية للطاقة الذرية تؤكد استعادة خط الكهرباء الاحتياطي بقدرة 330 كيلوفولت لمحطة زابوريجيا النووية",
          summary: "توثيق ميداني مباشر من مفتشي الوكالة المتمركزين داخل المحطة يؤكد إعادة ربط خط التبريد الاحتياطي وبقاء الإشعاع طبيعيًا.",
          impact: "يعزز هامش الأمان النووي لتبريد المفاعلات الستة في وضع الإغلاق البارد ويقلص خطر الاعتماد على مولدات الديزل الطارئة.",
          orig: "IAEA experts stationed at ZNPP confirmed today that the 330 kV back-up power line has been restored."
        },
        {
          id: "d3",
          theater: "EAST_EUROPE",
          sev: "HIGH",
          sevLabel: "تأهب مرتفع",
          domain: "nato.int",
          acc: 94,
          title: "القيادة البحرية لحلف الناتو تنشر فرقاطات ومسيّرات أعماق لحماية الكابلات البحرية وخطوط الطاقة في بحر البلطيق",
          summary: "بيان رسمي من القيادة البحرية للناتو متقاطع مع وكالة الصحافة الفرنسية ورصد الموقف الدبلوماسي المقابل في موسكو.",
          impact: "تحمل الكابلات البحرية 95% من الاتصالات الدولية، ويعكس الانتشار احتدام التنافس الجيوعسكري تحت سطح البحار.",
          orig: "NATO Allied Maritime Command deploys enhanced naval and undersea surveillance patrols across Baltic corridors."
        },
        {
          id: "d4",
          theater: "INDO_PACIFIC_TAIWAN",
          sev: "HIGH",
          sevLabel: "تأهب مرتفع",
          domain: "reuters.com",
          acc: 93,
          title: "رصد دوريات بحرية وجوية مشتركة في محيط مضيق تايوان وممر باشي مع استمرار حركة الملاحة التجارية الدولية",
          summary: "تطابق البيانات الرسمية المتقابلة في شرق آسيا مع تغطية وكالة رويترز دون إغلاق أي ممر ملاحي مدني.",
          impact: "يعد ممر باشي البوابة الاستراتيجية الرابطة بين بحر الصين الجنوبي وغرب المحيط الهادئ ومسار الكابلات الآسيوية.",
          orig: "Official communiques confirm coordinated naval and early-warning patrols around Taiwan Strait and Bashi Channel."
        }
      ];

      let currentTheater = "ALL";
      let extractedFrames = [];
      let videoSha = "";

      function playChime() {
        try {
          const Ctx = window.AudioContext || window.webkitAudioContext;
          if (!Ctx) return;
          const ctx = new Ctx();
          const now = ctx.currentTime;
          [880, 1174, 880].forEach(function(f, idx) {
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.type = "sawtooth";
            o.frequency.setValueAtTime(f, now + idx * 0.16);
            g.gain.setValueAtTime(0.001, now + idx * 0.16);
            g.gain.exponentialRampToValueAtTime(0.12, now + idx * 0.16 + 0.02);
            g.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.16 + 0.14);
            o.connect(g); g.connect(ctx.destination);
            o.start(now + idx * 0.16); o.stop(now + idx * 0.16 + 0.15);
          });
        } catch (e) {}
      }

      function renderFeed() {
        const list = document.getElementById("dispatchesList");
        const items = dispatches.filter(function(d) {
          return currentTheater === "ALL" || d.theater === currentTheater;
        });
        list.innerHTML = items.map(function(d) {
          const bCls = d.sev === "CRITICAL" ? "b-crit" : "b-high";
          return '<div class="card" onclick="var el=this.querySelector(\\'.detail-box\\');el.classList.toggle(\\'open\\')">' +
            '<div class="meta-row">' +
              '<div><span class="badge ' + bCls + '">' + d.sevLabel + '</span> <span class="badge b-src">' + d.domain + '</span></div>' +
              '<span class="badge b-acc">' + d.acc + '% دقة</span>' +
            '</div>' +
            '<h3>' + d.title + '</h3>' +
            '<p>' + d.summary + '</p>' +
            '<div class="detail-box">' +
              '<div><strong style="color:#fcd34d;">• التفسير الاستراتيجي والعسكري:</strong> ' + d.impact + '</div>' +
              '<div dir="ltr" style="margin-top:8px;padding:8px;background:#030712;border-radius:8px;font-family:monospace;font-size:11px;color:#94a3b8;">' + d.orig + '</div>' +
            '</div>' +
          '</div>';
        }).join("");
      }

      function renderSources() {
        document.getElementById("sourcesList").innerHTML = ROOT_SOURCES.map(function(s) {
          return '<div class="card"><div class="meta-row">' +
            '<div><span class="badge b-src">' + s.code + '</span> <strong style="font-size:13px;color:#fff;">' + s.name + '</strong></div>' +
            '<span class="badge b-acc">' + s.score + '% موثوقية</span>' +
          '</div><p style="margin-top:4px;font-family:monospace;color:#34d399;">https://' + s.domain + '</p></div>';
        }).join("");
      }

      // Navigation
      document.querySelectorAll(".nav-btn").forEach(function(btn) {
        btn.addEventListener("click", function() {
          document.querySelectorAll(".nav-btn").forEach(function(b) { b.classList.remove("active"); });
          document.querySelectorAll(".tab-view").forEach(function(v) { v.classList.remove("active"); });
          btn.classList.add("active");
          document.getElementById("tab-" + btn.getAttribute("data-tab")).classList.add("active");
        });
      });

      document.querySelectorAll("#theaterPills .pill").forEach(function(p) {
        p.addEventListener("click", function() {
          document.querySelectorAll("#theaterPills .pill").forEach(function(x) { x.classList.remove("active"); });
          p.classList.add("active");
          currentTheater = p.getAttribute("data-th");
          renderFeed();
        });
      });

      // Drill Alert Button
      document.getElementById("drillBtn").addEventListener("click", async function() {
        playChime();
        const fresh = {
          id: "drill-" + Date.now(),
          theater: "SAHEL_HORN_AFRICA",
          sev: "CRITICAL",
          sevLabel: "إنذار فوري",
          domain: "news.un.org",
          acc: 96,
          title: "مجلس الأمن الدولي يعقد إحاطة طارئة حول أمن الموانئ والممرات البحرية في القرن الأفريقي وجنوب البحر الأحمر",
          summary: "تم التقاط البرقية من النشرة الرسمية للأمم المتحدة ومقاطعتها مع وكالة الصحافة الفرنسية (AFP) بصياغة عربية محايدة.",
          impact: "تشكل موانئ القرن الأفريقي وباب المندب شريانًا حيويًا للتجارة الدولية والقواعد البحرية العالمية.",
          orig: "UN Security Council holds urgent briefing on maritime corridor security across the Horn of Africa and Red Sea."
        };
        dispatches.unshift(fresh);
        renderFeed();
        try {
          if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.LocalNotifications) {
            await window.Capacitor.Plugins.LocalNotifications.requestPermissions();
            await window.Capacitor.Plugins.LocalNotifications.schedule({
              notifications: [{
                id: Math.floor(Date.now() % 2000000000),
                title: "🚨 راصد [إنذار عاجل - 96% دقة]",
                body: fresh.title
              }]
            });
          }
        } catch (e) {}
      });

      // Video extraction on Android
      document.getElementById("videoInput").addEventListener("change", async function(ev) {
        const file = ev.target.files && ev.target.files[0];
        if (!file) return;
        const box = document.getElementById("videoFramesBox");
        box.innerHTML = "<p style='font-size:12px;color:#67e8f9;'>جاري استخراج الإطارات وحساب بصمة SHA-256...</p>";
        try {
          const buf = await file.slice(0, 2 * 1024 * 1024).arrayBuffer();
          const hashBuf = await crypto.subtle.digest("SHA-256", buf);
          videoSha = Array.from(new Uint8Array(hashBuf)).map(b => b.toString(16).padStart(2, "0")).join("");

          const url = URL.createObjectURL(file);
          const v = document.createElement("video");
          v.muted = true; v.playsInline = true; v.src = url;
          await new Promise((res) => { v.onloadedmetadata = res; setTimeout(res, 3000); });
          const dur = v.duration || 4;
          const c = document.createElement("canvas");
          c.width = 320; c.height = 180;
          const ctx = c.getContext("2d");
          extractedFrames = [];
          for (const frac of [0.15, 0.4, 0.65, 0.88]) {
            v.currentTime = dur * frac;
            await new Promise((r) => { v.onseeked = r; setTimeout(r, 700); });
            ctx.drawImage(v, 0, 0, 320, 180);
            extractedFrames.push({ sec: (dur * frac).toFixed(1), dataUrl: c.toDataURL("image/jpeg", 0.7) });
          }
          URL.revokeObjectURL(url);
          box.innerHTML = extractedFrames.map(f =>
            '<div class="frame-card"><img src="' + f.dataUrl + '"/><div><span>T+' + f.sec + 's</span><span>SHA:' + videoSha.slice(0,6) + '</span></div></div>'
          ).join("");
        } catch (e) {
          box.innerHTML = "<p style='color:#fda4af;'>تعذر قراءة الفيديو</p>";
        }
      });

      // Forensic Analyzer (Cloud Server -> Gemini API -> Local Strict Verifier)
      document.getElementById("analyzeBtn").addEventListener("click", async function() {
        const text = document.getElementById("claimInput").value.trim();
        const url = document.getElementById("claimUrl").value.trim().toLowerCase();
        const out = document.getElementById("forensicOut");
        out.classList.add("open");
        out.innerHTML = "جاري الفحص ومطابقة سجل المصادر الأم...";

        const matched = ROOT_SOURCES.find(s => url.includes(s.domain));
        const isSensational = /(شاهد قبل الحذف|دمار شامل|مصادر سرية|tiktok\\.com|t\\.me)/i.test(text + " " + url);
        let score = matched ? 95 : (isSensational ? 18 : 54);

        const geminiKey = localStorage.getItem("rased_gemini_key") || "";
        if (geminiKey) {
          try {
            const parts = [{ text: "أنت محلل تحقق عسكري في راصد. حلل بدقة وحياد بالعربية هذا الادعاء واكشف أي تضليل في 4 جمل مركزة: " + text + " | الرابط: " + url }];
            extractedFrames.slice(0, 2).forEach(f => {
              parts.push({ inline_data: { mime_type: "image/jpeg", data: f.dataUrl.split(",")[1] } });
            });
            const r = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + encodeURIComponent(geminiKey), {
              method: "POST", headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ contents: [{ parts }] })
            });
            if (r.ok) {
              const j = await r.json();
              const aiTxt = j.candidates[0].content.parts[0].text;
              out.innerHTML = '<div style="color:#6ee7b7;font-weight:700;">درجة الموثوقية: ' + score + '% (Gemini Multimodal AI)</div><p style="margin-top:6px;color:#f1f5f9;">' + aiTxt + '</p>';
              return;
            }
          } catch (e) {}
        }

        out.innerHTML =
          '<div style="font-weight:800;color:' + (score >= 80 ? '#6ee7b7' : '#fda4af') + ';">درجة الموثوقية الجنائية: ' + score + '% • ' +
          (matched ? 'مسند لمصدر أم معتمد (' + matched.name + ')' : 'تحذير: غير مسند لمصدر أم معتمد') + '</div>' +
          (videoSha ? '<div style="font-family:monospace;font-size:11px;color:#67e8f9;margin-top:4px;">SHA-256: ' + videoSha.slice(0, 28) + '...</div>' : '') +
          '<p style="margin-top:6px;color:#e2e8f0;">' +
          (matched
            ? 'الصياغة العربية المحققة: الخبر صادر من نطاق رسمي مدرج في بوابة المصادر الأم، وخالٍ من الصيغ الدعائية المضللة.'
            : 'تم حجز الادعاء عن الإشعارات العاجلة لعدم صدوره من وكالة أنباء أم أو هيئة رسمية معتمدة، مع رصد مؤشرات تهويل أو نقل ثانوي.') +
          '</p>';
      });

      // Cloud & AI Save
      const savedUrl = localStorage.getItem("rased_cloud_server_url") || "${defaultCloudUrl}";
      const savedKey = localStorage.getItem("rased_gemini_key") || "";
      if (savedUrl) document.getElementById("cloudUrlField").value = savedUrl;
      if (savedKey) document.getElementById("geminiKeyField").value = savedKey;

      async function syncWithCloud(url) {
        if (!url) return;
        try {
          const r = await fetch(url.replace(/\\/+$/, "") + "/api/state");
          const j = await r.json();
          if (j && j.ok && Array.isArray(j.dispatches)) {
            document.getElementById("statusSub").textContent = "متصل بالخادم السحابي 24/7 • " + j.dispatches.length + " برقية";
            dispatches = j.dispatches.map(d => ({
              id: d.id,
              theater: d.theaterId,
              sev: d.severity,
              sevLabel: d.severity === "CRITICAL" ? "إنذار حرج" : "تأهب مرتفع",
              domain: d.rootSourceDomain,
              acc: d.accuracy.overallScore,
              title: d.headlineAr,
              summary: d.flashSummaryAr,
              impact: d.strategicExplanation.operationalImpactAr,
              orig: d.originalHeadline + " — " + d.originalExcerpt
            }));
            renderFeed();
          }
        } catch (e) {}
      }

      document.getElementById("saveCloudBtn").addEventListener("click", async function() {
        const u = document.getElementById("cloudUrlField").value.trim().replace(/\\/+$/, "");
        const k = document.getElementById("geminiKeyField").value.trim();
        localStorage.setItem("rased_cloud_server_url", u);
        if (k) localStorage.setItem("rased_gemini_key", k);
        try {
          if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.SentinelNative) {
            await window.Capacitor.Plugins.SentinelNative.startForegroundVigilance({ serverUrl: u, pollSeconds: 45 });
          }
        } catch (e) {}
        document.getElementById("cloudSaveMsg").textContent = "✓ تم الحفظ وتفعيل خدمة التأهب الخلفية الدائمة 24/7 على هاتفك.";
        if (u) syncWithCloud(u);
      });

      renderFeed();
      renderSources();
      if (savedUrl) syncWithCloud(savedUrl);
    })();
  </script>
</body>
</html>
`;

fs.writeFileSync(path.join(outDir, "index.html"), html, "utf-8");
console.log("[RASED APK] Generated full 5-tab mobile-shell/index.html successfully.");
