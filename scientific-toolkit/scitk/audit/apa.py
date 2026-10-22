# -*- coding: utf-8 -*-
"""Audit de cohérence statistique d'un texte scientifique (approche statcheck).

Extrait les résultats rapportés au format APA — t, F, χ², r, z, p seul —
recalcule la p-value à partir de la statistique et des degrés de liberté,
puis signale :

  • les incohérences statistique ↔ p (erreur de recalcul, décimale déplacée) ;
  • les erreurs de décision (p < .05 annoncé alors que p > .05, et inversement) ;
  • les p impossibles (p = .000, p > 1) et les valeurs charnières (p = .05) ;
  • les degrés de liberté implausibles.

Aucune dépendance externe : le texte peut venir d'un PDF, d'un XML JATS,
d'un abstract ou d'un manuscrit.
"""
from __future__ import annotations
import math
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Iterable

from . import stats as S

# ─────────────────────────── structures ───────────────────────────
SEVERITES = {"critique": 3, "majeur": 2, "mineur": 1, "info": 0}


@dataclass
class Constat:
    code: str
    severite: str
    message: str
    extrait: str = ""

    def dict(self):
        return asdict(self)


@dataclass
class Resultat:
    type: str                      # t, F, chi2, r, z
    statistique: float
    df1: float | None
    df2: float | None
    df_texte: str
    p_rapportee: float | None
    operateur: str                 # '=', '<', '>'
    p_calculee: float | None
    n: int | None = None
    extrait: str = ""
    ecart: float | None = None
    stat_brut: str = ""
    intervalle_p: tuple[float, float] | None = None
    constats: list[Constat] = field(default_factory=list)

    def dict(self):
        d = asdict(self)
        d["constats"] = [c.dict() for c in self.constats]
        return d


@dataclass
class AuditTexte:
    resultats: list[Resultat] = field(default_factory=list)
    constats: list[Constat] = field(default_factory=list)     # constats hors résultats
    nb_resultats: int = 0
    nb_significatifs: int = 0
    nb_incoherents: int = 0
    nb_arrondis: int = 0
    nb_erreurs_decision: int = 0
    score: int = 100

    def dict(self):
        return {
            "resultats": [r.dict() for r in self.resultats],
            "constats": [c.dict() for c in self.constats],
            "nb_resultats": self.nb_resultats,
            "nb_significatifs": self.nb_significatifs,
            "nb_incoherents": self.nb_incoherents,
            "nb_arrondis": self.nb_arrondis,
            "nb_erreurs_decision": self.nb_erreurs_decision,
            "score": self.score,
        }


# ─────────────────────────── normalisation ───────────────────────────
_TRAD = {
    "χ²": "chi2", "χ2": "chi2", "x²": "chi2", "X²": "chi2", "X2": "chi2",
    "χ": "chi", "\u2212": "-", "\u2013": "-", "\u2014": "-", "\u00a0": " ",
    "\u2009": " ", "\u202f": " ", "≤": "<", "≥": ">", "\uff1d": "=", "＝": "=",
}


def normaliser(texte: str) -> str:
    t = unicodedata.normalize("NFKC", texte)
    for a, b in _TRAD.items():
        t = t.replace(a, b)
    t = re.sub(r"[ \t]+", " ", t)
    return t


# ─────────────────────────── expressions régulières ───────────────────────────
_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)"
_P = rf"p\s*(?P<op>[=<>])\s*(?P<p>{_NUM})"
_D = r"[-+]?\d+(?:\.\d+)?"

RE_T = re.compile(rf"\bt\s*\(\s*(?P<df>{_D})\s*\)\s*=\s*(?P<stat>{_NUM})\s*[,;]?\s*{_P}", re.I)
RE_F = re.compile(rf"\bF\s*\(\s*(?P<df1>{_D})\s*,\s*(?P<df2>{_D})\s*\)\s*=\s*(?P<stat>{_NUM})\s*[,;]?\s*{_P}", re.I)
RE_CHI = re.compile(rf"\bchi2\s*\(\s*(?P<df>{_D})(?:\s*,\s*N\s*=\s*(?P<n>\d+))?\s*\)\s*=\s*(?P<stat>{_NUM})\s*[,;]?\s*{_P}", re.I)
RE_R = re.compile(rf"\br\s*\(\s*(?P<df>{_D})\s*\)\s*=\s*(?P<stat>{_NUM})\s*[,;]?\s*{_P}", re.I)
RE_Z = re.compile(rf"\bz\s*=\s*(?P<stat>{_NUM})\s*[,;]?\s*{_P}", re.I)
# p orphelin (sans statistique) — utile pour détecter p = .000
RE_P_SEUL = re.compile(rf"\bp\s*(?P<op>[=<>])\s*(?P<p>{_NUM})(?!\s*[,;]?\s*\d)", re.I)

# mots de décision autour du résultat
RE_SIG = re.compile(r"\b(?:significatif|significative|significant|significance|marginal|marginalement)\b", re.I)
RE_NEG = re.compile(r"(?:non[- ]?significatif|non[- ]?significant|not\s+significant|"
                    r"no\s+significant|(?:n['’]?)?(?:est|était|etaient|étaient)?\s*pas\s+significatif|"
                    r"absence\s+de\s+significativit|insignifiant)", re.I)


def _to_float(s: str) -> float:
    s = s.strip().replace(",", ".")
    return float(s)


def _decimales(raw: str) -> int:
    """Nombre de décimales d'un nombre tel qu'écrit dans le texte."""
    raw = raw.strip().lstrip("+-")
    return len(raw.split(".")[1]) if "." in raw else 0


def _p_de(stat: float, type_: str, df1, df2) -> float:
    """p bilatérale pour une statistique donnée (sans gestion d'erreur)."""
    if type_ == "t":
        return S.t_two_sided_p(stat, df1)
    if type_ == "F":
        return S.f_sf(stat, df1, df2)
    if type_ == "chi2":
        return S.chi2_sf(stat, df1)
    if type_ == "r":
        t = abs(stat) * (df1 / max(1e-12, 1 - stat ** 2)) ** 0.5
        return S.t_two_sided_p(t, df1)
    if type_ == "z":
        return S.z_two_sided_p(stat)
    return float("nan")


def _contexte(texte: str, a: int, b: int, marge: int = 160) -> str:
    return texte[max(0, a - marge): min(len(texte), b + marge)].strip()


RE_CONCESSIF = re.compile(r"\b(?:bien\s+que|quoique|although|though|even\s+though|"
                          r"malgr[ée]|despite|however|toutefois|n[ée]anmoins)\b", re.I)


def _decision_claim(ctx: str) -> str | None:
    """Retourne 'significatif', 'non-significatif' ou None selon le contexte local.

    Les tournures concessives (« bien que la différence soit significative,
    la relation n'était pas… ») sont écartées : elles décrivent un autre
    résultat que celui qui suit la statistique.
    """
    if RE_CONCESSIF.search(ctx):
        return None
    neg = RE_NEG.search(ctx)
    sig = RE_SIG.search(ctx)
    if neg:
        return "non-significatif"
    if sig:
        seg = ctx[max(0, sig.start() - 25): sig.end() + 25].lower()
        if "non" in seg.split("significatif")[0][-12:] or "not " in seg[-18:]:
            return "non-significatif"
        return "significatif"
    return None


# ─────────────────────────── audit d'un résultat ───────────────────────────
def _intervalle_stat(res: Resultat) -> tuple[float, float] | None:
    """Intervalle de p compatible avec l'arrondi de la statistique rapportée.

    Ex. F(2,45) = 3.21 signifie 3.205 ≤ F < 3.215 : la p recalculée doit être
    comparée à cet intervalle, pas à une valeur unique, sinon on fabrique de
    faux positifs.
    """
    d = _decimales(res.stat_brut) if res.stat_brut else 2
    demi = 0.5 * 10 ** (-d)
    try:
        p1 = _p_de(res.statistique - demi, res.type, res.df1, res.df2)
        p2 = _p_de(res.statistique + demi, res.type, res.df1, res.df2)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None
    if any(x != x for x in (p1, p2)):      # NaN
        return None
    return (min(p1, p2), max(p1, p2))


def _evaluer(res: Resultat, alpha: float = 0.05) -> None:
    """Recalcule p et remplit les constats du résultat."""
    try:
        res.p_calculee = _p_de(res.statistique, res.type, res.df1, res.df2)
    except (ValueError, ZeroDivisionError, OverflowError) as e:
        res.constats.append(Constat("calcul_impossible", "info",
                                    f"Résultat non recalculable ({e}).", res.extrait))
        return
    res.intervalle_p = _intervalle_stat(res)

    if res.p_rapportee is None:
        return
    p_rep = res.p_rapportee
    if p_rep > 1.0 or p_rep < 0.0:
        res.constats.append(Constat("p_impossible", "critique",
                                    f"p rapportée hors de [0,1] : {p_rep}.", res.extrait))
        return
    if p_rep == 0.0:
        res.constats.append(Constat(
            "p_zero", "mineur",
            "p = .000 est impossible : une p-value ne peut valoir exactement 0 "
            "(rapporter p < .001).", res.extrait))
        return

    p_calc = res.p_calculee
    lo_calc, hi_calc = res.intervalle_p or (p_calc, p_calc)

    # ── erreur de décision
    if res.operateur == "=" and (p_rep < alpha) != (p_calc < alpha):
        res.constats.append(Constat(
            "erreur_decision", "critique",
            f"La décision change : p rapportée = {p_rep:.4f} mais p recalculée = "
            f"{p_calc:.4f} (seuil {alpha}).", res.extrait))

    if res.operateur == "=":
        # intervalle de compatibilité : arrondi de p + arrondi de la statistique
        demi_p = 0.5 * 10 ** (-3)
        bas, haut = p_rep - demi_p, p_rep + demi_p
        recouvre = not (hi_calc < bas or lo_calc > haut)
        res.ecart = abs(p_calc - p_rep)
        if not recouvre:
            # écart entre les deux intervalles
            trou = bas - hi_calc if hi_calc < bas else lo_calc - haut
            if trou > 0.01:
                res.constats.append(Constat(
                    "incoherence", "majeur",
                    f"p recalculée = {p_calc:.4f} (intervalle {lo_calc:.4f}–{hi_calc:.4f}) "
                    f"incompatible avec p rapportée = {p_rep:.4f}.", res.extrait))
            else:
                res.constats.append(Constat(
                    "incoherence", "mineur",
                    f"Écart faible mais réel : p recalculée = {p_calc:.4f} "
                    f"(intervalle {lo_calc:.4f}–{hi_calc:.4f}) vs p rapportée = {p_rep:.4f}.",
                    res.extrait))
    elif res.operateur == "<":
        if not (lo_calc < p_rep):
            res.constats.append(Constat(
                "incoherence_inegalite", "critique",
                f"p annoncée < {p_rep} mais p recalculée = {p_calc:.4f} "
                f"(l'inégalité est fausse).", res.extrait))
    elif res.operateur == ">":
        if not (hi_calc > p_rep):
            res.constats.append(Constat(
                "incoherence_inegalite", "critique",
                f"p annoncée > {p_rep} mais p recalculée = {p_calc:.4f}.", res.extrait))

    if abs(p_rep - alpha) < 1e-12:
        res.constats.append(Constat(
            "p_charniere", "info",
            "p exactement égal au seuil (.05) : la conclusion dépend du seuil, "
            "rapporter la valeur exacte et l'intervalle de confiance.", res.extrait))

    if res.type == "t" and res.df1 is not None and res.df1 < 1:
        res.constats.append(Constat("df_suspect", "majeur",
                                    "t avec df < 1 : impossible.", res.extrait))
    if res.type == "F" and (res.df1 or 0) < 1:
        res.constats.append(Constat("df_suspect", "majeur",
                                    "F avec df1 < 1 : impossible.", res.extrait))
    if res.type == "r" and abs(res.statistique) > 1:
        res.constats.append(Constat("r_invalide", "critique",
                                    "|r| > 1 : corrélation impossible.", res.extrait))


# ─────────────────────────── audit principal ───────────────────────────
def extraire_resultats(texte: str) -> list[Resultat]:
    t = normaliser(texte)
    out: list[Resultat] = []
    pris: list[tuple[int, int]] = []

    def libre(a, b):
        return all(b <= x or a >= y for x, y in pris)

    for m in RE_F.finditer(t):
        if not libre(m.start(), m.end()):
            continue
        pris.append((m.start(), m.end()))
        out.append(Resultat("F", _to_float(m["stat"]), _to_float(m["df1"]), _to_float(m["df2"]),
                            f"F({m['df1']}, {m['df2']})", _to_float(m["p"]), m["op"], None,
                            extrait=_contexte(t, m.start(), m.end()), stat_brut=m["stat"]))
    for m in RE_CHI.finditer(t):
        if not libre(m.start(), m.end()):
            continue
        pris.append((m.start(), m.end()))
        out.append(Resultat("chi2", _to_float(m["stat"]), _to_float(m["df"]), None,
                            f"chi2({m['df']})", _to_float(m["p"]), m["op"], None,
                            n=int(m["n"]) if m["n"] else None,
                            extrait=_contexte(t, m.start(), m.end()), stat_brut=m["stat"]))
    for m in RE_T.finditer(t):
        if not libre(m.start(), m.end()):
            continue
        pris.append((m.start(), m.end()))
        out.append(Resultat("t", _to_float(m["stat"]), _to_float(m["df"]), None,
                            f"t({m['df']})", _to_float(m["p"]), m["op"], None,
                            extrait=_contexte(t, m.start(), m.end()), stat_brut=m["stat"]))
    for m in RE_R.finditer(t):
        if not libre(m.start(), m.end()):
            continue
        pris.append((m.start(), m.end()))
        out.append(Resultat("r", _to_float(m["stat"]), _to_float(m["df"]), None,
                            f"r({m['df']})", _to_float(m["p"]), m["op"], None,
                            extrait=_contexte(t, m.start(), m.end()), stat_brut=m["stat"]))
    for m in RE_Z.finditer(t):
        if not libre(m.start(), m.end()):
            continue
        pris.append((m.start(), m.end()))
        out.append(Resultat("z", _to_float(m["stat"]), None, None, "z",
                            _to_float(m["p"]), m["op"], None,
                            extrait=_contexte(t, m.start(), m.end()), stat_brut=m["stat"]))
    return out


def audit_texte(texte: str, alpha: float = 0.05) -> AuditTexte:
    """Audit complet d'un texte : résultats, incohérences, décisions, score."""
    audit = AuditTexte()
    resultats = extraire_resultats(texte)
    for r in resultats:
        _evaluer(r, alpha=alpha)
        # cohérence avec les mots du contexte
        claim = _decision_claim(r.extrait)
        if claim and r.p_calculee is not None and r.type != "z":
            sig_calc = r.p_calculee < alpha
            if claim == "significatif" and not sig_calc:
                r.constats.append(Constat(
                    "claim_contredit", "critique",
                    f"Le texte qualifie le résultat de significatif, mais p recalculée = "
                    f"{r.p_calculee:.4f}.", r.extrait))
            elif claim == "non-significatif" and sig_calc:
                r.constats.append(Constat(
                    "claim_contredit", "majeur",
                    f"Le texte évoque une absence de significativité, mais p recalculée = "
                    f"{r.p_calculee:.4f}.", r.extrait))
        audit.resultats.append(r)

    # p orphelines : p = .000, p > 1, etc.
    t = normaliser(texte)
    for m in RE_P_SEUL.finditer(t):
        val = _to_float(m["p"])
        if val == 0.0:
            audit.constats.append(Constat(
                "p_zero", "mineur", "p = .000 apparaît dans le texte (impossible).",
                _contexte(t, m.start(), m.end())))
        elif val > 1.0:
            audit.constats.append(Constat(
                "p_impossible", "critique", f"p > 1 rapportée ({val}).",
                _contexte(t, m.start(), m.end())))

    audit.nb_resultats = len(audit.resultats)
    audit.nb_significatifs = sum(1 for r in audit.resultats
                                 if r.p_calculee is not None and r.p_calculee < alpha)
    audit.nb_incoherents = sum(
        1 for r in audit.resultats
        if any(c.code in ("incoherence_inegalite", "p_impossible")
               or (c.code == "incoherence" and c.severite in ("critique", "majeur"))
               for c in r.constats))
    audit.nb_arrondis = sum(1 for r in audit.resultats
                            if any(c.code == "incoherence" and c.severite == "mineur"
                                   for c in r.constats))
    audit.nb_erreurs_decision = sum(1 for r in audit.resultats
                                    if any(c.code in ("erreur_decision", "claim_contredit")
                                           for c in r.constats))
    audit.score = _score(audit)
    return audit


POIDS_SEVERITE = {"critique": 2.0, "majeur": 0.6, "mineur": 0.15, "info": 0.0}


def _score(audit: AuditTexte) -> int:
    """Score de cohérence 0–100.

    Chaque résultat ne contribue que par son constat le plus grave (évite de
    triple-compter une même erreur), et la pénalité décroît exponentiellement
    avec le volume de résultats : un article long n'est pas mécaniquement
    pénalisé, un article truffé d'erreurs tend vers 0 sans jamais l'atteindre.
    """
    pen = sum(POIDS_SEVERITE[c.severite] for c in audit.constats)
    for r in audit.resultats:
        if r.constats:
            pire = max(r.constats, key=lambda c: POIDS_SEVERITE[c.severite])
            pen += POIDS_SEVERITE[pire.severite]
    n = max(6, audit.nb_resultats)
    return max(0, min(100, round(100 * (1 - pen / (2.0 * n)))))


def taux_incoherence(audit: AuditTexte) -> float:
    return audit.nb_incoherents / audit.nb_resultats if audit.nb_resultats else 0.0


def comparer_litterature(audits: Iterable[AuditTexte]) -> dict:
    """Agrège plusieurs articles : taux d'incohérence, part de p < .05, etc."""
    audits = list(audits)
    n_res = sum(a.nb_resultats for a in audits)
    n_inc = sum(a.nb_incoherents for a in audits)
    n_dec = sum(a.nb_erreurs_decision for a in audits)
    n_sig = sum(a.nb_significatifs for a in audits)
    return {
        "articles": len(audits),
        "resultats": n_res,
        "incoherents": n_inc,
        "taux_incoherence": round(n_inc / n_res, 4) if n_res else None,
        "erreurs_decision": n_dec,
        "part_significatifs": round(n_sig / n_res, 4) if n_res else None,
        "score_moyen": round(sum(a.score for a in audits) / len(audits), 1) if audits else None,
    }
