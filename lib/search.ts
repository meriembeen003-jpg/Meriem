// Recherche fédérée côté navigateur : OpenAlex, Crossref, Europe PMC.
// Les appels partent du navigateur de l'utilisateur (CORS ouvert sur ces trois API).

export interface Travail {
  titre: string;
  doi: string;
  annee?: number;
  auteurs: string[];
  revue: string;
  resume: string;
  citations?: number;
  oaUrl: string;
  source: string;
  sources: string[];
  url: string;
  type: string;
}

const nettoie = (s: string) => (s ?? "").replace(/\s+/g, " ").trim();
const sansBalises = (s: string) => nettoie((s ?? "").replace(/<[^>]+>/g, " "));

function reconstruire(inv: Record<string, number[]> | null | undefined): string {
  if (!inv) return "";
  const pos: [number, string][] = [];
  for (const [mot, idx] of Object.entries(inv)) for (const i of idx) pos.push([i, mot]);
  return pos.sort((a, b) => a[0] - b[0]).map((p) => p[1]).join(" ");
}

export async function chercherOpenAlex(q: string, limite: number, anneeMin?: number): Promise<Travail[]> {
  const p = new URLSearchParams({ search: q, "per-page": String(Math.min(limite, 50)) });
  const filtres: string[] = [];
  if (anneeMin) filtres.push(`from_publication_date:${anneeMin}-01-01`);
  if (filtres.length) p.set("filter", filtres.join(","));
  const r = await fetch(`https://api.openalex.org/works?${p}`);
  if (!r.ok) throw new Error(`OpenAlex HTTP ${r.status}`);
  const d = await r.json();
  return (d.results ?? []).map((w: any): Travail => ({
    titre: nettoie(w.title ?? w.display_name ?? ""),
    doi: (w.doi ?? "").replace("https://doi.org/", ""),
    annee: w.publication_year,
    auteurs: (w.authorships ?? []).map((a: any) => a.author?.display_name).filter(Boolean),
    revue: w.primary_location?.source?.display_name ?? "",
    resume: reconstruire(w.abstract_inverted_index),
    citations: w.cited_by_count,
    oaUrl: w.open_access?.oa_url ?? "",
    source: "OpenAlex",
    sources: ["OpenAlex"],
    url: w.id ?? "",
    type: w.type ?? "",
  }));
}

export async function chercherCrossref(q: string, limite: number, anneeMin?: number): Promise<Travail[]> {
  const p = new URLSearchParams({ "query.bibliographic": q, rows: String(Math.min(limite, 50)) });
  if (anneeMin) p.set("filter", `from-pub-date:${anneeMin}-01-01`);
  const r = await fetch(`https://api.crossref.org/works?${p}`, {
    headers: { Accept: "application/json" },
  });
  if (!r.ok) throw new Error(`Crossref HTTP ${r.status}`);
  const d = await r.json();
  return (d.message?.items ?? []).map((it: any): Travail => {
    const parties = it.issued?.["date-parts"]?.[0]?.[0];
    return {
      titre: nettoie((it.title ?? [""])[0] ?? ""),
      doi: (it.DOI ?? "").toLowerCase(),
      annee: parties,
      auteurs: (it.author ?? []).map((a: any) => [a.given, a.family].filter(Boolean).join(" ") || a.name || ""),
      revue: nettoie((it["container-title"] ?? [""])[0] ?? ""),
      resume: sansBalises(it.abstract ?? ""),
      citations: it["is-referenced-by-count"],
      oaUrl: "",
      source: "Crossref",
      sources: ["Crossref"],
      url: it.URL ?? (it.DOI ? `https://doi.org/${it.DOI}` : ""),
      type: it.type ?? "",
    };
  });
}

export async function chercherEuropePmc(q: string, limite: number, anneeMin?: number): Promise<Travail[]> {
  let requete = q;
  if (anneeMin) requete += ` AND (PUB_YEAR:[${anneeMin} TO 2030])`;
  const p = new URLSearchParams({
    query: requete, format: "json", resultType: "core",
    pageSize: String(Math.min(limite, 50)), sort: "CITED desc",
  });
  const r = await fetch(`https://www.ebi.ac.uk/europepmc/webservices/rest/search?${p}`);
  if (!r.ok) throw new Error(`Europe PMC HTTP ${r.status}`);
  const d = await r.json();
  return (d.resultList?.result ?? []).map((x: any): Travail => ({
    titre: nettoie(x.title ?? ""),
    doi: (x.doi ?? "").toLowerCase(),
    annee: Number(x.pubYear) || undefined,
    auteurs: (x.authorString ?? "").replace(/\.$/, "").split(",").map((s: string) => s.trim()).filter(Boolean),
    revue: x.journalTitle ?? "",
    resume: nettoie(x.abstractText ?? ""),
    citations: typeof x.citedByCount === "number" ? x.citedByCount : undefined,
    oaUrl: x.isOpenAccess === "Y" ? `https://europepmc.org/article/${x.source}/${x.id}` : "",
    source: "Europe PMC",
    sources: ["Europe PMC"],
    url: `https://europepmc.org/article/${x.source}/${x.id}`,
    type: x.pubType ?? "",
  }));
}

const cleTitre = (t: string) => t.toLowerCase().replace(/[^a-z0-9 ]/g, "").split(/\s+/).slice(0, 12).join(" ");

export function dedupliquer(travaux: Travail[]): { uniques: Travail[]; doublons: number } {
  const map = new Map<string, Travail>();
  for (const t of travaux) {
    const cle = t.doi ? `doi:${t.doi}` : `titre:${cleTitre(t.titre)}|${t.annee ?? ""}`;
    const existant = map.get(cle);
    if (existant) {
      existant.sources = Array.from(new Set([...existant.sources, t.source]));
      existant.resume = existant.resume || t.resume;
      existant.oaUrl = existant.oaUrl || t.oaUrl;
      existant.revue = existant.revue || t.revue;
      existant.citations = Math.max(existant.citations ?? 0, t.citations ?? 0);
      existant.auteurs = existant.auteurs.length ? existant.auteurs : t.auteurs;
    } else {
      map.set(cle, { ...t, sources: [t.source] });
    }
  }
  return { uniques: Array.from(map.values()), doublons: travaux.length - map.size };
}

export interface OptionsRecherche {
  requete: string;
  sources: ("openalex" | "crossref" | "europepmc")[];
  limite: number;
  anneeMin?: number;
}

export async function rechercher(o: OptionsRecherche) {
  const taches: Promise<Travail[]>[] = [];
  const noms: string[] = [];
  if (o.sources.includes("openalex")) { taches.push(chercherOpenAlex(o.requete, o.limite, o.anneeMin)); noms.push("OpenAlex"); }
  if (o.sources.includes("crossref")) { taches.push(chercherCrossref(o.requete, o.limite, o.anneeMin)); noms.push("Crossref"); }
  if (o.sources.includes("europepmc")) { taches.push(chercherEuropePmc(o.requete, o.limite, o.anneeMin)); noms.push("Europe PMC"); }
  const resultats = await Promise.allSettled(taches);
  const travaux: Travail[] = [];
  const erreurs: Record<string, string> = {};
  const parSource: Record<string, number> = {};
  resultats.forEach((r, i) => {
    if (r.status === "fulfilled") {
      travaux.push(...r.value);
      parSource[noms[i]] = r.value.length;
    } else {
      erreurs[noms[i]] = String(r.reason?.message ?? r.reason);
      parSource[noms[i]] = 0;
    }
  });
  const { uniques, doublons } = dedupliquer(travaux);
  uniques.sort((a, b) => (b.sources.length - a.sources.length) || ((b.citations ?? 0) - (a.citations ?? 0)));
  return { travaux: uniques, doublons, brut: travaux.length, erreurs, parSource };
}

export function versBibtex(travaux: Travail[]): string {
  const slug = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "").slice(0, 30);
  return travaux.map((t, i) => {
    const auteur = t.auteurs[0]?.split(" ").pop() ?? "anonyme";
    const mot = slug(t.titre.split(" ")[0] ?? "ref");
    const champs = [
      ["title", t.titre], ["author", t.auteurs.join(" and ")], ["journal", t.revue],
      ["year", t.annee ? String(t.annee) : ""], ["doi", t.doi],
      ["url", t.oaUrl || t.url], ["abstract", t.resume.slice(0, 900)],
    ].filter(([, v]) => v);
    return `@article{${slug(auteur)}${t.annee ?? ""}${mot}${i || ""},\n` +
      champs.map(([k, v]) => `  ${k} = {${v}}`).join(",\n") + "\n}";
  }).join("\n\n") + "\n";
}

export function versCsv(travaux: Travail[]): string {
  const esc = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""').replace(/\s+/g, " ")}"`;
  const entete = ["titre", "doi", "annee", "auteurs", "revue", "citations", "sources", "oa_url"];
  const lignes = travaux.map((t) => [
    t.titre, t.doi, t.annee ?? "", t.auteurs.join("; "), t.revue,
    t.citations ?? "", t.sources.join("; "), t.oaUrl,
  ].map(esc).join(","));
  return [entete.join(","), ...lignes].join("\n");
}
