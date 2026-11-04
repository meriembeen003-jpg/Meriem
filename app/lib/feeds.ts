import { Capacitor, CapacitorHttp } from "@capacitor/core";

export type FeedFormat = "rss" | "atom" | "html";
export type PublicFeed = {
  id: string;
  country: string;
  countryCode: string;
  organization: string;
  description: string;
  language: string;
  format: FeedFormat;
  feedUrl: string;
  siteUrl: string;
  tone: "mint" | "blue" | "amber" | "rose" | "violet";
};

export type PublicItem = {
  id: string;
  feedId: string;
  country: string;
  countryCode: string;
  organization: string;
  language: string;
  title: string;
  excerpt: string;
  url: string;
  publishedAt: string | null;
  category?: string;
};

export const PUBLIC_FEEDS: PublicFeed[] = [
  {
    id: "morocco",
    country: "المغرب",
    countryCode: "MA",
    organization: "البوابة الرسمية للمغرب",
    description: "أخبار وبلاغات منشورة على البوابة الوطنية.",
    language: "العربية",
    format: "html",
    feedUrl: "https://maroc.ma/ar",
    siteUrl: "https://maroc.ma/ar",
    tone: "mint",
  },
  {
    id: "uk",
    country: "المملكة المتحدة",
    countryCode: "GB",
    organization: "GOV.UK · الحكومة البريطانية",
    description: "إعلانات وبيانات وخطابات حكومية رسمية.",
    language: "English",
    format: "atom",
    feedUrl: "https://www.gov.uk/search/news-and-communications.atom",
    siteUrl: "https://www.gov.uk/search/news-and-communications",
    tone: "blue",
  },
  {
    id: "france",
    country: "فرنسا",
    countryCode: "FR",
    organization: "موقع الحكومة الفرنسية",
    description: "بلاغات حكومية ومقاطع إحاطة منشورة.",
    language: "Français",
    format: "rss",
    feedUrl: "https://www.info.gouv.fr/rss/actualites.xml",
    siteUrl: "https://www.info.gouv.fr/toute-l-actualite",
    tone: "blue",
  },
  {
    id: "us",
    country: "الولايات المتحدة",
    countryCode: "US",
    organization: "The White House · البيت الأبيض",
    description: "بيانات وإعلانات منشورة من البيت الأبيض.",
    language: "English",
    format: "rss",
    feedUrl: "https://www.whitehouse.gov/news/feed/",
    siteUrl: "https://www.whitehouse.gov/news/",
    tone: "rose",
  },
  {
    id: "un",
    country: "الأمم المتحدة",
    countryCode: "UN",
    organization: "UN News · أخبار الأمم المتحدة",
    description: "تغطية أممية؛ ليست بيانًا صادرًا عن حكومة وطنية.",
    language: "English",
    format: "rss",
    feedUrl: "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    siteUrl: "https://news.un.org/en/",
    tone: "violet",
  },
];

export type FeedResult = {
  feed: PublicFeed;
  items: PublicItem[];
  error?: string;
  stale?: boolean;
};

const cleanText = (value: string) => value.replace(/<!\[CDATA\[|\]\]>/g, "").replace(/\s+/g, " ").trim();

function htmlText(value: string) {
  const doc = new DOMParser().parseFromString(value, "text/html");
  return cleanText(doc.body.textContent ?? "");
}

function readNodeText(parent: Element, selectors: string[]) {
  for (const selector of selectors) {
    const node = parent.querySelector(selector);
    const value = node?.textContent?.trim();
    if (value) return value;
  }
  return "";
}

function absoluteUrl(value: string, base: string) {
  try {
    const parsed = new URL(value, base);
    return parsed.protocol === "https:" ? parsed.href : "";
  } catch {
    return "";
  }
}

function parseFeedXml(feed: PublicFeed, text: string): PublicItem[] {
  const document = new DOMParser().parseFromString(text, "application/xml");
  if (document.querySelector("parsererror")) throw new Error("تعذّر قراءة صيغة المصدر.");
  const entries = Array.from(document.querySelectorAll("item, entry"));
  return entries.map((entry, index) => {
    const title = htmlText(readNodeText(entry, ["title"]));
    const link = entry.querySelector("link");
    const rawUrl = link?.getAttribute("href") || link?.textContent?.trim() || readNodeText(entry, ["guid", "id"]);
    const url = absoluteUrl(rawUrl, feed.siteUrl);
    const excerpt = htmlText(readNodeText(entry, ["description", "summary", "content\\:encoded", "content"]));
    const date = readNodeText(entry, ["published", "updated", "pubDate", "dc\\:date"]);
    const parsedDate = date ? new Date(date) : null;
    if (!title || !url) return null;
    return {
      id: `${feed.id}:${url || index}`,
      feedId: feed.id,
      country: feed.country,
      countryCode: feed.countryCode,
      organization: feed.organization,
      language: feed.language,
      title,
      excerpt: excerpt.slice(0, 680),
      url,
      publishedAt: parsedDate && !Number.isNaN(parsedDate.getTime()) ? parsedDate.toISOString() : null,
    } satisfies PublicItem;
  }).filter((item): item is PublicItem => item !== null).slice(0, 18);
}

const ARABIC_MONTHS: Record<string, number> = {
  "يناير": 0, "فبراير": 1, "مارس": 2, "أبريل": 3, "ابريل": 3, "ماي": 4,
  "يونيو": 5, "يوليوز": 6, "يوليو": 6, "غشت": 7, "أغسطس": 7,
  "شتنبر": 8, "سبتمبر": 8, "أكتوبر": 9, "نونبر": 10, "نوفمبر": 10,
  "دجنبر": 11, "ديسمبر": 11,
};

function parseMoroccanDate(value: string): string | null {
  const match = value.match(/(\d{1,2})\s+([\p{Script=Arabic}]+)\s+(\d{4})/u);
  if (!match) return null;
  const month = ARABIC_MONTHS[match[2]];
  if (month === undefined) return null;
  const date = new Date(Number(match[3]), month, Number(match[1]), 12);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function parseMoroccoHtml(feed: PublicFeed, text: string): PublicItem[] {
  const document = new DOMParser().parseFromString(text, "text/html");
  const anchors = Array.from(document.querySelectorAll("a[href]")).filter((anchor) => {
    const raw = anchor.getAttribute("href") || "";
    let decoded = raw;
    try { decoded = decodeURIComponent(raw); } catch { /* keep the original URL */ }
    return /\/(?:الأخبار|news)\//i.test(decoded);
  });
  const seen = new Set<string>();
  const results: PublicItem[] = [];

  for (const anchor of anchors) {
    const url = absoluteUrl(anchor.getAttribute("href") || "", feed.siteUrl);
    if (!url || seen.has(url)) continue;
    const clone = anchor.cloneNode(true) as HTMLAnchorElement;
    clone.querySelectorAll("img, svg, picture, script, style").forEach((node) => node.remove());
    const titleNode = clone.querySelector("h1, h2, h3, h4, strong, [class*=title]");
    const cardText = cleanText(clone.textContent || "");
    const title = cleanText(titleNode?.textContent || cardText.split(/\s{2,}|\n/)[0] || "");
    if (title.length < 12 || title.length > 260 || /^(المزيد|الأخبار|اقرأ المزيد)/.test(title)) continue;
    seen.add(url);
    const dateText = cardText.match(/\d{1,2}\s+[\p{Script=Arabic}]+\s+\d{4}/u)?.[0] || "";
    const excerpt = cardText.replace(title, "").replace(dateText, "").trim();
    results.push({
      id: `${feed.id}:${url}`,
      feedId: feed.id,
      country: feed.country,
      countryCode: feed.countryCode,
      organization: feed.organization,
      language: feed.language,
      title,
      excerpt: excerpt.slice(0, 680),
      url,
      publishedAt: parseMoroccanDate(dateText),
    });
    if (results.length >= 18) break;
  }
  return results;
}

async function requestText(url: string) {
  if (Capacitor.isNativePlatform()) {
    const response = await CapacitorHttp.get({
      url,
      headers: { Accept: "application/atom+xml, application/rss+xml, application/xml, text/html;q=0.9, */*;q=0.8" },
      connectTimeout: 12_000,
      readTimeout: 18_000,
      responseType: "text",
    });
    if (response.status < 200 || response.status >= 300) throw new Error(`HTTP ${response.status}`);
    return typeof response.data === "string" ? response.data : String(response.data ?? "");
  }
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 18_000);
  try {
    const response = await fetch(url, { cache: "no-store", signal: controller.signal, headers: { Accept: "application/atom+xml, application/rss+xml, application/xml, text/html;q=0.9, */*;q=0.8" } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.text();
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function loadPublicFeed(feed: PublicFeed): Promise<FeedResult> {
  try {
    const text = await requestText(feed.feedUrl);
    const items = feed.format === "html" ? parseMoroccoHtml(feed, text) : parseFeedXml(feed, text);
    if (items.length === 0) throw new Error("لم يعثر القارئ على مواد في المصدر.");
    return { feed, items };
  } catch (error) {
    return { feed, items: [], error: error instanceof Error ? error.message : "تعذّر الاتصال بالمصدر." };
  }
}
