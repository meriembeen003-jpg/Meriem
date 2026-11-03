"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Browser } from "@capacitor/browser";
import { Capacitor } from "@capacitor/core";
import { loadPublicFeed, PUBLIC_FEEDS, type FeedResult, type PublicItem } from "./lib/feeds";

type View = "briefing" | "saved" | "sources" | "method";
type Note = { id: string; title: string; source: string; url: string; text: string; createdAt: string };
type InstallPromptEvent = Event & { prompt: () => Promise<void> };

const viewItems: { id: View; label: string; icon: string }[] = [
  { id: "briefing", label: "النشرة", icon: "▥" },
  { id: "saved", label: "المحفوظات", icon: "☆" },
  { id: "sources", label: "المصادر", icon: "⌘" },
  { id: "method", label: "عن مِرصد", icon: "i" },
];

const publicBroadcasts = [
  { title: "UN Web TV", subtitle: "جلسات وفعاليات الأمم المتحدة", url: "https://webtv.un.org/en", symbol: "UN", tone: "violet" },
  { title: "البوابة المغربية", subtitle: "تسجيلات ومواد منشورة", url: "https://maroc.ma/ar", symbol: "MA", tone: "mint" },
];

function OpenIcon({ small = false }: { small?: boolean }) {
  return <svg className={small ? "open-icon small" : "open-icon"} viewBox="0 0 20 20" aria-hidden="true"><path d="M11 3h6v6M17 3l-8 8"/><path d="M15 11v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h4"/></svg>;
}

function RadarMark() {
  return <span className="radar-mark" aria-hidden="true"><svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="15"/><circle cx="20" cy="20" r="9"/><circle cx="20" cy="20" r="3"/><path d="M20 20 31 8"/><path className="radar-spark" d="M30 8h4v4"/></svg></span>;
}

function CountrySeal({ code, tone }: { code: string; tone: string }) {
  return <span className={`country-seal tone-${tone}`}>{code}</span>;
}

function formatDate(value: string | null, compact = false) {
  if (!value) return "التاريخ غير مذكور في الخلاصة";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "التاريخ غير مذكور في الخلاصة";
  const now = Date.now();
  const elapsed = Math.max(0, now - date.getTime());
  if (elapsed < 60_000) return "منذ لحظات";
  if (elapsed < 60 * 60_000) return `قبل ${Math.floor(elapsed / 60_000)} دقيقة`;
  if (elapsed < 24 * 60 * 60_000) return `قبل ${Math.floor(elapsed / (60 * 60_000))} ساعة`;
  return new Intl.DateTimeFormat("ar-MA", compact ? { day: "numeric", month: "short" } : { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" }).format(date);
}

function getFeedTone(feedId: string) {
  return PUBLIC_FEEDS.find((feed) => feed.id === feedId)?.tone ?? "blue";
}

function getSourceLabel(item: PublicItem) {
  const code = item.countryCode;
  return code === "UN" ? "مؤسسة دولية" : "مصدر حكومي مباشر";
}

export default function Home() {
  const [view, setView] = useState<View>("briefing");
  const [results, setResults] = useState<FeedResult[]>([]);
  const resultsRef = useRef<FeedResult[]>([]);
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready">("idle");
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [countryFilter, setCountryFilter] = useState("all");
  const [favorites, setFavorites] = useState<string[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [preferencesReady, setPreferencesReady] = useState(false);
  const [selected, setSelected] = useState<PublicItem | null>(null);
  const [toast, setToast] = useState("");
  const [showNote, setShowNote] = useState(false);
  const [online, setOnline] = useState(true);
  const [installPrompt, setInstallPrompt] = useState<InstallPromptEvent | null>(null);
  const [speakState, setSpeakState] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const refresh = useCallback(async () => {
    setLoadState("loading");
    const fetched = await Promise.all(PUBLIC_FEEDS.map(loadPublicFeed));
    const previous = resultsRef.current;
    const merged = fetched.map((result) => {
      if (!result.error) return result;
      const cached = previous.find((entry) => entry.feed.id === result.feed.id && entry.items.length > 0);
      return cached ? { ...cached, error: result.error, stale: true } : result;
    });
    const checkedAt = new Date().toISOString();
    resultsRef.current = merged;
    setResults(merged);
    setLastUpdated(checkedAt);
    setLoadState("ready");
    try { localStorage.setItem("marsad-feed-cache-v2", JSON.stringify({ checkedAt, results: merged })); } catch { /* cache is optional */ }
  }, []);

  useEffect(() => {
    const restoreTimer = window.setTimeout(() => {
      try {
        setFavorites(JSON.parse(localStorage.getItem("marsad-favorites-v2") || "[]"));
        setNotes(JSON.parse(localStorage.getItem("marsad-notes-v2") || "[]"));
        const cached = JSON.parse(localStorage.getItem("marsad-feed-cache-v2") || "null") as { checkedAt?: string; results?: FeedResult[] } | null;
        if (cached?.results?.length) {
          const known = new Set(PUBLIC_FEEDS.map((feed) => feed.id));
          const restored = cached.results.filter((result) => known.has(result.feed.id)).map((result) => ({ ...result, stale: true }));
          resultsRef.current = restored;
          setResults(restored);
          if (cached.checkedAt) setLastUpdated(cached.checkedAt);
          setLoadState("ready");
        }
      } catch { /* discard corrupt local preferences or feed cache */ }
      setOnline(navigator.onLine);
      setPreferencesReady(true);
    }, 0);
    const onlineHandler = () => setOnline(true);
    const offlineHandler = () => setOnline(false);
    const installHandler = (event: Event) => {
      event.preventDefault();
      setInstallPrompt(event as InstallPromptEvent);
    };
    window.addEventListener("online", onlineHandler);
    window.addEventListener("offline", offlineHandler);
    window.addEventListener("beforeinstallprompt", installHandler);
    if ("serviceWorker" in navigator && process.env.NODE_ENV === "production") {
      navigator.serviceWorker.register("/sw.js").catch(() => undefined);
    }
    const initialRefreshTimer = window.setTimeout(() => { void refresh(); }, 0);
    const interval = window.setInterval(refresh, 15 * 60 * 1000);
    return () => {
      window.removeEventListener("online", onlineHandler);
      window.removeEventListener("offline", offlineHandler);
      window.removeEventListener("beforeinstallprompt", installHandler);
      window.clearTimeout(restoreTimer);
      window.clearTimeout(initialRefreshTimer);
      window.clearInterval(interval);
    };
  }, [refresh]);

  useEffect(() => { if (preferencesReady) localStorage.setItem("marsad-favorites-v2", JSON.stringify(favorites)); }, [favorites, preferencesReady]);
  useEffect(() => { if (preferencesReady) localStorage.setItem("marsad-notes-v2", JSON.stringify(notes)); }, [notes, preferencesReady]);

  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;
    const openOfficialSource = (event: MouseEvent) => {
      if (!(event.target instanceof Element)) return;
      const anchor = event.target.closest("a[href]");
      if (!(anchor instanceof HTMLAnchorElement)) return;
      const url = new URL(anchor.href);
      if (url.protocol !== "https:") return;
      event.preventDefault();
      void Browser.open({ url: anchor.href });
    };
    document.addEventListener("click", openOfficialSource);
    return () => document.removeEventListener("click", openOfficialSource);
  }, []);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        document.querySelector<HTMLInputElement>(".global-search input")?.focus();
      }
      if (event.key === "Escape") { setSelected(null); setShowNote(false); setMenuOpen(false); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const allItems = useMemo(() => {
    const items = results.flatMap((result) => result.items);
    return items.sort((a, b) => {
      if (!a.publishedAt) return 1;
      if (!b.publishedAt) return -1;
      return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
    });
  }, [results]);

  const visibleItems = useMemo(() => allItems.filter((item) => {
    const matchesCountry = countryFilter === "all" || item.feedId === countryFilter;
    const matchesSaved = view !== "saved" || favorites.includes(item.id);
    const query = search.trim().toLocaleLowerCase();
    const matchesSearch = !query || `${item.title} ${item.excerpt} ${item.organization} ${item.country}`.toLocaleLowerCase().includes(query);
    return matchesCountry && matchesSaved && matchesSearch;
  }), [allItems, countryFilter, favorites, search, view]);

  const successfulFeeds = results.filter((result) => !result.error && !result.stale && result.items.length).length;
  const totalFeeds = PUBLIC_FEEDS.length;
  const toggleFavorite = (id: string) => setFavorites((current) => current.includes(id) ? current.filter((item) => item !== id) : [id, ...current]);
  const notify = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2600); };

  const addNote = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = String(form.get("title") || "").trim();
    const text = String(form.get("text") || "").trim();
    if (!title || !text) return;
    setNotes((current) => [{ id: crypto.randomUUID(), title, source: String(form.get("source") || "مصدر عام"), url: String(form.get("url") || ""), text, createdAt: new Date().toISOString() }, ...current]);
    setShowNote(false);
    notify("حُفظت الملاحظة على هذا الجهاز فقط");
  };

  const openNoteFor = (item?: PublicItem | null) => {
    setSelected(item ?? null);
    setShowNote(true);
  };

  const speak = (item: PublicItem) => {
    if (!("speechSynthesis" in window)) { notify("القراءة الصوتية غير متاحة على هذا الجهاز"); return; }
    if (speakState) {
      window.speechSynthesis.cancel();
      setSpeakState(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance([item.title, item.excerpt].filter(Boolean).join(". "));
    utterance.lang = item.language === "العربية" ? "ar-MA" : item.language === "Français" ? "fr-FR" : "en-US";
    utterance.rate = 0.92;
    utterance.onend = () => setSpeakState(false);
    utterance.onerror = () => setSpeakState(false);
    window.speechSynthesis.speak(utterance);
    setSpeakState(true);
  };

  const install = async () => {
    if (!installPrompt) { notify("من قائمة المتصفح اختر: إضافة إلى الشاشة الرئيسية"); return; }
    await installPrompt.prompt();
    setInstallPrompt(null);
  };

  const currentTitle = viewItems.find((item) => item.id === view)?.label ?? "النشرة";
  const chosenFilter = (id: string) => {
    setCountryFilter(id);
    if (id !== "all") setView("briefing");
  };

  return (
    <main className="mirsad" dir="rtl">
      <aside className={`rail ${menuOpen ? "rail-open" : ""}`}>
        <div className="rail-brand"><RadarMark /><span><strong>مِرصد</strong><small>المصادر العلنية كما هي</small></span></div>
        <div className="rail-caption">مساحة الرصد</div>
        <nav className="rail-nav" aria-label="التنقل">
          {viewItems.map((item) => <button key={item.id} className={view === item.id ? "rail-link current" : "rail-link"} onClick={() => { setView(item.id); if (item.id === "saved") setCountryFilter("all"); setMenuOpen(false); }}><span className="rail-glyph">{item.icon}</span><span>{item.label}</span>{item.id === "saved" && favorites.length > 0 && <b>{favorites.length}</b>}</button>)}
        </nav>
        <div className="rail-divider" />
        <div className="rail-caption rail-caption-row"><span>تدفقات مفعّلة</span><span className="rail-count">{successfulFeeds}/{totalFeeds}</span></div>
        <div className="source-mini-list">
          {PUBLIC_FEEDS.map((feed) => {
            const state = results.find((result) => result.feed.id === feed.id);
            return <button key={feed.id} className="source-mini" onClick={() => { chosenFilter(feed.id); setMenuOpen(false); }}><CountrySeal code={feed.countryCode} tone={feed.tone} /><span>{feed.country}</span><i className={state?.error ? "feed-indicator bad" : state?.stale ? "feed-indicator stale" : state ? "feed-indicator ok" : "feed-indicator"} /></button>;
          })}
        </div>
        <div className="rail-spacer" />
        <a className="rail-live-link" href="https://webtv.un.org/en" target="_blank" rel="noreferrer"><span className="live-wave"><i /><i /><i /><i /></span><span><b>بث عام</b><small>UN Web TV · فتح البث</small></span><OpenIcon small /></a>
        <div className="rail-bottom"><span className={`connection-light ${online ? "is-online" : "is-offline"}`} /><span>{online ? "الاتصال متاح" : "غير متصل"}</span><button onClick={install} aria-label="تثبيت التطبيق">تثبيت التطبيق <span>↓</span></button></div>
      </aside>

      <section className="stage">
        <header className="masthead">
          <button className="menu-trigger" onClick={() => setMenuOpen((open) => !open)} aria-label="فتح القائمة">☰</button>
          <div className="masthead-left"><span className="masthead-overline">مِرصد / <b>{currentTitle}</b></span><span className="masthead-date">{new Intl.DateTimeFormat("ar-MA", { weekday: "long", day: "numeric", month: "long" }).format(new Date())}</span></div>
          <div className="masthead-tools"><div className="secure-label"><span>◉</span> مصادر عامة فقط</div><button className="refresh-button" onClick={refresh} disabled={loadState === "loading"}><span className={loadState === "loading" ? "refresh-icon spinning" : "refresh-icon"}>↻</span><span>{loadState === "loading" ? "يحدّث…" : "تحديث"}</span></button></div>
        </header>

        <div className="page-content">
          <section className="intro-panel">
            <div className="intro-copy">
              <div className="eyebrow"><span className="eyebrow-dash" /> رصد التصريحات والبيانات المنشورة</div>
              <h1>من الجهة مباشرة.<br /><em>بلا وسيط بينك وبين المصدر.</em></h1>
              <p>تابع ما تنشره الجهات علنًا، وافتح النص أو التسجيل الأصلي بنفسك. لا نعيد صياغة التصريحات ولا نزعم التحقق من صحتها.</p>
              <div className="intro-actions"><button className="primary-action" onClick={() => { setView("briefing"); document.querySelector(".feed-controls")?.scrollIntoView({ behavior: "smooth", block: "center" }); }}>استكشف النشرة <span>←</span></button><button className="quiet-action" onClick={() => setView("sources")}>تعرّف على المصادر</button></div>
            </div>
            <div className="signal-art" aria-hidden="true"><div className="signal-grid"/><div className="signal-orbit orbit-a"/><div className="signal-orbit orbit-b"/><div className="signal-orbit orbit-c"/><div className="signal-center"><RadarMark /></div><span className="signal-point point-a"/><span className="signal-point point-b"/><span className="signal-point point-c"/><span className="signal-readout readout-a">SOURCE / OPEN</span><span className="signal-readout readout-b">NO SYNTHESIS</span></div>
            <div className="intro-foot"><span><b>{successfulFeeds.toLocaleString("ar-MA")}</b> مصادر متاحة الآن</span><i /><span>تحديث تلقائي كل 15 دقيقة</span><i /><span>{lastUpdated ? `آخر فحص ${new Intl.DateTimeFormat("ar-MA", { hour: "2-digit", minute: "2-digit" }).format(new Date(lastUpdated))}` : "بانتظار أول تحديث"}</span></div>
          </section>

          {view === "briefing" && <>
            <section className="metrics-row" aria-label="حالة المصادر">
              <article className="metric"><span className="metric-icon metric-icon-green">◉</span><div><small>مصادر تُحدّث بنجاح</small><strong>{loadState === "ready" ? `${successfulFeeds} / ${totalFeeds}` : "—"}</strong></div><span className="metric-meta">خلاصات أصلية</span></article>
              <article className="metric"><span className="metric-icon metric-icon-blue">▤</span><div><small>مواد في النشرة</small><strong>{loadState === "ready" ? allItems.length.toLocaleString("ar-MA") : "—"}</strong></div><span className="metric-meta">من الجهات المدرجة</span></article>
              <article className="metric"><span className="metric-icon metric-icon-gold">☆</span><div><small>مواد محفوظة</small><strong>{favorites.length.toLocaleString("ar-MA")}</strong></div><span className="metric-meta">على هذا الجهاز</span></article>
            </section>

            <section className="feed-section">
              <div className="feed-head"><div><div className="eyebrow"><span className="eyebrow-dash" /> تغطية أولية</div><h2>النشرة العامة</h2><p>مواد منشورة من الجهات نفسها؛ افتح الأصل لقراءة النص الكامل وسياقه.</p></div><div className="feed-head-note"><span className="feed-head-dot" />{loadState === "loading" ? "جارٍ الاتصال بالمصادر" : loadState === "ready" ? `${successfulFeeds} من ${totalFeeds} استجاب` : "لم يبدأ التحديث"}</div></div>
              <div className="feed-controls">
                <label className="global-search"><span>⌕</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="ابحث في العناوين والمقتطفات…" /><kbd>Ctrl K</kbd></label>
                <div className="country-tabs"><button className={countryFilter === "all" ? "country-tab selected" : "country-tab"} onClick={() => chosenFilter("all")}>الكل <span>{allItems.length}</span></button>{PUBLIC_FEEDS.map((feed) => <button key={feed.id} className={countryFilter === feed.id ? "country-tab selected" : "country-tab"} onClick={() => chosenFilter(feed.id)}>{feed.country}</button>)}</div>
              </div>
              {results.some((result) => result.stale) && <div className="stale-notice"><span>◷</span><p><b>نسخة محفوظة للقراءة دون اتصال.</b> قد تكون بعض المواد قديمة؛ وقت الفحص السابق ظاهر في التذييل.</p></div>}
              <div className="feed-layout">
                <div className="timeline-column">
                  {loadState === "loading" && results.length === 0 && <div className="loading-panel"><span className="large-spinner"/><strong>نفتح قنوات المصادر العلنية</strong><small>نحمّل المواد من الجهات المدرجة. قد يستغرق الاتصال لحظات.</small></div>}
                  {loadState === "ready" && visibleItems.length > 0 && <div className="story-list">{visibleItems.map((item) => {
                    const feed = PUBLIC_FEEDS.find((source) => source.id === item.feedId)!;
                    const isSaved = favorites.includes(item.id);
                    return <article className={`story-card ${selected?.id === item.id ? "story-selected" : ""}`} key={item.id} onClick={() => setSelected(item)}>
                      <div className="story-rail"><CountrySeal code={item.countryCode} tone={feed.tone}/><span /></div>
                      <div className="story-body"><div className="story-meta"><span className="story-source">{item.organization}</span><span className="source-class">{getSourceLabel(item)}</span><span className="story-dot">·</span><time>{formatDate(item.publishedAt, true)}</time></div><button className="story-title" dir="auto" onClick={(event) => { event.stopPropagation(); setSelected(item); }}>{item.title}</button>{item.excerpt && <p className="story-excerpt" dir="auto">{item.excerpt}</p>}<div className="story-bottom"><span className="language-tag">{item.language}</span><a href={item.url} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>النص الأصلي <OpenIcon small /></a><div className="story-quick"><button title={isSaved ? "إزالة من المحفوظات" : "حفظ"} onClick={(event) => { event.stopPropagation(); toggleFavorite(item.id); notify(isSaved ? "أزيلت المادة من المحفوظات" : "حُفظت المادة على الجهاز"); }}>{isSaved ? "★" : "☆"}</button><button title="عرض التفاصيل" onClick={(event) => { event.stopPropagation(); setSelected(item); }}>⋯</button></div></div></div>
                    </article>;
                  })}</div>}
                  {loadState === "ready" && visibleItems.length === 0 && <div className="empty-feed"><span>⌕</span><strong>{search ? "لا نتائج لهذا البحث" : "لا توجد مواد من هذا المصدر الآن"}</strong><p>{search ? "جرّب كلمات أخرى أو اختر مصدرًا مختلفًا." : "اضغط تحديث لإعادة فحص الخلاصة، أو افتح المصدر الرسمي مباشرة."}</p><button onClick={refresh}>إعادة الفحص <span>↻</span></button></div>}
                  {loadState === "ready" && results.some((result) => result.error) && <div className="source-warning"><span>!</span><div><b>بعض المصادر لم تستجب</b><p>{results.filter((result) => result.error).map((result) => result.feed.country).join("، ")} — نعرض فقط المواد التي أمكن جلبها، ولا نستبدلها بمحتوى مخمّن.</p></div><button onClick={refresh}>إعادة المحاولة</button></div>}
                  <div className="feed-footnote"><span>ⓘ</span> العنوان والمقتطف من الناشر الأصلي؛ انتقل إلى رابط المصدر للسياق الكامل. لا تعني أسبقية النشر صحة الادعاء.</div>
                </div>
                <aside className="intel-column">
                  <section className="side-module source-health"><div className="module-head"><div><span className="module-kicker">الحالة الآن</span><h3>قنوات المصدر</h3></div><button onClick={refresh} aria-label="تحديث القنوات">↻</button></div><div className="health-list">{PUBLIC_FEEDS.map((feed) => { const result = results.find((entry) => entry.feed.id === feed.id); const count = result?.items.length ?? 0; return <button key={feed.id} className="health-row" onClick={() => chosenFilter(feed.id)}><CountrySeal code={feed.countryCode} tone={feed.tone}/><span className="health-copy"><b>{feed.country}</b><small>{feed.language} · {feed.format === "html" ? "صفحة رسمية" : "خلاصة عامة"}</small></span><span className={result?.error ? "health-status fail" : result?.stale ? "health-status stale" : result ? "health-status good" : "health-status pending"}>{loadState === "loading" && !result ? "···" : result?.error ? "تعذر" : result?.stale ? "مخزّنة" : result ? `${count} مادة` : "انتظار"}</span></button>; })}</div><div className="module-foot">المحتوى يأتي من النطاق الأصلي لكل جهة.</div></section>
                  <section className="side-module broadcast-module"><div className="module-head"><div><span className="module-kicker">مواد صوتية ومرئية عامة</span><h3>افتح البث الأصلي</h3></div><span className="broadcast-mark">◖</span></div>{publicBroadcasts.map((item) => <a className="broadcast-link" key={item.title} href={item.url} target="_blank" rel="noreferrer"><span className={`broadcast-seal tone-${item.tone}`}>{item.symbol}</span><span><b>{item.title}</b><small>{item.subtitle}</small></span><OpenIcon small /></a>)}<p className="module-disclaimer">هذه روابط إلى صفحات بث عامة، وليست رصدًا لاتصالات خاصة أو بثًا مضمون الاستمرار.</p></section>
                  <section className="quote-module"><span className="quote-mark">“</span><p>اقرأ النص الكامل، وتحقق من التاريخ والسياق قبل بناء استنتاج.</p><button onClick={() => setView("method")}>منهجية الرصد <span>←</span></button></section>
                </aside>
              </div>
            </section>
          </>}

          {view === "saved" && <section className="secondary-view"><div className="secondary-heading"><div><div className="eyebrow"><span className="eyebrow-dash"/> مكتبتك الشخصية</div><h2>المحفوظات</h2><p>مواد علنية حفظتها للعودة إليها. تُخزّن القائمة على هذا الجهاز فقط.</p></div><span className="secondary-count">{favorites.length.toLocaleString("ar-MA")} <small>مادة</small></span></div><div className="story-list">{visibleItems.map((item) => <article className="story-card" key={item.id} onClick={() => setSelected(item)}><div className="story-rail"><CountrySeal code={item.countryCode} tone={getFeedTone(item.feedId)}/><span/></div><div className="story-body"><div className="story-meta"><span className="story-source">{item.organization}</span><time>{formatDate(item.publishedAt, true)}</time></div><button className="story-title" dir="auto" onClick={() => setSelected(item)}>{item.title}</button><p className="story-excerpt" dir="auto">{item.excerpt}</p><div className="story-bottom"><span className="language-tag">{item.language}</span><a href={item.url} target="_blank" rel="noreferrer">النص الأصلي <OpenIcon small /></a><div className="story-quick"><button title="إزالة من المحفوظات" onClick={() => toggleFavorite(item.id)}>★</button></div></div></div></article>)}</div>{visibleItems.length === 0 && <div className="empty-feed"><span>☆</span><strong>قائمتك فارغة الآن</strong><p>من النشرة، اضغط النجمة بجانب أي مادة لحفظها هنا.</p><button onClick={() => setView("briefing")}>العودة إلى النشرة <span>←</span></button></div>}</section>}

          {view === "sources" && <section className="secondary-view"><div className="secondary-heading"><div><div className="eyebrow"><span className="eyebrow-dash"/> دليل التتبّع</div><h2>مصادر الرصد</h2><p>كل بطاقة تفتح جهة النشر نفسها؛ حالة الوصول تتغير بحسب الشبكة وقيود الموقع.</p></div><button className="refresh-button" onClick={refresh}><span className="refresh-icon">↻</span> فحص المصادر</button></div><div className="source-directory">{PUBLIC_FEEDS.map((feed) => { const result = results.find((entry) => entry.feed.id === feed.id); return <article className="directory-card" key={feed.id}><div className="directory-top"><CountrySeal code={feed.countryCode} tone={feed.tone}/><span className={result?.error ? "directory-state unavailable" : result?.stale ? "directory-state stale" : result ? "directory-state active" : "directory-state"}><i/>{result?.error ? "تعذّر التحديث" : result?.stale ? "نسخة محفوظة" : result ? "اتصال ناجح" : "بانتظار الفحص"}</span></div><span className="directory-country">{feed.country} · {feed.language}</span><h3>{feed.organization}</h3><p>{feed.description}</p><div className="directory-type"><span>{feed.format === "html" ? "صفحة أصلية" : feed.format.toUpperCase()}</span><span>يُفحص كل 15 دقيقة</span></div><a className="directory-open" href={feed.siteUrl} target="_blank" rel="noreferrer">فتح موقع الناشر <OpenIcon small /></a></article>; })}</div><div className="broadcast-directory"><div><span className="eyebrow"><span className="eyebrow-dash"/> بث ومواد مرئية</span><h3>استمع وشاهد من الناشر نفسه</h3><p>لا نتوسط في البث ولا نعيد رفعه؛ الرابط يقود إلى صفحة الجهة العلنية.</p></div>{publicBroadcasts.map((item) => <a key={item.title} href={item.url} target="_blank" rel="noreferrer"><span className={`broadcast-seal tone-${item.tone}`}>{item.symbol}</span><span><b>{item.title}</b><small>{item.subtitle}</small></span><OpenIcon small /></a>)}</div></section>}

          {view === "method" && <section className="secondary-view method-view"><div className="secondary-heading"><div><div className="eyebrow"><span className="eyebrow-dash"/> شفافية وحدود واضحة</div><h2>ما الذي يفعله مِرصد؟</h2><p>أداة لتقريب المصادر الأولية العامة، لا محركًا لإثبات الحقيقة ولا نظام إنذار.</p></div></div><div className="method-grid"><article><span className="method-number">01</span><h3>المصدر قبل التعليق</h3><p>نجلب العناوين والمقتطفات من خلاصات أو صفحات منشورة علنًا، ونربط كل مادة بصفحتها الأصلية. لا ننشئ اقتباسات ولا نكتب ملخصات من عندنا.</p></article><article><span className="method-number">02</span><h3>الحالة لا تُخفى</h3><p>عند فشل اتصال أي جهة نظهر ذلك ونحددها. عدم ظهور مادة لا يعني عدم وجود حدث، وتأخر التحديث لا يعني عدم وقوعه.</p></article><article><span className="method-number">03</span><h3>قولٌ منشور، لا حقيقة محققة</h3><p>المصدر الأولي يثبت ما نشرته الجهة، لكنه لا يثبت وحده صحة الادعاء أو اكتمال السياق. المقارنة والتحقق مسؤولية القارئ.</p></article><article><span className="method-number">04</span><h3>خصوصية الجهاز</h3><p>المحفوظات والملاحظات تبقى في التخزين المحلي للتطبيق. لا يوجد تسجيل دخول أو رفع تلقائي لملاحظاتك.</p></article></div><div className="limits-panel"><span>!</span><div><b>حدود تقنية مهمة</b><p>مِرصد لا يلتقط ترددات الراديو، ولا يعترض الاتصالات الخاصة أو المشفرة، ولا يعمل كنظام طوارئ. البثوث المتاحة هنا منشورة للعامة من الجهات نفسها.</p></div></div></section>}

          <footer className="app-footer"><span>مِرصد <i>·</i> إصدار تجريبي</span><span>{lastUpdated ? `آخر فحص ${formatDate(lastUpdated, true)}` : "لم يتم التحديث بعد"}</span><span>لا حساب · لا تتبّع · لا معلومات مخترعة</span></footer>
        </div>
      </section>

      {selected && <div className="detail-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelected(null); }}><aside className="detail-drawer" dir="rtl"><div className="drawer-top"><span className="drawer-label">مادة منشورة علنًا</span><button onClick={() => setSelected(null)} aria-label="إغلاق">×</button></div><div className="drawer-source"><CountrySeal code={selected.countryCode} tone={getFeedTone(selected.feedId)}/><span><b>{selected.organization}</b><small>{selected.country} · {selected.language}</small></span></div><div className="drawer-divider"/><div className="drawer-metadata"><span>تاريخ النشر</span><b>{formatDate(selected.publishedAt)}</b><span>نوع المصدر</span><b>{getSourceLabel(selected)}</b></div><h2 className="drawer-title">{selected.title}</h2>{selected.excerpt ? <div className="drawer-excerpt"><span>مقتطف الناشر</span><p>{selected.excerpt}</p></div> : <div className="drawer-excerpt"><span>المادة الأصلية</span><p>لا يتضمن موجز المصدر مقتطفًا نصيًا. افتح صفحة الجهة لقراءة النص الكامل.</p></div>}<div className="drawer-caution">المعروض مقتطف من الناشر وليس تحققًا مستقلًا. راجع النص الكامل والسياق الأصلي.</div><div className="drawer-actions"><a className="primary-action" href={selected.url} target="_blank" rel="noreferrer">افتح النص الأصلي <OpenIcon small /></a><button onClick={() => toggleFavorite(selected.id)}>{favorites.includes(selected.id) ? "★ محفوظة" : "☆ احفظها"}</button><button onClick={() => speak(selected)}>{speakState ? "■ أوقف القراءة" : "◖ استمع للمقتطف"}</button><button onClick={() => openNoteFor(selected)}>＋ أضف ملاحظة</button></div></aside></div>}

      {showNote && <div className="modal-layer" onMouseDown={(event) => { if (event.target === event.currentTarget) setShowNote(false); }}><form className="note-form" onSubmit={addNote}><div className="note-form-head"><div><span className="eyebrow">ملاحظات محلية</span><h2>أضف إلى دفتر التحقق</h2></div><button type="button" onClick={() => setShowNote(false)}>×</button></div><label>العنوان<input name="title" defaultValue={selected?.title || ""} placeholder="عنوان الملاحظة" required/></label><label>الجهة<input name="source" defaultValue={selected?.organization || ""} placeholder="اسم الناشر"/></label><label>رابط المصدر<input name="url" type="url" defaultValue={selected?.url || ""} placeholder="https://…"/></label><label>ملاحظتك<textarea name="text" rows={5} placeholder="دوّن الاقتباس أو ما تريد التحقق منه…" required/></label><div className="local-only-note">🔒 تُحفظ محليًا على هذا الجهاز فقط.</div><button className="primary-action note-submit" type="submit">حفظ الملاحظة <span>←</span></button></form></div>}
      {toast && <div className="toast-message"><span>✓</span>{toast}</div>}
      {menuOpen && <button className="menu-scrim" aria-label="إغلاق القائمة" onClick={() => setMenuOpen(false)} />}
    </main>
  );
}
