"use client";

import { useEffect, useMemo, useState } from "react";
import { Capacitor } from "@capacitor/core";
import { Browser } from "@capacitor/browser";

type Section = "overview" | "sources" | "fieldnotes";
type Quake = { id: string; place: string; magnitude: number; time: number; url: string; depth: number };
type Source = { id: string; name: string; kind: string; region: string; url: string; detail: string; live?: boolean };
type Note = { id: string; title: string; source: string; url: string; text: string; createdAt: string };

const sources: Source[] = [
  { id: "un-webtv", name: "UN Web TV", kind: "بث مباشر", region: "دولي", url: "https://webtv.un.org/en", detail: "بثّ علني لاجتماعات وفعاليات الأمم المتحدة." },
  { id: "un-press", name: "تغطية مجلس الأمن", kind: "محاضر وتصريحات", region: "دولي", url: "https://press.un.org/en/content/security-council/meetings-coverage", detail: "تغطية رسمية لاجتماعات مجلس الأمن وبياناته." },
  { id: "maroc", name: "بوابة المغرب الرسمية", kind: "بيانات حكومية", region: "المغرب", url: "https://www.maroc.ma/ar", detail: "بوابة رسمية للأخبار والبلاغات الحكومية المنشورة." },
  { id: "who", name: "منظمة الصحة العالمية", kind: "تنبيهات صحية", region: "دولي", url: "https://www.who.int/emergencies/disease-outbreak-news", detail: "إشعارات صحية عامة صادرة عن المنظمة." },
  { id: "usgs", name: "USGS · رصد الزلازل", kind: "بيانات حية", region: "عالمي", url: "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson", detail: "خلاصة آلية للنشاط الزلزالي خلال آخر 24 ساعة.", live: true },
  { id: "gdacs", name: "GDACS", kind: "إنذارات كوارث", region: "دولي", url: "https://www.gdacs.org/", detail: "نظام تنسيق دولي لمتابعة الكوارث الطبيعية." },
];

const navigation: { id: Section; label: string; icon: string }[] = [
  { id: "overview", label: "نظرة عامة", icon: "◫" },
  { id: "sources", label: "مكتبة المصادر", icon: "◎" },
  { id: "fieldnotes", label: "دفتر التحقق", icon: "▤" },
];

function ExternalIcon() {
  return <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M11 3h6v6M17 3l-8 8"/><path d="M15 11v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h4"/></svg>;
}

function formatAgo(timestamp: number) {
  const minutes = Math.max(0, Math.floor((Date.now() - timestamp) / 60000));
  if (minutes < 1) return "الآن";
  if (minutes < 60) return `قبل ${minutes} د`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `قبل ${hours} س`;
  return `قبل ${Math.floor(hours / 24)} يوم`;
}

export default function Home() {
  const [section, setSection] = useState<Section>("overview");
  const [quakes, setQuakes] = useState<Quake[]>([]);
  const [quakeState, setQuakeState] = useState<"loading" | "ready" | "error">("loading");
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("الكل");
  const [savedSources, setSavedSources] = useState<string[]>(["un-webtv", "maroc", "usgs"]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [showNote, setShowNote] = useState(false);
  const [toast, setToast] = useState("");
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [mobileNav, setMobileNav] = useState(false);

  useEffect(() => {
    try {
      const storedSources = localStorage.getItem("marsad-sources");
      const storedNotes = localStorage.getItem("marsad-notes");
      if (storedSources) setSavedSources(JSON.parse(storedSources));
      if (storedNotes) setNotes(JSON.parse(storedNotes));
    } catch { /* ignore invalid local preferences */ }
    const handler = (event: Event) => {
      event.preventDefault();
      setInstallPrompt(event as BeforeInstallPromptEvent);
    };
    window.addEventListener("beforeinstallprompt", handler);
    if ("serviceWorker" in navigator && process.env.NODE_ENV === "production") {
      navigator.serviceWorker.register("/sw.js").catch(() => undefined);
    }
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;
    const handleExternalLink = (event: MouseEvent) => {
      if (!(event.target instanceof Element)) return;
      const anchor = event.target.closest("a[href]");
      if (!(anchor instanceof HTMLAnchorElement) || !/^https?:$/.test(new URL(anchor.href).protocol)) return;
      event.preventDefault();
      void Browser.open({ url: anchor.href });
    };
    document.addEventListener("click", handleExternalLink);
    return () => document.removeEventListener("click", handleExternalLink);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setQuakeState("loading");
      try {
        const response = await fetch("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson", { cache: "no-store" });
        if (!response.ok) throw new Error("feed unavailable");
        const data = await response.json();
        if (cancelled) return;
        const items: Quake[] = (data.features ?? []).slice(0, 8).map((item: { id: string; properties: { place: string; mag: number; time: number; url: string }; geometry: { coordinates: number[] } }) => ({
          id: item.id,
          place: item.properties.place,
          magnitude: item.properties.mag,
          time: item.properties.time,
          url: item.properties.url,
          depth: item.geometry.coordinates[2],
        }));
        setQuakes(items);
        setLastChecked(new Date());
        setQuakeState("ready");
      } catch {
        if (!cancelled) setQuakeState("error");
      }
    };
    load();
    const timer = window.setInterval(load, 5 * 60 * 1000);
    return () => { cancelled = true; window.clearInterval(timer); };
  }, []);

  useEffect(() => {
    localStorage.setItem("marsad-sources", JSON.stringify(savedSources));
  }, [savedSources]);
  useEffect(() => {
    localStorage.setItem("marsad-notes", JSON.stringify(notes));
  }, [notes]);

  const filteredSources = useMemo(() => sources.filter((source) => {
    const matchesText = `${source.name} ${source.kind} ${source.region} ${source.detail}`.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === "الكل" || source.kind === filter || source.region === filter;
    return matchesText && matchesFilter;
  }), [search, filter]);

  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2600);
  };

  const toggleSource = (id: string) => {
    setSavedSources((current) => current.includes(id) ? current.filter((value) => value !== id) : [...current, id]);
    notify(savedSources.includes(id) ? "أزيل المصدر من قائمتك" : "أضيف المصدر إلى قائمتك");
  };

  const addNote = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = String(form.get("title") || "").trim();
    const url = String(form.get("url") || "").trim();
    const text = String(form.get("text") || "").trim();
    if (!title || !text) return;
    setNotes((current) => [{ id: crypto.randomUUID(), title, source: String(form.get("source") || "مصدر مباشر"), url, text, createdAt: new Date().toISOString() }, ...current]);
    setShowNote(false);
    notify("حُفظت ملاحظتك على هذا الجهاز");
  };

  const installApp = async () => {
    if (!installPrompt) {
      notify("استخدم قائمة المتصفح ثم «إضافة إلى الشاشة الرئيسية»");
      return;
    }
    await installPrompt.prompt();
    setInstallPrompt(null);
  };

  const latestQuake = quakes.reduce<Quake | null>((max, item) => !max || item.magnitude > max.magnitude ? item : max, null);

  return (
    <main className="app-shell" dir="rtl">
      <aside className={`sidebar ${mobileNav ? "sidebar-open" : ""}`}>
        <a className="brand" href="#home" onClick={() => setSection("overview")}>
          <span className="brand-mark"><span>م</span><i /></span>
          <span className="brand-copy"><strong>مِرصد</strong><small>من المصدر، لا من الصدى</small></span>
        </a>
        <div className="sidebar-label">مساحة العمل</div>
        <nav className="main-nav" aria-label="التنقل الرئيسي">
          {navigation.map((item) => <button key={item.id} className={section === item.id ? "nav-item active" : "nav-item"} onClick={() => { setSection(item.id); setMobileNav(false); }}><span className="nav-icon">{item.icon}</span>{item.label}{item.id === "fieldnotes" && notes.length > 0 && <b className="nav-count">{notes.length}</b>}</button>)}
        </nav>
        <div className="sidebar-rule" />
        <div className="sidebar-label">مصادري المثبّتة <span>{savedSources.length}</span></div>
        <div className="pinned-list">
          {sources.filter((item) => savedSources.includes(item.id)).slice(0, 4).map((source) => <button key={source.id} className="pinned-item" onClick={() => { setSection("sources"); setSearch(source.name); setMobileNav(false); }}><i className={`source-dot ${source.live ? "live" : ""}`} /><span>{source.name}</span></button>)}
          {savedSources.length === 0 && <p className="quiet-note">ثبّت مصادر لتظهر هنا.</p>}
        </div>
        <div className="sidebar-bottom">
          <div className="privacy-card"><span className="privacy-icon">⌁</span><div><strong>خصوصيتك أولًا</strong><p>ملاحظاتك محفوظة على جهازك فقط.</p></div></div>
          <div className="profile-row"><span className="avatar">م</span><span><b>مساحة شخصية</b><small>لا حساب · لا تتبّع</small></span><span className="more">···</span></div>
        </div>
      </aside>

      <section className="main-area">
        <header className="topbar">
          <button className="mobile-menu" aria-label="القائمة" onClick={() => setMobileNav(!mobileNav)}>☰</button>
          <div className="breadcrumb"><span>مساحة الرصد</span><b>/</b><strong>{navigation.find((item) => item.id === section)?.label}</strong></div>
          <div className="top-actions"><span className="local-badge"><i /> يعمل محليًا</span><button className="install-btn" onClick={installApp}><span>↓</span> تثبيت التطبيق</button></div>
        </header>
        <div className="content-wrap">
          {section === "overview" && <>
            <div className="welcome-row"><div><div className="eyebrow"><span className="eyebrow-line" /> لوحة الرصد الشخصي</div><h1>اعرف ما قيل.<br /><em>وتحقّق بنفسك.</em></h1><p className="welcome-copy">مصادر أولية، سياق واضح، ولا ادّعاء بمعرفة ما لا نعرفه.</p></div><div className="date-chip"><span className="calendar-icon">▦</span><div><small>التاريخ المحلي</small><strong>{new Intl.DateTimeFormat("ar-MA", { weekday: "long", day: "numeric", month: "long" }).format(new Date())}</strong></div></div></div>
            <section className="truth-strip"><span className="truth-symbol">i</span><p><strong>مبدأ مِرصد</strong> — نعرض المصدر الأصلي ووقت التحديث. وجود معلومة هنا لا يعني التحقق من صحتها؛ افحص السياق وقارن الأدلة.</p><button onClick={() => setSection("sources")}>كيف يعمل؟ <span>←</span></button></section>

            <div className="section-heading"><div><span className="section-kicker">إشارات قابلة للتحقق</span><h2>ماذا يحدث الآن؟</h2></div><span className="update-state"><i className={quakeState === "ready" ? "pulse-dot" : "pulse-dot muted"} />{quakeState === "ready" ? "تحديث تلقائي كل 5 دقائق" : quakeState === "error" ? "تعذّر الاتصال بالمصدر" : "جارٍ الاتصال بالمصدر المفتوح"}</span></div>
            <div className="metrics-grid">
              <article className="metric-card metric-featured"><div className="metric-top"><span className="metric-icon globe-icon">◎</span><span className="metric-label">رصد زلزالي · USGS</span><a href={sources.find((s) => s.id === "usgs")?.url} target="_blank" rel="noreferrer" aria-label="افتح المصدر الأصلي"><ExternalIcon /></a></div><div className="metric-main"><strong>{quakeState === "ready" ? quakes.length : "—"}</strong><span>أحداث معروضة<br />خلال آخر 24 ساعة</span></div><div className="metric-foot"><span>{quakeState === "ready" ? `أعلى مقدار: ${latestQuake ? latestQuake.magnitude.toFixed(1) : "—"}` : quakeState === "error" ? "البيانات غير متاحة الآن" : "بانتظار استجابة المصدر"}</span><span>{lastChecked ? lastChecked.toLocaleTimeString("ar-MA", { hour: "2-digit", minute: "2-digit" }) : "—"}</span></div></article>
              <article className="metric-card"><div className="metric-top"><span className="metric-icon docs-icon">▤</span><span className="metric-label">مصادر أولية</span><button className="text-arrow" onClick={() => setSection("sources")}>عرض الكل <span>←</span></button></div><div className="metric-main"><strong>{sources.length}</strong><span>مصادر عامة<br />قابلة للفتح والتحقق</span></div><div className="metric-foot"><span>حكومية · دولية · علمية</span><span className="green-tag">مباشرة</span></div></article>
              <article className="metric-card"><div className="metric-top"><span className="metric-icon note-icon">✎</span><span className="metric-label">دفتر التحقق</span><button className="text-arrow" onClick={() => setSection("fieldnotes")}>فتح الدفتر <span>←</span></button></div><div className="metric-main"><strong>{notes.length.toLocaleString("ar-MA")}</strong><span>ملاحظة محفوظة<br />على هذا الجهاز</span></div><div className="metric-foot"><span>لا مزامنة سحابية</span><span className="lock-mark">⌑ خاص</span></div></article>
            </div>

            <div className="dashboard-columns">
              <section className="panel activity-panel"><div className="panel-heading"><div><span className="section-kicker">مصدر بيانات مفتوح</span><h3>آخر النشاط الزلزالي</h3></div><a className="source-link" href={sources.find((s) => s.id === "usgs")?.url} target="_blank" rel="noreferrer">USGS <ExternalIcon /></a></div><div className="earthquake-list">
                {quakeState === "loading" && <div className="empty-state"><span className="spinner" /> جارٍ جلب بيانات المصدر…</div>}
                {quakeState === "error" && <div className="empty-state error-state"><span>!</span><div><b>تعذر تحميل البيانات</b><small>قد يكون المصدر غير متاح أو الاتصال مقطوعًا. لا نعرض بيانات قديمة كأنها حيّة.</small><button onClick={() => window.location.reload()}>إعادة المحاولة</button></div></div>}
                {quakeState === "ready" && quakes.length === 0 && <div className="empty-state">لا توجد أحداث في الخلاصة الحالية.</div>}
                {quakeState === "ready" && quakes.slice(0, 5).map((quake) => <a className="quake-row" href={quake.url} target="_blank" rel="noreferrer" key={quake.id}><span className={`magnitude ${quake.magnitude >= 4.5 ? "high" : ""}`}>{quake.magnitude.toFixed(1)}</span><span className="quake-info"><b>{quake.place || "موقع غير محدد"}</b><small>عمق {Math.round(quake.depth)} كم · {formatAgo(quake.time)}</small></span><span className="row-open"><ExternalIcon /></span></a>)}
              </div><div className="panel-foot"><span>البيانات من خدمة USGS العامة؛ تعرض الزلازل فقط.</span><span>{lastChecked ? `تحديث ${lastChecked.toLocaleTimeString("ar-MA", { hour: "2-digit", minute: "2-digit" })}` : ""}</span></div></section>

              <section className="panel quick-panel"><div className="panel-heading"><div><span className="section-kicker">وصول مباشر</span><h3>مصادرك المثبّتة</h3></div><button className="add-round" aria-label="إضافة مصدر" onClick={() => setSection("sources")}>＋</button></div><div className="quick-sources">{sources.filter((source) => savedSources.includes(source.id)).slice(0, 4).map((source) => <a className="quick-source" key={source.id} href={source.url} target="_blank" rel="noreferrer"><span className={`quick-source-icon q-${source.id}`}>{source.id === "usgs" ? "⌁" : source.id === "maroc" ? "م" : source.id === "who" ? "+" : "◉"}</span><span className="quick-source-text"><b>{source.name}</b><small>{source.kind} · {source.region}</small></span><ExternalIcon /></a>)}{savedSources.length === 0 && <p className="empty-mini">اذهب إلى مكتبة المصادر وثبّت ما يهمك.</p>}</div><button className="all-sources-btn" onClick={() => setSection("sources")}>استكشف مكتبة المصادر <span>←</span></button></section>
            </div>

            <section className="prepared-card"><div className="prepared-art"><span className="orbit orbit-one"/><span className="orbit orbit-two"/><span className="prepared-core">⌖</span></div><div className="prepared-copy"><span className="section-kicker">استعداد بلا تهويل</span><h3>المعلومة المفيدة تبدأ بخطة واضحة.</h3><p>جهّز قائمة اتصال، دوّن نقاط الالتقاء، واحفظ إرشادات الطوارئ الرسمية محليًا. لا تنتظر تطبيقًا ليؤكد خطرًا آنيًا.</p></div><button onClick={() => { setSection("fieldnotes"); setShowNote(true); }}>دوّن خطة الاستعداد <span>←</span></button></section>
            <footer className="page-footer"><span>مِرصد — أداة متابعة للمصادر العامة، وليست نظام إنذار رسميًا.</span><span>بياناتك تبقى على جهازك <i>◆</i></span></footer>
          </>}

          {section === "sources" && <>
            <div className="page-title-row"><div><div className="eyebrow"><span className="eyebrow-line" /> مكتبة المصادر</div><h1 className="page-title">ابدأ من <em>الأصل.</em></h1><p className="welcome-copy">روابط مباشرة إلى جهات تنشر بياناتها علنًا. المصدر الأولي يبيّن ما قيل، ولا يثبت وحده صحته.</p></div><button className="install-btn" onClick={() => setShowNote(true)}>＋ أضف إلى دفتر التحقق</button></div>
            <div className="source-tools"><label className="search-box"><span>⌕</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="ابحث عن جهة أو موضوع…" /><kbd>⌘ K</kbd></label><div className="filter-row">{["الكل", "دولي", "المغرب", "بث مباشر", "بيانات حية"].map((item) => <button className={filter === item ? "filter-chip selected" : "filter-chip"} key={item} onClick={() => setFilter(item)}>{item}</button>)}</div></div>
            <div className="source-grid">{filteredSources.map((source, index) => <article className="source-card" key={source.id}><div className="source-card-top"><span className={`source-emblem emblem-${index % 5}`}>{source.id === "maroc" ? "م" : source.id === "who" ? "+" : source.id === "usgs" ? "⌁" : source.id === "gdacs" ? "△" : "◉"}</span><span className="source-type">{source.kind}</span><button className={savedSources.includes(source.id) ? "bookmark saved" : "bookmark"} onClick={() => toggleSource(source.id)} title={savedSources.includes(source.id) ? "إزالة من المثبتة" : "تثبيت المصدر"}>{savedSources.includes(source.id) ? "◆" : "◇"}</button></div><h3>{source.name}</h3><p>{source.detail}</p><div className="source-card-bottom"><span><i className={source.live ? "source-dot live" : "source-dot"} />{source.region}{source.live ? " · خلاصة آلية" : " · صفحة عامة"}</span><a href={source.url} target="_blank" rel="noreferrer">فتح المصدر <ExternalIcon /></a></div></article>)}</div>
            {filteredSources.length === 0 && <div className="empty-search"><span>⌕</span><b>لا توجد نتائج</b><small>جرّب كلمة بحث أخرى أو غيّر التصفية.</small></div>}
            <div className="source-disclaimer"><span>ⓘ</span><p><b>تنبيه منهجي:</b> وجود الجهة في المكتبة لا يعني تزكية كل ما تنشره. احتفظ بالرابط والتاريخ، واقرأ المادة الأصلية كاملةً قبل الاستنتاج.</p></div>
          </>}

          {section === "fieldnotes" && <>
            <div className="page-title-row"><div><div className="eyebrow"><span className="eyebrow-line" /> أدواتك الخاصة</div><h1 className="page-title">دفتر <em>التحقّق.</em></h1><p className="welcome-copy">سجّل ما شاهدته في المصدر، وافصل الاقتباس عن تفسيرك له.</p></div><button className="install-btn" onClick={() => setShowNote(true)}>＋ ملاحظة جديدة</button></div>
            <div className="method-banner"><span>01</span><div><b>دوّن قبل أن تستنتج</b><p>من قال ماذا؟ متى؟ أين التسجيل الكامل؟ ما الذي لا نعرفه بعد؟ الملاحظات هنا خاصة بهذا الجهاز ولا تُرسل إلى خادم.</p></div><span className="method-stamp">محلي فقط · 🔒</span></div>
            {notes.length === 0 ? <div className="empty-notes"><div className="empty-note-icon">✎</div><h3>دفترك يبدأ منك</h3><p>لا توجد ملاحظات محفوظة بعد. أضف رابطًا ومقتطفًا أو اكتب خطة استعداد شخصية.</p><button className="primary-btn" onClick={() => setShowNote(true)}>＋ أنشئ أول ملاحظة</button></div> : <div className="notes-list">{notes.map((note) => <article className="note-card" key={note.id}><div className="note-card-meta"><span>ملاحظة شخصية</span><span>{new Date(note.createdAt).toLocaleDateString("ar-MA", { day: "numeric", month: "long", year: "numeric" })}</span></div><h3>{note.title}</h3><p className="note-source">المصدر: {note.source}{note.url && <> · <a href={note.url} target="_blank" rel="noreferrer">فتح الرابط <ExternalIcon /></a></>}</p><blockquote>{note.text}</blockquote><button className="delete-note" onClick={() => setNotes((current) => current.filter((item) => item.id !== note.id))}>حذف الملاحظة</button></article>)}</div>}
            <button className="export-btn" onClick={() => { const blob = new Blob([JSON.stringify(notes, null, 2)], { type: "application/json" }); const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = "marsad-notes.json"; link.click(); URL.revokeObjectURL(link.href); }}>↓ تصدير نسخة احتياطية من ملاحظاتي</button>
          </>}
        </div>
      </section>

      {showNote && <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setShowNote(false); }}><form className="note-modal" onSubmit={addNote}><div className="modal-head"><div><span className="section-kicker">دفتر خاص · على هذا الجهاز</span><h2>ملاحظة جديدة</h2></div><button type="button" className="modal-close" onClick={() => setShowNote(false)}>×</button></div><label>عنوان الملاحظة<input name="title" placeholder="مثال: تصريح في جلسة اليوم" required autoFocus /></label><label>الجهة أو المصدر<input name="source" placeholder="اسم الجهة أو المتحدث" /></label><label>رابط المصدر الأصلي <span className="optional">اختياري</span><input name="url" type="url" placeholder="https://…" /></label><label>ماذا شاهدت أو سمعت؟<textarea name="text" rows={5} placeholder="اكتب المقتطف كما ورد، ثم ميّز رأيك عنه…" required /></label><div className="modal-tip">ⓘ هذه الملاحظة لا تتحقق من صحة الادعاء، ولا تغادر هذا الجهاز.</div><div className="modal-actions"><button type="button" className="cancel-btn" onClick={() => setShowNote(false)}>إلغاء</button><button className="primary-btn" type="submit">حفظ الملاحظة</button></div></form></div>}
      {toast && <div className="toast"><span>✓</span>{toast}</div>}
    </main>
  );
}

type BeforeInstallPromptEvent = Event & { prompt: () => Promise<void>; userChoice: Promise<{ outcome: "accepted" | "dismissed" }> };
