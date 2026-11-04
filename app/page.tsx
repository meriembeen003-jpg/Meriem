"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Browser } from "@capacitor/browser";
import { Capacitor } from "@capacitor/core";
import { loadPublicFeed, PUBLIC_FEEDS, type FeedFormat, type FeedResult, type PublicFeed, type PublicItem } from "./lib/feeds";

type View = "briefing" | "saved" | "notes" | "radar" | "sources" | "method";
type Note = { id: string; title: string; source: string; url: string; text: string; createdAt: string };
type InstallPromptEvent = Event & { prompt: () => Promise<void> };

const viewItems: { id: View; label: string; icon: string }[] = [
  { id: "briefing", label: "النشرة", icon: "▥" },
  { id: "saved", label: "المحفوظات", icon: "☆" },
  { id: "notes", label: "ملاحظاتي", icon: "✎" },
  { id: "radar", label: "الرادار", icon: "◉" },
  { id: "sources", label: "المصادر", icon: "⌘" },
  { id: "method", label: "المنهجية", icon: "i" },
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

function getFeedTone(feedId: string, feeds: PublicFeed[] = PUBLIC_FEEDS) {
  return feeds.find((feed) => feed.id === feedId)?.tone ?? "blue";
}

function getSourceLabel(item: PublicItem) {
  if (item.countryCode === "UN") return "مؤسسة دولية";
  if (item.countryCode === "CUSTOM") return "مصدر أضافه المستخدم";
  return "مصدر حكومي مباشر";
}

function stableSourceId(value: string) {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) hash = Math.imul(hash ^ value.charCodeAt(index), 16777619);
  return `custom-${(hash >>> 0).toString(36)}`;
}

function safeHttpsUrl(value: string) {
  try {
    const url = new URL(value);
    if (url.protocol !== "https:") return "";
    const hostname = url.hostname.toLowerCase();
    const host = hostname.startsWith("[") ? hostname.slice(1, -1) : hostname;
    const normalizedHost = host.endsWith(".") ? host.slice(0, -1) : host;
    if (normalizedHost === "localhost" || normalizedHost.endsWith(".localhost") || normalizedHost.endsWith(".local") || normalizedHost.endsWith(".internal")) return "";
    const octets = normalizedHost.split(".");
    if (octets.length === 4 && octets.every((part) => part.length > 0 && Number.isInteger(Number(part)) && Number(part) <= 255)) {
      const [a, b] = octets.map(Number);
      if (a === 0 || a === 10 || a === 127 || (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168) || (a === 100 && b >= 64 && b <= 127) || a >= 224) return "";
    }
    if (host.startsWith("::") || host.startsWith("fc") || host.startsWith("fd") || host.startsWith("fe80") || host.startsWith("ff")) return "";
    return url.href;
  } catch { return ""; }
}

function normalizeSearch(value: string) {
  return value.normalize("NFD").replace(/\p{M}/gu, "").replace(/[أإآٱ]/g, "ا").replace(/ى/g, "ي").replace(/ة/g, "ه").replace(/ـ/g, "").toLocaleLowerCase();
}

function getMatchedTerms(item: PublicItem, terms: string[]) {
  const body = normalizeSearch(`${item.title} ${item.excerpt}`);
  return terms.filter((term) => body.includes(normalizeSearch(term)));
}

function isPublicItem(value: unknown): value is PublicItem {
  if (!value || typeof value !== "object") return false;
  const item = value as Partial<PublicItem>;
  return typeof item.id === "string" && typeof item.feedId === "string" && typeof item.title === "string" &&
    typeof item.excerpt === "string" && typeof item.organization === "string" && typeof item.country === "string" &&
    typeof item.countryCode === "string" && typeof item.language === "string" && !!safeHttpsUrl(item.url ?? "") &&
    (item.publishedAt === null || typeof item.publishedAt === "string");
}

export default function Home() {
  const [view, setView] = useState<View>("briefing");
  const [results, setResults] = useState<FeedResult[]>([]);
  const [customFeeds, setCustomFeeds] = useState<PublicFeed[]>([]);
  const [sourceFormOpen, setSourceFormOpen] = useState(false);
  const resultsRef = useRef<FeedResult[]>([]);
  const allFeeds = useMemo(() => [...PUBLIC_FEEDS, ...customFeeds], [customFeeds]);
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready">("idle");
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [countryFilter, setCountryFilter] = useState("all");
  const [favorites, setFavorites] = useState<string[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [watchTerms, setWatchTerms] = useState<string[]>([]);
  const [watchInput, setWatchInput] = useState("");
  const [refreshMinutes, setRefreshMinutes] = useState(15);
  const opmlPicker = useRef<HTMLInputElement>(null);
  const [preferencesReady, setPreferencesReady] = useState(false);
  const [selected, setSelected] = useState<PublicItem | null>(null);
  const [toast, setToast] = useState("");
  const [showNote, setShowNote] = useState(false);
  const [online, setOnline] = useState(true);
  const [installPrompt, setInstallPrompt] = useState<InstallPromptEvent | null>(null);
  const [speakState, setSpeakState] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const toastTimer = useRef<number | null>(null);
  const notify = useCallback((message: string) => {
    setToast(message);
    if (toastTimer.current !== null) window.clearTimeout(toastTimer.current);
    toastTimer.current = window.setTimeout(() => setToast(""), 3200);
  }, []);

  const refresh = useCallback(async () => {
    setLoadState("loading");
    const fetched = await Promise.all(allFeeds.map(loadPublicFeed));
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
  }, [allFeeds]);

  useEffect(() => {
    const restoreTimer = window.setTimeout(() => {
      try {
        const storedFavorites = JSON.parse(localStorage.getItem("marsad-favorites-v2") || "[]") as unknown;
        setFavorites(Array.isArray(storedFavorites) ? storedFavorites.filter((id): id is string => typeof id === "string").slice(0, 2000) : []);
        const storedNotes = JSON.parse(localStorage.getItem("marsad-notes-v2") || "[]") as unknown;
        setNotes(Array.isArray(storedNotes) ? storedNotes.filter((note): note is Note => !!note && typeof note === "object" && typeof note.id === "string" && typeof note.title === "string" && typeof note.text === "string" && typeof note.createdAt === "string").slice(0, 200) : []);
        const storedWatchTerms = JSON.parse(localStorage.getItem("marsad-watch-terms-v1") || "[]") as unknown;
        setWatchTerms(Array.isArray(storedWatchTerms) ? storedWatchTerms.filter((term): term is string => typeof term === "string" && term.trim().length > 0).slice(0, 30) : []);
        const storedRefresh = Number(localStorage.getItem("marsad-refresh-minutes-v1"));
        if ([5, 15, 30, 60].includes(storedRefresh)) setRefreshMinutes(storedRefresh);
        const storedCustom = JSON.parse(localStorage.getItem("marsad-custom-feeds-v1") || "[]") as unknown;
        const validCustom = Array.isArray(storedCustom) ? storedCustom.filter((value): value is PublicFeed => {
          if (!value || typeof value !== "object") return false;
          const feed = value as Partial<PublicFeed>;
          return typeof feed.id === "string" && typeof feed.country === "string" && typeof feed.organization === "string" &&
            typeof feed.language === "string" && (feed.format === "rss" || feed.format === "atom") &&
            !!safeHttpsUrl(feed.feedUrl ?? "") && !!safeHttpsUrl(feed.siteUrl ?? "");
        }).slice(0, 20) : [];
        setCustomFeeds(validCustom);
        const cached = JSON.parse(localStorage.getItem("marsad-feed-cache-v2") || "null") as { checkedAt?: string; results?: FeedResult[] } | null;
        if (Array.isArray(cached?.results) && cached.results.length) {
          const known = new Set([...PUBLIC_FEEDS, ...validCustom].map((feed) => feed.id));
          const restored = cached.results.filter((result) => !!result && typeof result === "object" && !!result.feed && known.has(result.feed.id) && Array.isArray(result.items)).map((result) => ({ ...result, items: result.items.filter(isPublicItem), stale: true })).filter((result) => result.items.length > 0);
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
    const interval = window.setInterval(refresh, refreshMinutes * 60 * 1000);
    return () => {
      window.removeEventListener("online", onlineHandler);
      window.removeEventListener("offline", offlineHandler);
      window.removeEventListener("beforeinstallprompt", installHandler);
      window.clearTimeout(restoreTimer);
      window.clearTimeout(initialRefreshTimer);
      window.clearInterval(interval);
    };
  }, [refresh, refreshMinutes]);

  useEffect(() => { if (preferencesReady) { try { localStorage.setItem("marsad-favorites-v2", JSON.stringify(favorites)); } catch { /* storage can be disabled by the device */ } } }, [favorites, preferencesReady]);
  useEffect(() => { if (preferencesReady) { try { localStorage.setItem("marsad-notes-v2", JSON.stringify(notes)); } catch { /* storage can be full or disabled */ } } }, [notes, preferencesReady]);
  useEffect(() => { if (preferencesReady) { try { localStorage.setItem("marsad-custom-feeds-v1", JSON.stringify(customFeeds)); } catch { /* storage can be disabled by the device */ } } }, [customFeeds, preferencesReady]);
  useEffect(() => { if (preferencesReady) { try { localStorage.setItem("marsad-watch-terms-v1", JSON.stringify(watchTerms)); } catch { /* storage can be disabled by the device */ } } }, [watchTerms, preferencesReady]);
  useEffect(() => { if (preferencesReady) { try { localStorage.setItem("marsad-refresh-minutes-v1", String(refreshMinutes)); } catch { /* storage can be disabled */ } } }, [refreshMinutes, preferencesReady]);

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

  const watchedItems = useMemo(() => allItems.filter((item) => getMatchedTerms(item, watchTerms).length > 0), [allItems, watchTerms]);

  const visibleItems = useMemo(() => allItems.filter((item) => {
    const matchesCountry = countryFilter === "all" || item.feedId === countryFilter;
    const matchesSaved = view !== "saved" || favorites.includes(item.id);
    const query = normalizeSearch(search.trim());
    const matchesSearch = !query || normalizeSearch(`${item.title} ${item.excerpt} ${item.organization} ${item.country}`).includes(query);
    return matchesCountry && matchesSaved && matchesSearch;
  }), [allItems, countryFilter, favorites, search, view]);

  const successfulFeeds = results.filter((result) => !result.error && !result.stale && result.items.length).length;
  const totalFeeds = allFeeds.length;
  const toggleFavorite = (id: string) => setFavorites((current) => current.includes(id) ? current.filter((item) => item !== id) : [id, ...current]);

  const addNote = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = String(form.get("title") || "").trim();
    const text = String(form.get("text") || "").trim();
    if (!title || !text) return;
    setNotes((current) => [{ id: crypto.randomUUID(), title, source: String(form.get("source") || "مصدر عام"), url: safeHttpsUrl(String(form.get("url") || "")), text, createdAt: new Date().toISOString() }, ...current].slice(0, 200));
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

  const exportOpml = () => {
    const escapeXml = (value: string) => value.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    const outlines = allFeeds.filter((feed) => feed.format !== "html").map((feed) => `    <outline text="${escapeXml(feed.organization)}" title="${escapeXml(feed.organization)}" type="${feed.format}" xmlUrl="${escapeXml(feed.feedUrl)}" htmlUrl="${escapeXml(feed.siteUrl)}"/>`).join("\n");
    const content = `<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0"><head><title>Subscriptions — Mirsad</title></head><body>\n${outlines}\n</body></opml>`;
    const url = URL.createObjectURL(new Blob([content], { type: "application/xml;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "mirsad-subscriptions.opml";
    anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const importOpml = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      if (file.size > 1_000_000) throw new Error("حجم ملف OPML أكبر من 1 ميغابايت.");
      const document = new DOMParser().parseFromString(await file.text(), "application/xml");
      if (document.querySelector("parsererror") || document.documentElement.tagName.toLowerCase() !== "opml") throw new Error("الملف ليس OPML صالحًا.");
      const knownUrls = new Set(allFeeds.map((feed) => feed.feedUrl));
      const imported: PublicFeed[] = [];
      for (const outline of Array.from(document.getElementsByTagName("outline"))) {
        const feedUrl = safeHttpsUrl(outline.getAttribute("xmlUrl") || outline.getAttribute("xmlurl") || "");
        if (!feedUrl || knownUrls.has(feedUrl) || imported.length >= 20 - customFeeds.length) continue;
        const siteUrl = safeHttpsUrl(outline.getAttribute("htmlUrl") || outline.getAttribute("htmlurl") || "") || new URL(feedUrl).origin;
        const title = (outline.getAttribute("title") || outline.getAttribute("text") || new URL(feedUrl).hostname).trim().slice(0, 100);
        const type = `${outline.getAttribute("type") || ""} ${feedUrl}`.toLowerCase();
        imported.push({ id: stableSourceId(feedUrl), country: "مستورد من OPML", countryCode: "CUSTOM", organization: title || new URL(feedUrl).hostname, description: "خلاصة مستوردة محليًا من ملف OPML؛ تحقق من هوية الناشر.", language: "لغة المصدر", format: type.includes("atom") ? "atom" : "rss", feedUrl, siteUrl, tone: "amber" });
        knownUrls.add(feedUrl);
      }
      setCustomFeeds((current) => [...current, ...imported].slice(0, 20 + PUBLIC_FEEDS.length));
      notify(imported.length ? `استوردت ${imported.length} خلاصة` : "لم يُعثر على خلاصات HTTPS جديدة ضمن حدّ 20 مصدرًا");
    } catch (error) {
      notify(error instanceof Error ? error.message : "تعذّر استيراد ملف OPML");
    } finally {
      event.target.value = "";
    }
  };

  const addCustomSource = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const organization = String(form.get("organization") || "").trim().slice(0, 100);
    const country = String(form.get("country") || "مصادر أضفتها").trim().slice(0, 60) || "مصادر أضفتها";
    const language = String(form.get("language") || "غير محددة").trim().slice(0, 40) || "غير محددة";
    const rawFeedUrl = String(form.get("feedUrl") || "").trim();
    const rawSiteUrl = String(form.get("siteUrl") || "").trim() || rawFeedUrl;
    if (!organization) { notify("اكتب اسم الجهة أولًا"); return; }
    try {
      const feedUrl = new URL(rawFeedUrl);
      const siteUrl = new URL(rawSiteUrl);
      if (feedUrl.protocol !== "https:" || siteUrl.protocol !== "https:" || !safeHttpsUrl(feedUrl.href) || !safeHttpsUrl(siteUrl.href)) throw new Error("https");
      const id = stableSourceId(feedUrl.href);
      if (allFeeds.some((feed) => feed.id === id || feed.feedUrl === feedUrl.href)) { notify("هذا المصدر مضاف بالفعل"); return; }
      if (customFeeds.length >= 20) { notify("وصلت إلى الحد الأقصى: 20 مصدرًا مخصصًا"); return; }
      const format = String(form.get("format")) as FeedFormat;
      if (format !== "rss" && format !== "atom") { notify("اختر RSS أو Atom"); return; }
      const source: PublicFeed = {
        id, country, countryCode: "CUSTOM", organization, description: "مصدر أضافه المستخدم. تحقق من الجهة والرابط قبل الاعتماد عليه.",
        language, format, feedUrl: feedUrl.href, siteUrl: siteUrl.href, tone: "amber",
      };
      setCustomFeeds((current) => [...current, source]);
      setSourceFormOpen(false);
      event.currentTarget.reset();
      notify("أُضيف المصدر. جارٍ فحصه؛ قد لا تسمح بعض المواقع بالاتصال المباشر.");
    } catch {
      notify("استخدم روابط HTTPS عامة؛ عناوين الشبكة المحلية غير مسموحة");
    }
  };

  const addWatchTerm = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const term = watchInput.trim().slice(0, 80);
    const normalized = normalizeSearch(term);
    if (normalized.length < 2) { notify("اكتب كلمة أو عبارة من حرفين على الأقل"); return; }
    if (watchTerms.some((saved) => normalizeSearch(saved) === normalized)) { notify("هذه العبارة موجودة في الرادار"); return; }
    if (watchTerms.length >= 30) { notify("وصلت إلى الحد الأقصى: 30 عبارة مراقبة"); return; }
    setWatchTerms((current) => [...current, term]);
    setWatchInput("");
    notify("أُضيفت العبارة؛ طابِق المواد المنشورة معها محليًا");
  };

  const removeWatchTerm = (term: string) => setWatchTerms((current) => current.filter((saved) => normalizeSearch(saved) !== normalizeSearch(term)));

  const removeCustomSource = (feedId: string) => {
    setCustomFeeds((current) => current.filter((feed) => feed.id !== feedId));
    const nextResults = resultsRef.current.filter((result) => result.feed.id !== feedId);
    resultsRef.current = nextResults;
    setResults(nextResults);
    if (countryFilter === feedId) setCountryFilter("all");
    notify("أُزيل المصدر من قائمتك المحلية");
  };

  const deleteNote = (noteId: string) => setNotes((current) => current.filter((note) => note.id !== noteId));

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
          {viewItems.map((item) => <button key={item.id} className={view === item.id ? "rail-link current" : "rail-link"} onClick={() => { setView(item.id); if (item.id === "saved") setCountryFilter("all"); setMenuOpen(false); }}><span className="rail-glyph">{item.icon}</span><span>{item.label}</span>{item.id === "saved" && favorites.length > 0 && <b>{favorites.length}</b>}{item.id === "radar" && watchedItems.length > 0 && <b>{watchedItems.length}</b>}</button>)}
        </nav>
        <div className="rail-divider" />
        <div className="rail-caption rail-caption-row"><span>تدفقات مفعّلة</span><span className="rail-count">{successfulFeeds}/{totalFeeds}</span></div>
        <div className="source-mini-list">
          {allFeeds.map((feed) => {
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
            <div className="intro-foot"><span><b>{successfulFeeds.toLocaleString("ar-MA")}</b> مصادر متاحة الآن</span><i /><span>{`تحديث تلقائي كل ${refreshMinutes} دقيقة`}</span><i /><span>{lastUpdated ? `آخر فحص ${new Intl.DateTimeFormat("ar-MA", { hour: "2-digit", minute: "2-digit" }).format(new Date(lastUpdated))}` : "بانتظار أول تحديث"}</span></div>
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
                <div className="country-tabs"><button className={countryFilter === "all" ? "country-tab selected" : "country-tab"} onClick={() => chosenFilter("all")}>الكل <span>{allItems.length}</span></button>{allFeeds.map((feed) => <button key={feed.id} className={countryFilter === feed.id ? "country-tab selected" : "country-tab"} onClick={() => chosenFilter(feed.id)}>{feed.country}</button>)}</div>
              </div>
              {results.some((result) => result.stale) && <div className="stale-notice"><span>◷</span><p><b>نسخة محفوظة للقراءة دون اتصال.</b> قد تكون بعض المواد قديمة؛ وقت الفحص السابق ظاهر في التذييل.</p></div>}
              <div className="feed-layout">
                <div className="timeline-column">
                  {loadState === "loading" && results.length === 0 && <div className="loading-panel"><span className="large-spinner"/><strong>نفتح قنوات المصادر العلنية</strong><small>نحمّل المواد من الجهات المدرجة. قد يستغرق الاتصال لحظات.</small></div>}
                  {loadState === "ready" && visibleItems.length > 0 && <div className="story-list">{visibleItems.map((item) => {
                    const feed = allFeeds.find((source) => source.id === item.feedId)!;
                    const isSaved = favorites.includes(item.id);
                    const originalUrl = safeHttpsUrl(item.url);
                    const matchedTerms = getMatchedTerms(item, watchTerms);
                    return <article className={`story-card ${selected?.id === item.id ? "story-selected" : ""}`} key={item.id}>
                      <div className="story-rail"><CountrySeal code={item.countryCode} tone={feed.tone}/><span /></div>
                      <div className="story-body"><div className="story-meta"><span className="story-source">{item.organization}</span><span className="source-class">{getSourceLabel(item)}</span>{matchedTerms.length > 0 && <span className="watch-match">رادار: {matchedTerms.slice(0, 2).join("، ")}</span>}<span className="story-dot">·</span><time>{formatDate(item.publishedAt, true)}</time></div><button className="story-title" dir="auto" onClick={(event) => { event.stopPropagation(); setSelected(item); }}>{item.title}</button>{item.excerpt && <p className="story-excerpt" dir="auto">{item.excerpt}</p>}<div className="story-bottom"><span className="language-tag">{item.language}</span>{originalUrl && <a href={originalUrl} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>النص الأصلي <OpenIcon small /></a>}<div className="story-quick"><button title={isSaved ? "إزالة من المحفوظات" : "حفظ"} onClick={(event) => { event.stopPropagation(); toggleFavorite(item.id); notify(isSaved ? "أزيلت المادة من المحفوظات" : "حُفظت المادة على الجهاز"); }}>{isSaved ? "★" : "☆"}</button><button title="عرض التفاصيل" onClick={(event) => { event.stopPropagation(); setSelected(item); }}>⋯</button></div></div></div>
                    </article>;
                  })}</div>}
                  {loadState === "ready" && visibleItems.length === 0 && <div className="empty-feed"><span>⌕</span><strong>{search ? "لا نتائج لهذا البحث" : "لا توجد مواد من هذا المصدر الآن"}</strong><p>{search ? "جرّب كلمات أخرى أو اختر مصدرًا مختلفًا." : "اضغط تحديث لإعادة فحص الخلاصة، أو افتح المصدر الرسمي مباشرة."}</p><button onClick={refresh}>إعادة الفحص <span>↻</span></button></div>}
                  {loadState === "ready" && results.some((result) => result.error) && <div className="source-warning"><span>!</span><div><b>بعض المصادر لم تستجب</b><p>{results.filter((result) => result.error).map((result) => result.feed.country).join("، ")} — نعرض فقط المواد التي أمكن جلبها، ولا نستبدلها بمحتوى مخمّن.</p></div><button onClick={refresh}>إعادة المحاولة</button></div>}
                  <div className="feed-footnote"><span>ⓘ</span> العنوان والمقتطف من الناشر الأصلي؛ انتقل إلى رابط المصدر للسياق الكامل. لا تعني أسبقية النشر صحة الادعاء.</div>
                </div>
                <aside className="intel-column">
                  <section className="side-module source-health"><div className="module-head"><div><span className="module-kicker">الحالة الآن</span><h3>قنوات المصدر</h3></div><button onClick={refresh} aria-label="تحديث القنوات">↻</button></div><div className="health-list">{allFeeds.map((feed) => { const result = results.find((entry) => entry.feed.id === feed.id); const count = result?.items.length ?? 0; return <button key={feed.id} className="health-row" onClick={() => chosenFilter(feed.id)}><CountrySeal code={feed.countryCode} tone={feed.tone}/><span className="health-copy"><b>{feed.country}</b><small>{feed.language} · {feed.format === "html" ? "صفحة رسمية" : "خلاصة عامة"}</small></span><span className={result?.error ? "health-status fail" : result?.stale ? "health-status stale" : result ? "health-status good" : "health-status pending"}>{loadState === "loading" && !result ? "···" : result?.error ? "تعذر" : result?.stale ? "مخزّنة" : result ? `${count} مادة` : "انتظار"}</span></button>; })}</div><div className="module-foot">المحتوى يأتي من النطاق الأصلي لكل جهة.</div></section>
                  <section className="side-module broadcast-module"><div className="module-head"><div><span className="module-kicker">مواد صوتية ومرئية عامة</span><h3>افتح البث الأصلي</h3></div><span className="broadcast-mark">◖</span></div>{publicBroadcasts.map((item) => <a className="broadcast-link" key={item.title} href={item.url} target="_blank" rel="noreferrer"><span className={`broadcast-seal tone-${item.tone}`}>{item.symbol}</span><span><b>{item.title}</b><small>{item.subtitle}</small></span><OpenIcon small /></a>)}<p className="module-disclaimer">هذه روابط إلى صفحات بث عامة، وليست رصدًا لاتصالات خاصة أو بثًا مضمون الاستمرار.</p></section>
                  <section className="quote-module"><span className="quote-mark">“</span><p>اقرأ النص الكامل، وتحقق من التاريخ والسياق قبل بناء استنتاج.</p><button onClick={() => setView("method")}>منهجية الرصد <span>←</span></button></section>
                </aside>
              </div>
            </section>
          </>}

          {view === "saved" && <section className="secondary-view"><div className="secondary-heading"><div><div className="eyebrow"><span className="eyebrow-dash"/> مكتبتك الشخصية</div><h2>المحفوظات</h2><p>مواد علنية حفظتها للعودة إليها. تُخزّن القائمة على هذا الجهاز فقط.</p></div><span className="secondary-count">{favorites.length.toLocaleString("ar-MA")} <small>مادة</small></span></div><div className="story-list">{visibleItems.map((item) => <article className="story-card" key={item.id}><div className="story-rail"><CountrySeal code={item.countryCode} tone={getFeedTone(item.feedId, allFeeds)}/><span/></div><div className="story-body"><div className="story-meta"><span className="story-source">{item.organization}</span><time>{formatDate(item.publishedAt, true)}</time></div><button className="story-title" dir="auto" onClick={() => setSelected(item)}>{item.title}</button><p className="story-excerpt" dir="auto">{item.excerpt}</p><div className="story-bottom"><span className="language-tag">{item.language}</span>{safeHttpsUrl(item.url) && <a href={safeHttpsUrl(item.url)} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>النص الأصلي <OpenIcon small /></a>}<div className="story-quick"><button title="إزالة من المحفوظات" onClick={(event) => { event.stopPropagation(); toggleFavorite(item.id); }}>★</button></div></div></div></article>)}</div>{visibleItems.length === 0 && <div className="empty-feed"><span>☆</span><strong>قائمتك فارغة الآن</strong><p>من النشرة، اضغط النجمة بجانب أي مادة لحفظها هنا.</p><button onClick={() => setView("briefing")}>العودة إلى النشرة <span>←</span></button></div>}</section>}

          {view === "notes" && <section className="secondary-view"><div className="secondary-heading"><div><div className="eyebrow"><span className="eyebrow-dash"/> دفتر خاص على هذا الجهاز</div><h2>ملاحظاتي</h2><p>ملاحظاتك لا تُرسل إلى أي خادم. اكتب ما تريد مراجعته أو مقارنته لاحقًا.</p></div><button className="refresh-button" onClick={() => openNoteFor(null)}>＋ ملاحظة جديدة</button></div>{notes.length > 0 ? <div className="notes-list">{notes.map((note) => <article className="note-card" key={note.id}><div className="note-card-head"><span>{note.source || "مصدر عام"}</span><time>{formatDate(note.createdAt, true)}</time></div><h3>{note.title}</h3><p>{note.text}</p><div className="note-card-actions">{safeHttpsUrl(note.url) && <a href={safeHttpsUrl(note.url)} target="_blank" rel="noreferrer">فتح الرابط المرتبط <OpenIcon small/></a>}<button onClick={() => { deleteNote(note.id); notify("حُذفت الملاحظة"); }}>حذف الملاحظة</button></div></article>)}</div> : <div className="empty-feed"><span>✎</span><strong>لا توجد ملاحظات بعد</strong><p>أنشئ ملاحظة مستقلة أو افتح مادة من النشرة ثم أضف ما تريد حفظه.</p><button onClick={() => openNoteFor(null)}>أضف أول ملاحظة <span>＋</span></button></div>}</section>}

          {view === "radar" && <section className="secondary-view radar-view"><div className="secondary-heading"><div><div className="eyebrow"><span className="eyebrow-dash"/> مراقبة محلية قابلة للتفسير</div><h2>رادار الكلمات</h2><p>أضف أسماء أو مواضيع. يطابقها التطبيق مع العناوين والمقتطفات بعد تطبيع اختلافات التشكيل والألف، دون إرسالها لأي جهة.</p></div><span className="secondary-count">{watchedItems.length.toLocaleString("ar-MA")} <small>مطابقة</small></span></div><div className="radar-settings"><div><b>وتيرة تحديث المصادر</b><small>الفحص التلقائي ما دام التطبيق مفتوحًا</small></div><label><span>كل</span><select value={refreshMinutes} onChange={(event) => setRefreshMinutes(Number(event.target.value))}><option value={5}>5 دقائق</option><option value={15}>15 دقيقة</option><option value={30}>30 دقيقة</option><option value={60}>ساعة</option></select></label></div><form className="watch-form" onSubmit={addWatchTerm}><label htmlFor="watch-term">عبارة للمراقبة</label><div><input id="watch-term" value={watchInput} onChange={(event) => setWatchInput(event.target.value)} maxLength={80} placeholder="مثال: الطاقة، اجتماع وزاري، اسم جهة…"/><button className="primary-action" type="submit">＋ أضف للرادار</button></div><small>حتى 30 عبارة · مطابقة نصية محلية وليست تنبؤًا أو تحققًا</small></form>{watchTerms.length > 0 ? <><div className="watch-term-list"><span className="watch-list-label">قائمة المراقبة</span>{watchTerms.map((term) => <button className="watch-chip" key={term} onClick={() => removeWatchTerm(term)} title={`إزالة ${term}`}><span>{term}</span><b>×</b></button>)}</div><div className="radar-results-head"><h3>المواد المطابقة</h3><span>{watchedItems.length} نتيجة من المواد المحمّلة حاليًا</span></div>{watchedItems.length > 0 ? <div className="radar-results">{watchedItems.map((item) => { const matches = getMatchedTerms(item, watchTerms); const link = safeHttpsUrl(item.url); return <article className="radar-result" key={item.id}><div className="radar-result-meta"><CountrySeal code={item.countryCode} tone={getFeedTone(item.feedId, allFeeds)}/><span><b>{item.organization}</b><small>{item.country} · {formatDate(item.publishedAt, true)}</small></span></div><button className="radar-result-title" onClick={() => setSelected(item)} dir="auto">{item.title}</button><div className="radar-result-matches">{matches.map((term) => <span key={term}>{term}</span>)}</div><div className="radar-result-foot"><span>مطابقة في نص الناشر</span>{link && <a href={link} target="_blank" rel="noreferrer">النص الأصلي <OpenIcon small/></a>}</div></article>; })}</div> : <div className="empty-feed"><span>◉</span><strong>لا تطابق العبارات مواد محمّلة حاليًا</strong><p>جرّب عبارة أوسع أو حدّث المصادر. غياب التطابق لا يعني غياب الخبر عن الجهة.</p><button onClick={refresh} disabled={loadState === "loading"}>فحص المصادر <span>↻</span></button></div>}</> : <div className="empty-feed"><span>⌕</span><strong>أنشئ رادارك الخاص</strong><p>أضف أسماء أو قضايا تريد ملاحظتها. المطابقة حتمية وواضحة، بلا ادعاء ذكاء اصطناعي.</p><button onClick={() => document.getElementById("watch-term")?.focus()}>أضف أول عبارة <span>＋</span></button></div>}<div className="radar-disclaimer">الرادار يبحث فقط في المواد التي نجح التطبيق في تحميلها. لا يمسح الإنترنت كله ولا يتنبأ بالأحداث ولا يثبت صحة الادعاءات.</div></section>}

          {view === "sources" && <section className="secondary-view"><div className="secondary-heading"><div><div className="eyebrow"><span className="eyebrow-dash"/> دليل التتبّع</div><h2>مصادر الرصد</h2><p>كل بطاقة تفتح جهة النشر نفسها؛ استورد أو صدّر خلاصات RSS/Atom بصيغة OPML. صفحة HTML لا تدخل في ملف الاشتراكات.</p></div><div className="source-heading-actions"><button className="refresh-button" onClick={refresh} disabled={loadState === "loading"}><span className="refresh-icon">↻</span> فحص المصادر</button><button className="refresh-button" onClick={() => opmlPicker.current?.click()}>استيراد OPML</button><button className="refresh-button" onClick={exportOpml}>تصدير OPML</button><button className="refresh-button add-source-button" onClick={() => setSourceFormOpen((open) => !open)}>＋ أضف خلاصة</button><input ref={opmlPicker} type="file" accept=".opml,.xml,text/xml,application/xml" hidden onChange={importOpml}/></div></div>{sourceFormOpen && <form className="source-form" onSubmit={addCustomSource}><div><b>أضف مصدرًا رسميًا تتابعه</b><p>أدخل رابط RSS أو Atom من موقع الجهة نفسه. لا نتحقق من هوية الموقع بدلًا عنك؛ افحص النطاق قبل الحفظ.</p></div><div className="source-form-grid"><label>اسم الجهة<input name="organization" required maxLength={100} placeholder="مثال: وزارة أو هيئة رسمية"/></label><label>البلد أو التصنيف<input name="country" maxLength={60} placeholder="مثال: المغرب"/></label><label>اللغة<input name="language" maxLength={40} placeholder="مثال: العربية"/></label><label>نوع الخلاصة<select name="format" defaultValue="rss"><option value="rss">RSS</option><option value="atom">Atom</option></select></label><label className="source-form-wide">رابط RSS أو Atom<input name="feedUrl" type="url" required placeholder="https://example.gov/feed.xml"/></label><label className="source-form-wide">رابط موقع الناشر<input name="siteUrl" type="url" placeholder="https://example.gov/"/></label></div><div className="source-form-actions"><span>HTTPS فقط · حتى 20 مصدرًا · التخزين محلي</span><button className="primary-action" type="submit">حفظ المصدر</button></div></form>}<div className="source-directory">{allFeeds.map((feed) => { const result = results.find((entry) => entry.feed.id === feed.id); return <article className="directory-card" key={feed.id}><div className="directory-top"><CountrySeal code={feed.countryCode} tone={feed.tone}/><span className={result?.error ? "directory-state unavailable" : result?.stale ? "directory-state stale" : result ? "directory-state active" : "directory-state"}><i/>{result?.error ? "تعذّر التحديث" : result?.stale ? "نسخة محفوظة" : result ? "اتصال ناجح" : "بانتظار الفحص"}</span></div><span className="directory-country">{feed.country} · {feed.language}</span><h3>{feed.organization}</h3><p>{feed.description}</p><div className="directory-type"><span>{feed.format === "html" ? "صفحة أصلية" : feed.format.toUpperCase()}</span><span>{`يفحص كل ${refreshMinutes} دقيقة`}</span></div>{safeHttpsUrl(feed.siteUrl) && <a className="directory-open" href={safeHttpsUrl(feed.siteUrl)} target="_blank" rel="noreferrer">فتح موقع الناشر <OpenIcon small /></a>}{feed.id.startsWith("custom-") && <button className="remove-source" onClick={() => removeCustomSource(feed.id)}>إزالة من قائمتي</button>}</article>; })}</div><div className="broadcast-directory"><div><span className="eyebrow"><span className="eyebrow-dash"/> بث ومواد مرئية</span><h3>استمع وشاهد من الناشر نفسه</h3><p>لا نتوسط في البث ولا نعيد رفعه؛ الرابط يقود إلى صفحة الجهة العلنية.</p></div>{publicBroadcasts.map((item) => <a key={item.title} href={item.url} target="_blank" rel="noreferrer"><span className={`broadcast-seal tone-${item.tone}`}>{item.symbol}</span><span><b>{item.title}</b><small>{item.subtitle}</small></span><OpenIcon small /></a>)}</div></section>}

          {view === "method" && <section className="secondary-view method-view"><div className="secondary-heading"><div><div className="eyebrow"><span className="eyebrow-dash"/> شفافية وحدود واضحة</div><h2>ما الذي يفعله مِرصد؟</h2><p>أداة لتقريب المصادر الأولية العامة، لا محركًا لإثبات الحقيقة ولا نظام إنذار.</p></div></div><div className="method-grid"><article><span className="method-number">01</span><h3>المصدر قبل التعليق</h3><p>نجلب العناوين والمقتطفات من خلاصات أو صفحات منشورة علنًا، ونربط كل مادة بصفحتها الأصلية. لا ننشئ اقتباسات ولا نكتب ملخصات من عندنا.</p></article><article><span className="method-number">02</span><h3>الحالة لا تُخفى</h3><p>عند فشل اتصال أي جهة نظهر ذلك ونحددها. عدم ظهور مادة لا يعني عدم وجود حدث، وتأخر التحديث لا يعني عدم وقوعه.</p></article><article><span className="method-number">03</span><h3>قولٌ منشور، لا حقيقة محققة</h3><p>المصدر الأولي يثبت ما نشرته الجهة، لكنه لا يثبت وحده صحة الادعاء أو اكتمال السياق. المقارنة والتحقق مسؤولية القارئ.</p></article><article><span className="method-number">04</span><h3>خصوصية الجهاز</h3><p>المحفوظات والملاحظات تبقى في التخزين المحلي للتطبيق. لا يوجد تسجيل دخول أو رفع تلقائي لملاحظاتك.</p></article></div><div className="limits-panel"><span>!</span><div><b>حدود تقنية مهمة</b><p>مِرصد لا يلتقط ترددات الراديو، ولا يعترض الاتصالات الخاصة أو المشفرة، ولا يعمل كنظام طوارئ. البثوث المتاحة هنا منشورة للعامة من الجهات نفسها.</p></div></div></section>}

          <footer className="app-footer"><span>مِرصد <i>·</i> إصدار تجريبي</span><span>{lastUpdated ? `آخر فحص ${formatDate(lastUpdated, true)}` : "لم يتم التحديث بعد"}</span><span>لا حساب · لا تتبّع · لا معلومات مخترعة</span></footer>
        </div>
      </section>

      {selected && <div className="detail-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelected(null); }}><aside className="detail-drawer" dir="rtl"><div className="drawer-top"><span className="drawer-label">مادة منشورة علنًا</span><button onClick={() => setSelected(null)} aria-label="إغلاق">×</button></div><div className="drawer-source"><CountrySeal code={selected.countryCode} tone={getFeedTone(selected.feedId, allFeeds)}/><span><b>{selected.organization}</b><small>{selected.country} · {selected.language}</small></span></div><div className="drawer-divider"/><div className="drawer-metadata"><span>تاريخ النشر</span><b>{formatDate(selected.publishedAt)}</b><span>نوع المصدر</span><b>{getSourceLabel(selected)}</b></div><h2 className="drawer-title">{selected.title}</h2>{selected.excerpt ? <div className="drawer-excerpt"><span>مقتطف الناشر</span><p>{selected.excerpt}</p></div> : <div className="drawer-excerpt"><span>المادة الأصلية</span><p>لا يتضمن موجز المصدر مقتطفًا نصيًا. افتح صفحة الجهة لقراءة النص الكامل.</p></div>}<div className="drawer-caution">المعروض مقتطف من الناشر وليس تحققًا مستقلًا. راجع النص الكامل والسياق الأصلي.</div><div className="drawer-actions">{safeHttpsUrl(selected.url) ? <a className="primary-action" href={safeHttpsUrl(selected.url)} target="_blank" rel="noreferrer">افتح النص الأصلي <OpenIcon small /></a> : <span className="primary-action">رابط المصدر غير متاح</span>}<button onClick={() => toggleFavorite(selected.id)}>{favorites.includes(selected.id) ? "★ محفوظة" : "☆ احفظها"}</button><button onClick={() => speak(selected)}>{speakState ? "■ أوقف القراءة" : "◖ استمع للمقتطف"}</button><button onClick={() => openNoteFor(selected)}>＋ أضف ملاحظة</button></div></aside></div>}

      {showNote && <div className="modal-layer" onMouseDown={(event) => { if (event.target === event.currentTarget) setShowNote(false); }}><form className="note-form" onSubmit={addNote}><div className="note-form-head"><div><span className="eyebrow">ملاحظات محلية</span><h2>أضف إلى دفتر التحقق</h2></div><button type="button" onClick={() => setShowNote(false)}>×</button></div><label>العنوان<input name="title" defaultValue={selected?.title || ""} placeholder="عنوان الملاحظة" required/></label><label>الجهة<input name="source" defaultValue={selected?.organization || ""} placeholder="اسم الناشر"/></label><label>رابط المصدر<input name="url" type="url" defaultValue={selected?.url || ""} placeholder="https://…"/></label><label>ملاحظتك<textarea name="text" rows={5} placeholder="دوّن الاقتباس أو ما تريد التحقق منه…" required/></label><div className="local-only-note">🔒 تُحفظ محليًا على هذا الجهاز فقط.</div><button className="primary-action note-submit" type="submit">حفظ الملاحظة <span>←</span></button></form></div>}
      {toast && <div className="toast-message"><span>✓</span>{toast}</div>}
      {menuOpen && <button className="menu-scrim" aria-label="إغلاق القائمة" onClick={() => setMenuOpen(false)} />}
    </main>
  );
}
