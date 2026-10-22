"use client";

import { useEffect, useMemo, useState } from "react";
import { auditTexte, auditerDescriptifs, type Audit, type LigneDescriptif } from "@/lib/audit";
import { rechercher, versBibtex, versCsv, type Travail } from "@/lib/search";

// ─────────────────────────── données annexes ───────────────────────────
interface Outil {
  repo: string;
  categorie: string;
  note: string;
  etoiles: number | null;
  licence: string | null;
  dernier_push: string | null;
  archive: boolean;
  archive_localement: boolean;
  url: string;
}

const CATEGORIES: Record<string, string> = {
  decouverte: "Découverte & métadonnées",
  fulltext: "Texte intégral",
  parsing: "Extraction & structuration",
  synthese: "Synthèse & RAG",
  revue_systematique: "Revue systématique",
  audit: "Audit & intégrité",
  mcp: "MCP & agents",
  donnees: "Données & dépôts",
  metascience: "Corpus & méta-science",
};

const EXEMPLE_ARTICLE = `Le groupe programme différait du groupe contrôle, t(28) = 1.85, p = .042.
Une analyse secondaire montrait un effet sur la fluence, t(38) = 2.15, p = .034.
L'interaction était significative, F(2, 45) = 3.21, p = .049.
La relation entre motivation et score valait r(28) = .41, p = .021.
Le modèle nul était significatif, F(1, 20) = 9.5, p = .000.`;

type Onglet = "recherche" | "audit" | "tableau" | "catalogue";

export default function Console() {
  const [onglet, setOnglet] = useState<Onglet>("recherche");
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-8 sm:px-6 lg:py-12">
      <EnTete />
      <nav className="flex flex-wrap gap-2">
        {([
          ["recherche", "Recherche"],
          ["audit", "Audit d'article"],
          ["tableau", "GRIM / tableau"],
          ["catalogue", "Catalogue · 142 outils"],
        ] as [Onglet, string][]).map(([cle, libelle]) => (
          <button
            key={cle}
            onClick={() => setOnglet(cle)}
            className={`rounded-full px-4 py-2 text-sm font-medium transition ${
              onglet === cle
                ? "bg-teal-400 text-slate-950 shadow-lg shadow-teal-500/20"
                : "border border-white/10 bg-white/5 text-slate-300 hover:bg-white/10"
            }`}
          >
            {libelle}
          </button>
        ))}
      </nav>

      {onglet === "recherche" && <PanneauRecherche />}
      {onglet === "audit" && <PanneauAudit />}
      {onglet === "tableau" && <PanneauTableau />}
      {onglet === "catalogue" && <PanneauCatalogue />}

      <footer className="mt-auto border-t border-white/10 pt-6 text-xs leading-relaxed text-slate-400">
        Recherche fédérée exécutée depuis votre navigateur (OpenAlex, Crossref, Europe PMC).
        L&apos;audit statistique reproduit le moteur Python <code className="rounded bg-white/10 px-1">scitk.audit</code> :
        recalcul des p-values APA avec tolérance d&apos;arrondi, GRIM, bornes exactes de l&apos;écart-type (SPRITE).
        Aucun texte n&apos;est envoyé à un serveur.
      </footer>
    </main>
  );
}

function EnTete() {
  return (
    <header className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <svg viewBox="0 0 32 32" className="h-9 w-9 text-teal-400" fill="none" stroke="currentColor" strokeWidth="1.6">
          <path d="M16 2.5 28 9v14L16 29.5 4 23V9z" />
          <path d="M16 10v8M16 21.5v.5" strokeLinecap="round" />
          <circle cx="16" cy="16" r="2.2" className="text-teal-300" />
        </svg>
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-white sm:text-2xl">
            Console de recherche &amp; d&apos;audit scientifiques
          </h1>
          <p className="text-sm text-slate-400">
            142 outils GitHub vérifiés · 74 archivés localement · audit statistique déterministe
          </p>
        </div>
      </div>
    </header>
  );
}

// ─────────────────────────── recherche ───────────────────────────
function PanneauRecherche() {
  const [requete, setRequete] = useState("reading remediation randomized controlled trial");
  const [sources, setSources] = useState<string[]>(["openalex", "crossref", "europepmc"]);
  const [limite, setLimite] = useState(15);
  const [anneeMin, setAnneeMin] = useState<string>("");
  const [charge, setCharge] = useState(false);
  const [travaux, setTravaux] = useState<Travail[]>([]);
  const [meta, setMeta] = useState<{ brut: number; doublons: number; parSource: Record<string, number>; erreurs: Record<string, string> } | null>(null);
  const [erreur, setErreur] = useState<string | null>(null);
  const [deja, setDeja] = useState(false);

  async function lancer() {
    if (!requete.trim() || sources.length === 0) return;
    setCharge(true);
    setErreur(null);
    try {
      const r = await rechercher({
        requete,
        sources: sources as ("openalex" | "crossref" | "europepmc")[],
        limite,
        anneeMin: anneeMin ? Number(anneeMin) : undefined,
      });
      setTravaux(r.travaux);
      setMeta({ brut: r.brut, doublons: r.doublons, parSource: r.parSource, erreurs: r.erreurs });
      setDeja(true);
    } catch (e) {
      setErreur(e instanceof Error ? e.message : String(e));
    } finally {
      setCharge(false);
    }
  }

  function telecharger(contenu: string, nom: string, type: string) {
    const blob = new Blob([contenu], { type });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = nom;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <section className="flex flex-col gap-4">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 sm:p-5">
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-3 sm:flex-row">
            <input
              value={requete}
              onChange={(e) => setRequete(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && lancer()}
              placeholder="Mots-clés, titre, question de recherche…"
              className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-teal-400/60"
            />
            <button
              onClick={lancer}
              disabled={charge}
              className="rounded-xl bg-teal-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-teal-300 disabled:opacity-50"
            >
              {charge ? "Recherche…" : "Rechercher"}
            </button>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-sm text-slate-300">
            {[
              ["openalex", "OpenAlex · 260 M"],
              ["crossref", "Crossref · 160 M DOI"],
              ["europepmc", "Europe PMC · 43 M"],
            ].map(([cle, libelle]) => (
              <label key={cle} className="flex cursor-pointer items-center gap-2">
                <input
                  type="checkbox"
                  checked={sources.includes(cle)}
                  onChange={(e) =>
                    setSources((s) => (e.target.checked ? [...s, cle] : s.filter((x) => x !== cle)))
                  }
                  className="h-4 w-4 accent-teal-400"
                />
                {libelle}
              </label>
            ))}
            <label className="flex items-center gap-2">
              Depuis
              <input
                value={anneeMin}
                onChange={(e) => setAnneeMin(e.target.value.replace(/\D/g, "").slice(0, 4))}
                placeholder="1990"
                className="w-20 rounded-lg border border-white/10 bg-slate-950/60 px-2 py-1 text-center text-white outline-none focus:border-teal-400/60"
              />
            </label>
            <label className="flex items-center gap-2">
              Limite
              <select
                value={limite}
                onChange={(e) => setLimite(Number(e.target.value))}
                className="rounded-lg border border-white/10 bg-slate-950/60 px-2 py-1 text-white outline-none"
              >
                {[10, 15, 25, 50].map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </label>
          </div>
        </div>
      </div>

      {erreur && <p className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-sm text-rose-200">{erreur}</p>}

      {meta && (
        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
          <span>{meta.brut} résultats bruts</span>
          <span>·</span>
          <span>{meta.doublons} doublons fusionnés</span>
          {Object.entries(meta.parSource).map(([s, n]) => (
            <span key={s} className="rounded-full border border-white/10 bg-white/5 px-2 py-1">
              {s} : {n}
            </span>
          ))}
          {Object.entries(meta.erreurs).map(([s, m]) => (
            <span key={s} className="rounded-full border border-amber-400/30 bg-amber-400/10 px-2 py-1 text-amber-200">
              {s} : {m}
            </span>
          ))}
          {travaux.length > 0 && (
            <span className="ml-auto flex gap-2">
              <button
                onClick={() => telecharger(versBibtex(travaux), "resultats.bib", "text/plain")}
                className="rounded-lg border border-white/10 px-2 py-1 hover:bg-white/10"
              >
                Export BibTeX
              </button>
              <button
                onClick={() => telecharger(versCsv(travaux), "resultats.csv", "text/csv")}
                className="rounded-lg border border-white/10 px-2 py-1 hover:bg-white/10"
              >
                Export CSV
              </button>
            </span>
          )}
        </div>
      )}

      {!deja && !charge && (
        <p className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
          Choisissez au moins une source puis lancez la recherche. Les requêtes partent directement
          de votre navigateur : aucune donnée ne transite par cette application.
        </p>
      )}

      <div className="flex flex-col gap-3">
        {travaux.map((t, i) => (
          <article key={`${t.doi}-${i}`} className="rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-teal-400/30">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <h2 className="max-w-3xl text-sm font-semibold leading-snug text-white sm:text-base">
                {t.titre || "(sans titre)"}
              </h2>
              {t.oaUrl && (
                <a href={t.oaUrl} target="_blank" rel="noreferrer"
                   className="rounded-full bg-emerald-400/15 px-2 py-1 text-[11px] font-medium text-emerald-300">
                  accès ouvert ↗
                </a>
              )}
            </div>
            <p className="mt-1 text-xs text-slate-400">
              {t.auteurs.slice(0, 4).join(", ")}
              {t.auteurs.length > 4 ? " et al." : ""} · {t.revue || "revue non précisée"} · {t.annee ?? "s.d."}
            </p>
            {t.resume && <p className="mt-2 line-clamp-3 text-xs leading-relaxed text-slate-400">{t.resume}</p>}
            <div className="mt-3 flex flex-wrap items-center gap-2 text-[11px] text-slate-400">
              {t.doi && (
                <a href={`https://doi.org/${t.doi}`} target="_blank" rel="noreferrer" className="rounded bg-white/5 px-2 py-1 font-mono hover:text-teal-300">
                  {t.doi}
                </a>
              )}
              {typeof t.citations === "number" && <span className="rounded bg-white/5 px-2 py-1">{t.citations} citations</span>}
              {t.sources.map((s) => (
                <span key={s} className="rounded bg-teal-400/10 px-2 py-1 text-teal-200">{s}</span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

// ─────────────────────────── audit ───────────────────────────
function PanneauAudit() {
  const [texte, setTexte] = useState(EXEMPLE_ARTICLE);
  const [audit, setAudit] = useState<Audit | null>(null);

  const lancer = () => setAudit(auditTexte(texte));

  function telecharger() {
    if (!audit) return;
    const blob = new Blob([JSON.stringify(audit, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "audit.json";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  const gravite = audit
    ? audit.resultats.some((r) => r.constats.some((c) => c.severite === "critique")) || audit.constats.some((c) => c.severite === "critique")
      ? "critique"
      : audit.resultats.some((r) => r.constats.some((c) => c.severite === "majeur"))
        ? "majeur"
        : audit.resultats.some((r) => r.constats.some((c) => c.severite === "mineur")) ? "mineur" : "aucune"
    : null;

  return (
    <section className="flex flex-col gap-4">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 sm:p-5">
        <label className="mb-2 block text-sm font-medium text-slate-300">
          Texte de l&apos;article (résultats au format APA)
        </label>
        <textarea
          value={texte}
          onChange={(e) => setTexte(e.target.value)}
          rows={9}
          className="w-full resize-y rounded-xl border border-white/10 bg-slate-950/60 p-4 font-mono text-xs leading-relaxed text-slate-200 outline-none focus:border-teal-400/60"
        />
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <button onClick={lancer} className="rounded-xl bg-teal-400 px-5 py-2.5 text-sm font-semibold text-slate-950 hover:bg-teal-300">
            Analyser
          </button>
          {audit && (
            <button onClick={telecharger} className="rounded-xl border border-white/10 px-4 py-2.5 text-sm text-slate-200 hover:bg-white/10">
              Télécharger le JSON
            </button>
          )}
          <span className="text-xs text-slate-500">
            Extrait t, F, χ², r, z ; recalcule p ; compare à l&apos;intervalle d&apos;arrondi.
          </span>
        </div>
      </div>

      {audit && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
            <Carte libelle="Résultats" valeur={audit.nbResultats} />
            <Carte libelle="Significatifs" valeur={audit.nbSignificatifs} />
            <Carte libelle="Incohérences" valeur={audit.nbIncoherents} accent={audit.nbIncoherents > 0} />
            <Carte libelle="Erreurs de décision" valeur={audit.nbErreursDecision} accent={audit.nbErreursDecision > 0} />
            <Carte libelle="Score" valeur={`${audit.score}/100`} accent={audit.score < 60} />
          </div>

          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-400">Gravité</span>
            <Badge severite={gravite ?? "aucune"} />
          </div>

          <div className="overflow-hidden rounded-2xl border border-white/10">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-white/5 text-slate-400">
                <tr>
                  {["Test", "p rapportée", "p recalculée", "Intervalle", "Constats"].map((h) => (
                    <th key={h} className="px-3 py-2 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {audit.resultats.map((r, i) => (
                  <tr key={i} className="text-slate-300">
                    <td className="px-3 py-2 font-mono">{r.dfTexte} = {r.statistique}</td>
                    <td className="px-3 py-2">{r.pRapportee !== undefined ? `${r.operateur} ${r.pRapportee}` : "—"}</td>
                    <td className="px-3 py-2">{r.pCalculee !== undefined ? r.pCalculee.toFixed(4) : "—"}</td>
                    <td className="px-3 py-2 text-slate-500">
                      {r.intervalle ? `${r.intervalle[0].toFixed(4)} – ${r.intervalle[1].toFixed(4)}` : "—"}
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex flex-wrap gap-1">
                        {r.constats.length === 0 && <span className="text-emerald-400">cohérent</span>}
                        {r.constats.map((c, j) => (
                          <span key={j} className={pastille(c.severite)}>{c.code}</span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <ul className="flex flex-col gap-2">
            {audit.resultats.flatMap((r, i) =>
              r.constats.map((c, j) => (
                <li key={`${i}-${j}`} className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm">
                  <Badge severite={c.severite} /> <span className="ml-2 text-slate-300">{c.message}</span>
                </li>
              )),
            )}
            {audit.constats.map((c, i) => (
              <li key={`t-${i}`} className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm">
                <Badge severite={c.severite} /> <span className="ml-2 text-slate-300">{c.message}</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}

// ─────────────────────────── GRIM / tableau ───────────────────────────
function PanneauTableau() {
  const [lignes, setLignes] = useState<LigneDescriptif[]>([
    { label: "Groupe programme", n: 60, mean: 3.77, sd: 0.31 },
    { label: "Groupe contrôle", n: 60, mean: 3.11, sd: 0.44 },
    { label: "Sous-groupe A", n: 25, mean: 4.37, sd: 0.42 },
  ]);
  const [lo, setLo] = useState(1);
  const [hi, setHi] = useState(5);
  const verdicts = useMemo(() => auditerDescriptifs(lignes, lo, hi), [lignes, lo, hi]);
  const echecs = verdicts.filter((v) => !v.grimOk || v.spriteOk === false).length;

  const maj = (i: number, champ: keyof LigneDescriptif, valeur: string) => {
    setLignes((l) =>
      l.map((x, j) =>
        j === i
          ? { ...x, [champ]: champ === "label" ? valeur : Number(valeur.replace(",", ".")) || 0 }
          : x,
      ),
    );
  };

  return (
    <section className="flex flex-col gap-4">
      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 sm:p-5">
        <p className="text-sm text-slate-300">
          Si les données sont des entiers (Likert, score total, comptage), la moyenne et
          l&apos;écart-type ne peuvent pas prendre n&apos;importe quelle valeur.
          <span className="text-slate-500"> GRIM vérifie la somme ; SPRITE calcule les bornes exactes de l&apos;écart-type.</span>
        </p>
        <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-300">
          <label className="flex items-center gap-2">
            Minimum de l&apos;échelle
            <input type="number" value={lo} onChange={(e) => setLo(Number(e.target.value))}
              className="w-16 rounded-lg border border-white/10 bg-slate-950/60 px-2 py-1 text-center text-white" />
          </label>
          <label className="flex items-center gap-2">
            Maximum
            <input type="number" value={hi} onChange={(e) => setHi(Number(e.target.value))}
              className="w-16 rounded-lg border border-white/10 bg-slate-950/60 px-2 py-1 text-center text-white" />
          </label>
          <span className={`ml-auto rounded-full px-3 py-1 text-xs ${echecs ? "bg-rose-500/15 text-rose-300" : "bg-emerald-500/15 text-emerald-300"}`}>
            {echecs} ligne(s) impossible(s) sur {lignes.length}
          </span>
        </div>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-white/10">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-white/5 text-slate-400">
            <tr>
              {["Libellé", "n", "Moyenne", "Écart-type", "Verdict"].map((h) => (
                <th key={h} className="px-3 py-2 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {lignes.map((l, i) => (
              <tr key={i} className="text-slate-200">
                <td className="px-3 py-2">
                  <input value={l.label} onChange={(e) => maj(i, "label", e.target.value)}
                    className="w-full rounded-lg border border-transparent bg-transparent px-2 py-1 hover:border-white/10 focus:border-teal-400/60 focus:outline-none" />
                </td>
                <td className="px-3 py-2">
                  <input type="number" value={l.n} onChange={(e) => maj(i, "n", e.target.value)}
                    className="w-20 rounded-lg border border-transparent bg-transparent px-2 py-1 hover:border-white/10 focus:border-teal-400/60 focus:outline-none" />
                </td>
                <td className="px-3 py-2">
                  <input type="number" step="0.01" value={l.mean} onChange={(e) => maj(i, "mean", e.target.value)}
                    className="w-24 rounded-lg border border-transparent bg-transparent px-2 py-1 hover:border-white/10 focus:border-teal-400/60 focus:outline-none" />
                </td>
                <td className="px-3 py-2">
                  <input type="number" step="0.01" value={l.sd ?? 0} onChange={(e) => maj(i, "sd", e.target.value)}
                    className="w-24 rounded-lg border border-transparent bg-transparent px-2 py-1 hover:border-white/10 focus:border-teal-400/60 focus:outline-none" />
                </td>
                <td className={`px-3 py-2 text-xs ${verdicts[i].grimOk && verdicts[i].spriteOk !== false ? "text-emerald-300" : "text-rose-300"}`}>
                  {verdicts[i].message}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setLignes((l) => [...l, { label: `Ligne ${l.length + 1}`, n: 30, mean: 3.5, sd: 1 }])}
          className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 hover:bg-white/10"
        >
          Ajouter une ligne
        </button>
        {lignes.length > 1 && (
          <button
            onClick={() => setLignes((l) => l.slice(0, -1))}
            className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-400 hover:bg-white/10"
          >
            Retirer la dernière
          </button>
        )}
      </div>
    </section>
  );
}

// ─────────────────────────── catalogue ───────────────────────────
function PanneauCatalogue() {
  const [outils, setOutils] = useState<Outil[]>([]);
  const [filtre, setFiltre] = useState("");
  const [categorie, setCategorie] = useState("tous");

  useEffect(() => {
    fetch("/catalogue.json")
      .then((r) => r.json())
      .then((d: Outil[]) => setOutils(d))
      .catch(() => setOutils([]));
  }, []);

  const liste = useMemo(() => {
    const f = filtre.toLowerCase();
    return outils
      .filter((o) => categorie === "tous" || o.categorie === categorie)
      .filter((o) =>
        !f ||
        o.repo.toLowerCase().includes(f) ||
        o.note.toLowerCase().includes(f) ||
        (o.licence ?? "").toLowerCase().includes(f),
      )
      .sort((a, b) => (b.etoiles ?? 0) - (a.etoiles ?? 0));
  }, [outils, filtre, categorie]);

  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <input
          value={filtre}
          onChange={(e) => setFiltre(e.target.value)}
          placeholder="Filtrer par nom, rôle, licence…"
          className="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white outline-none placeholder:text-slate-500 focus:border-teal-400/60"
        />
        <select
          value={categorie}
          onChange={(e) => setCategorie(e.target.value)}
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white outline-none"
        >
          <option value="tous">Toutes les catégories</option>
          {Object.entries(CATEGORIES).map(([cle, nom]) => (
            <option key={cle} value={cle}>{nom}</option>
          ))}
        </select>
        <span className="text-xs text-slate-400">{liste.length} outils</span>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {liste.map((o) => (
          <article key={o.repo} className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="flex items-start justify-between gap-3">
              <a href={o.url} target="_blank" rel="noreferrer" className="font-mono text-sm font-semibold text-teal-300 hover:underline">
                {o.repo}
              </a>
              <span className="shrink-0 text-xs text-slate-400">
                {o.etoiles !== null ? `${o.etoiles.toLocaleString("fr-FR")} ★` : "—"}
              </span>
            </div>
            <p className="mt-1.5 text-xs leading-relaxed text-slate-300">{o.note}</p>
            <div className="mt-2 flex flex-wrap gap-1.5 text-[11px]">
              <span className="rounded bg-white/5 px-2 py-0.5 text-slate-400">
                {CATEGORIES[o.categorie] ?? o.categorie}
              </span>
              {o.licence && <span className="rounded bg-white/5 px-2 py-0.5 text-slate-400">{o.licence}</span>}
              {o.archive_localement && (
                <span className="rounded bg-teal-400/15 px-2 py-0.5 text-teal-200">archivé ici</span>
              )}
              {o.archive && <span className="rounded bg-amber-400/15 px-2 py-0.5 text-amber-200">dépôt archivé</span>}
            </div>
          </article>
        ))}
      </div>
      {liste.length === 0 && (
        <p className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
          Aucun outil ne correspond. Le catalogue complet est dans <code>scientific-toolkit/CATALOGUE.md</code>.
        </p>
      )}
    </section>
  );
}

// ─────────────────────────── éléments d'interface ───────────────────────────
function Carte({ libelle, valeur, accent }: { libelle: string; valeur: string | number; accent?: boolean }) {
  return (
    <div className={`rounded-2xl border p-3 ${accent ? "border-rose-400/30 bg-rose-500/10" : "border-white/10 bg-white/5"}`}>
      <div className={`text-lg font-semibold ${accent ? "text-rose-300" : "text-white"}`}>{valeur}</div>
      <div className="text-[11px] uppercase tracking-wide text-slate-400">{libelle}</div>
    </div>
  );
}

function Badge({ severite }: { severite: string }) {
  const styles: Record<string, string> = {
    critique: "bg-rose-500/20 text-rose-300",
    majeur: "bg-amber-500/20 text-amber-300",
    mineur: "bg-yellow-500/15 text-yellow-200",
    info: "bg-sky-500/15 text-sky-300",
    aucune: "bg-emerald-500/15 text-emerald-300",
  };
  return (
    <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${styles[severite] ?? styles.info}`}>
      {severite}
    </span>
  );
}

function pastille(severite: string) {
  const base = "rounded px-1.5 py-0.5 font-mono text-[10px]";
  switch (severite) {
    case "critique": return `${base} bg-rose-500/20 text-rose-300`;
    case "majeur": return `${base} bg-amber-500/20 text-amber-300`;
    case "mineur": return `${base} bg-yellow-500/15 text-yellow-200`;
    default: return `${base} bg-sky-500/15 text-sky-300`;
  }
}
