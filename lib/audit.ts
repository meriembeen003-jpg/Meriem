// Moteur d'audit côté navigateur — portage TypeScript de scitk/audit/apa.py.
// Recalcule les p-values APA, détecte les incohérences et produit un rapport.

import { tTwoSidedP, fSf, chi2Sf, zTwoSidedP, grim, sdBounds, sprite } from "./stats";

export type Severite = "critique" | "majeur" | "mineur" | "info";

export interface Constat {
  code: string;
  severite: Severite;
  message: string;
}

export interface Resultat {
  type: "t" | "F" | "chi2" | "r" | "z";
  statistique: number;
  df1?: number;
  df2?: number;
  dfTexte: string;
  pRapportee?: number;
  operateur: "=" | "<" | ">";
  pCalculee?: number;
  intervalle?: [number, number];
  extrait: string;
  constats: Constat[];
}

export interface Audit {
  resultats: Resultat[];
  constats: Constat[];
  nbResultats: number;
  nbSignificatifs: number;
  nbIncoherents: number;
  nbErreursDecision: number;
  score: number;
  pValues: number[];
}

const TRAD: [string, string][] = [
  ["χ²", "chi2"], ["χ2", "chi2"], ["x²", "chi2"], ["X²", "chi2"], ["X2", "chi2"],
  ["−", "-"], ["–", "-"], ["—", "-"], ["\u00a0", " "], ["≤", "<"], ["≥", ">"], ["＝", "="],
];

export function normaliser(t: string): string {
  let s = t.normalize("NFKC");
  for (const [a, b] of TRAD) s = s.split(a).join(b);
  return s.replace(/[ \t]+/g, " ");
}

const NUM = String.raw`[-+]?(?:\d+\.?\d*|\.\d+)`;
const P = String.raw`p\s*(?<op>[=<>])\s*(?<p>${NUM})`;
const D = String.raw`[-+]?\d+(?:\.\d+)?`;

const RE_F = new RegExp(String.raw`\bF\s*\(\s*(?<df1>${D})\s*,\s*(?<df2>${D})\s*\)\s*=\s*(?<stat>${NUM})\s*[,;]?\s*${P}`, "gi");
const RE_CHI = new RegExp(String.raw`\bchi2\s*\(\s*(?<df>${D})(?:\s*,\s*N\s*=\s*(?<n>\d+))?\s*\)\s*=\s*(?<stat>${NUM})\s*[,;]?\s*${P}`, "gi");
const RE_T = new RegExp(String.raw`\bt\s*\(\s*(?<df>${D})\s*\)\s*=\s*(?<stat>${NUM})\s*[,;]?\s*${P}`, "gi");
const RE_R = new RegExp(String.raw`\br\s*\(\s*(?<df>${D})\s*\)\s*=\s*(?<stat>${NUM})\s*[,;]?\s*${P}`, "gi");
const RE_Z = new RegExp(String.raw`\bz\s*=\s*(?<stat>${NUM})\s*[,;]?\s*${P}`, "gi");
const RE_P_SEUL = new RegExp(String.raw`\bp\s*(?<op>[=<>])\s*(?<p>${NUM})`, "gi");
const RE_NEG = /(?:non[- ]?significatif|non[- ]?significant|not\s+significant|no\s+significant|(?:n['’]?)?(?:est|était|etaient|étaient)?\s*pas\s+significatif|absence\s+de\s+significativit|insignifiant)/i;
const RE_SIG = /\b(?:significatif|significative|significant|significance|marginal|marginalement)\b/i;
const RE_CONCESSIF = /\b(?:bien\s+que|quoique|although|though|even\s+though|malgr[ée]|despite|however|toutefois|n[ée]anmoins)\b/i;

interface Groupe { [k: string]: string }

function matchGroups(m: RegExpExecArray): Groupe {
  const g = (m.groups ?? {}) as Groupe;
  return g;
}

function contexte(t: string, a: number, b: number, marge = 160): string {
  return t.slice(Math.max(0, a - marge), Math.min(t.length, b + marge)).trim();
}

function claim(ctx: string): "significatif" | "non-significatif" | null {
  if (RE_CONCESSIF.test(ctx)) return null;
  if (RE_NEG.test(ctx)) return "non-significatif";
  if (RE_SIG.test(ctx)) return "significatif";
  return null;
}

function pDe(r: Resultat): number {
  switch (r.type) {
    case "t": return tTwoSidedP(r.statistique, r.df1 ?? 0);
    case "F": return fSf(r.statistique, r.df1 ?? 0, r.df2 ?? 0);
    case "chi2": return chi2Sf(r.statistique, r.df1 ?? 0);
    case "r": {
      const df = r.df1 ?? 0;
      if (df <= 0) return NaN;
      const t = Math.abs(r.statistique) * Math.sqrt(df / Math.max(1e-12, 1 - r.statistique ** 2));
      return tTwoSidedP(t, df);
    }
    case "z": return zTwoSidedP(r.statistique);
  }
}

function decimales(brut: string): number {
  const p = brut.replace(/^[+-]/, "").split(".");
  return p.length > 1 ? p[1].length : 0;
}

function evaluer(r: Resultat, statBrut: string, alpha = 0.05): void {
  const p = pDe(r);
  if (!Number.isFinite(p)) {
    r.constats.push({ code: "calcul_impossible", severite: "info", message: "Résultat non recalculable (dl invalides)." });
    return;
  }
  r.pCalculee = p;
  // intervalle compatible avec l'arrondi de la statistique
  const demi = 0.5 * 10 ** -decimales(statBrut);
  const bas = { ...r, statistique: r.statistique - demi };
  const haut = { ...r, statistique: r.statistique + demi };
  const p1 = pDe(bas), p2 = pDe(haut);
  if (Number.isFinite(p1) && Number.isFinite(p2)) r.intervalle = [Math.min(p1, p2), Math.max(p1, p2)];

  if (r.pRapportee === undefined) return;
  const pr = r.pRapportee;
  if (pr > 1 || pr < 0) {
    r.constats.push({ code: "p_impossible", severite: "critique", message: `p hors de [0,1] : ${pr}.` });
    return;
  }
  if (pr === 0) {
    r.constats.push({ code: "p_zero", severite: "mineur", message: "p = .000 est impossible : rapporter p < .001." });
    return;
  }
  const [lo, hi] = r.intervalle ?? [p, p];

  if (r.operateur === "=" && (pr < alpha) !== (p < alpha)) {
    r.constats.push({
      code: "erreur_decision", severite: "critique",
      message: `La décision change : p rapportée = ${pr.toFixed(4)}, p recalculée = ${p.toFixed(4)} (seuil ${alpha}).`,
    });
  }
  if (r.operateur === "=") {
    const basP = pr - 0.0005, hautP = pr + 0.0005;
    if (hi < basP || lo > hautP) {
      const trou = hi < basP ? basP - hi : lo - hautP;
      r.constats.push({
        code: "incoherence", severite: trou > 0.01 ? "majeur" : "mineur",
        message: `p recalculée = ${p.toFixed(4)} (intervalle ${lo.toFixed(4)}–${hi.toFixed(4)}) vs rapportée = ${pr.toFixed(4)}.`,
      });
    }
  } else if (r.operateur === "<" && !(lo < pr)) {
    r.constats.push({ code: "incoherence_inegalite", severite: "critique", message: `p < ${pr} annoncée, p recalculée = ${p.toFixed(4)}.` });
  } else if (r.operateur === ">" && !(hi > pr)) {
    r.constats.push({ code: "incoherence_inegalite", severite: "critique", message: `p > ${pr} annoncée, p recalculée = ${p.toFixed(4)}.` });
  }
  if (Math.abs(pr - alpha) < 1e-12) {
    r.constats.push({ code: "p_charniere", severite: "info", message: "p exactement au seuil : conclusion fragile." });
  }
  if (r.type === "r" && Math.abs(r.statistique) > 1) {
    r.constats.push({ code: "r_invalide", severite: "critique", message: "|r| > 1 : corrélation impossible." });
  }
}

export function auditTexte(texte: string, alpha = 0.05): Audit {
  const t = normaliser(texte);
  const pris: [number, number][] = [];
  const libre = (a: number, b: number) => pris.every(([x, y]) => b <= x || a >= y);
  const resultats: Resultat[] = [];

  const ajouter = (type: Resultat["type"], statBrut: string, dfTexte: string,
    pRapportee: number, operateur: "=" | "<" | ">", df1?: number, df2?: number, extrait = "") => {
    const r: Resultat = {
      type, statistique: parseFloat(statBrut), df1, df2, dfTexte,
      pRapportee, operateur, extrait, constats: [],
    };
    evaluer(r, statBrut, alpha);
    const c = claim(extrait);
    if (c && r.pCalculee !== undefined) {
      const sig = r.pCalculee < alpha;
      if (c === "significatif" && !sig) {
        r.constats.push({ code: "claim_contredit", severite: "critique", message: `Le texte dit « significatif », p recalculée = ${r.pCalculee.toFixed(4)}.` });
      } else if (c === "non-significatif" && sig) {
        r.constats.push({ code: "claim_contredit", severite: "majeur", message: `Le texte évoque une absence de significativité, p recalculée = ${r.pCalculee.toFixed(4)}.` });
      }
    }
    resultats.push(r);
  };

  for (const re of [RE_F, RE_CHI, RE_T, RE_R, RE_Z]) {
    re.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = re.exec(t))) {
      if (!libre(m.index, m.index + m[0].length)) continue;
      pris.push([m.index, m.index + m[0].length]);
      const g = matchGroups(m);
      const extrait = contexte(t, m.index, m.index + m[0].length);
      const op = (g.op ?? "=") as "=" | "<" | ">";
      if (re === RE_F) ajouter("F", g.stat, `F(${g.df1}, ${g.df2})`, parseFloat(g.p), op, parseFloat(g.df1), parseFloat(g.df2), extrait);
      else if (re === RE_CHI) ajouter("chi2", g.stat, `χ²(${g.df})`, parseFloat(g.p), op, parseFloat(g.df), undefined, extrait);
      else if (re === RE_T) ajouter("t", g.stat, `t(${g.df})`, parseFloat(g.p), op, parseFloat(g.df), undefined, extrait);
      else if (re === RE_R) ajouter("r", g.stat, `r(${g.df})`, parseFloat(g.p), op, parseFloat(g.df), undefined, extrait);
      else ajouter("z", g.stat, "z", parseFloat(g.p), op, undefined, undefined, extrait);
    }
  }

  const constats: Constat[] = [];
  RE_P_SEUL.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = RE_P_SEUL.exec(t))) {
    const v = parseFloat(matchGroups(m).p);
    if (v === 0) constats.push({ code: "p_zero", severite: "mineur", message: "p = .000 apparaît dans le texte (impossible)." });
    else if (v > 1) constats.push({ code: "p_impossible", severite: "critique", message: `p > 1 rapportée (${v}).` });
  }

  const codesGraves = (r: Resultat) => r.constats.some((c) => c.code === "incoherence" && c.severite !== "mineur");
  const nbIncoherents = resultats.filter((r) => codesGraves(r) || r.constats.some((c) => c.code === "incoherence_inegalite" || c.code === "p_impossible")).length;
  const nbErreurs = resultats.filter((r) => r.constats.some((c) => c.code === "erreur_decision" || c.code === "claim_contredit")).length;
  const nbSig = resultats.filter((r) => (r.pCalculee ?? 1) < alpha).length;

  // score : chaque résultat ne pèse que par son constat le plus grave
  const poids: Record<Severite, number> = { critique: 2, majeur: 0.6, mineur: 0.15, info: 0 };
  let pen = constats.reduce((a, c) => a + poids[c.severite], 0);
  for (const r of resultats) {
    if (r.constats.length) pen += Math.max(...r.constats.map((c) => poids[c.severite]));
  }
  const n = Math.max(6, resultats.length);
  const score = Math.max(0, Math.min(100, Math.round(100 * (1 - pen / (2 * n)))));

  const pValues = resultats
    .map((r) => r.pRapportee)
    .filter((v): v is number => v !== undefined && v > 0 && v <= 1);

  return {
    resultats, constats,
    nbResultats: resultats.length,
    nbSignificatifs: nbSig,
    nbIncoherents, nbErreursDecision: nbErreurs,
    score, pValues,
  };
}

// ─────────────────────────── tableau de descriptifs ───────────────────────────
export interface LigneDescriptif { label: string; n: number; mean: number; sd?: number }
export interface VerdictDescriptif {
  label: string; n: number; mean: number; sd?: number;
  grimOk: boolean; spriteOk?: boolean; spriteMin?: number; spriteMax?: number; message: string;
}

export function auditerDescriptifs(lignes: LigneDescriptif[], lo = 1, hi = 5): VerdictDescriptif[] {
  return lignes.map((l) => {
    const grimOk = grim(l.mean, l.n, 2);
    let spriteOk: boolean | undefined;
    let min: number | undefined, max: number | undefined;
    if (l.sd !== undefined) {
      const s = sprite(l.mean, l.sd, l.n, lo, hi);
      spriteOk = s.possible;
      min = s.min; max = s.max;
    }
    let message = grimOk ? "GRIM : réalisable" : "GRIM : impossible (somme non entière)";
    if (spriteOk === false) message += ` · SPRITE : SD hors bornes [${min?.toFixed(3)} ; ${max?.toFixed(3)}]`;
    if (spriteOk === true) message += " · SPRITE : compatible";
    return { ...l, grimOk, spriteOk, spriteMin: min, spriteMax: max, message };
  });
}

export function bornesSd(n: number, S: number, lo: number, hi: number) {
  return sdBounds(n, S, lo, hi);
}
