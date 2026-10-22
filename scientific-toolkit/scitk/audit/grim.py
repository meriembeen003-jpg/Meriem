# -*- coding: utf-8 -*-
"""GRIM, GRIMMER, SPRITE — tests de granularité des statistiques descriptives.

Idée commune : si les données brutes sont des entiers (échelle de Likert,
score total, comptage), alors la moyenne et l'écart-type rapportés ne peuvent
pas prendre n'importe quelle valeur. Un couple (M, SD) impossible est un signal
fort de données fabriquées ou copiées-collées.

Références
  • Brown & Heathers (2017), GRIM — Social Psychological and Personality Science
  • Allard (2018), GRIMMER — Advances in Methods and Practices in Psychological Science
  • Heathers et al. (2018), SPRITE — The R Journal
  • implémentation de référence : package R {scrutiny} (lhdjung), archivé dans vendor/
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, asdict


@dataclass
class Verdict:
    test: str
    possible: bool
    message: str
    details: dict

    def dict(self):
        return asdict(self)


def _arrondi(x: float, d: int) -> float:
    return round(x + 1e-12, d)


def grim(mean: float, n: int, decimals: int = 2, items: int = 1) -> Verdict:
    """La moyenne rapportée est-elle réalisable avec n entiers ?

    items = nombre d'items entiers par participant (score total = somme d'items).
    """
    if n <= 0:
        return Verdict("GRIM", False, "n doit être positif", {"n": n})
    if items < 1:
        return Verdict("GRIM", False, "items doit être >= 1", {"items": items})
    m = _arrondi(mean, decimals)
    cible = m * n
    demi = 0.5 * 10 ** (-decimals)
    faisables = []
    for k in range(max(0, int(math.floor(cible)) - 10), int(math.ceil(cible)) + 11):
        if k % items:
            continue
        if k / n < 0:
            continue
        if abs(k / n - m) <= demi + 1e-12:
            faisables.append(k)
    possible = bool(faisables)
    if not possible:
        arrondis = sorted({_arrondi(k / n, decimals) for k in
                           range(max(0, int(math.floor(cible)) - 60), int(math.ceil(cible)) + 61)
                           if k % items == 0 and k >= 0})
        proche = min(arrondis, key=lambda v: abs(v - m)) if arrondis else None
        msg = (f"M = {m} est impossible avec n = {n} et {items} item(s) entier(s) "
               f"(la somme devrait être {cible:.3f}, donc un multiple de {items})")
        if proche is not None:
            msg += f" ; la moyenne réalisable la plus proche est {proche}"
        return Verdict("GRIM", False, msg,
                       {"moyenne": m, "n": n, "items": items,
                        "somme_attendue": cible, "moyenne_proche": proche})
    return Verdict("GRIM", True,
                   f"M = {m} est réalisable avec n = {n} (somme entière possible).",
                   {"moyenne": m, "n": n, "items": items,
                    "sommes_possibles": faisables[:12]})


def grimmer(mean: float, sd: float, n: int, decimals_mean: int = 2,
            decimals_sd: int = 2, items: int = 1, lo: int | None = None,
            hi: int | None = None, fenetre: int | None = None) -> Verdict:
    """Le couple (M, SD) est-il réalisable avec n entiers ?

    Vérifie l'existence d'une somme S et d'une somme de carrés Q entières
    compatibles avec les valeurs arrondies rapportées.
    """
    g = grim(mean, n, decimals_mean, items)
    if not g.possible:
        return Verdict("GRIMMER", False, "Échec du test GRIM préalable : " + g.message,
                       {"grim": g.details})
    m, s = _arrondi(mean, decimals_mean), _arrondi(sd, decimals_sd)
    if s < 0:
        return Verdict("GRIMMER", False, "Écart-type négatif impossible", {"sd": s})
    dm = 0.5 * 10 ** (-decimals_mean)
    ds = 0.5 * 10 ** (-decimals_sd)
    lo = lo if lo is not None else 0
    hi = hi if hi is not None else max(items, int(math.ceil(m + 6 * max(s, 1))))

    faisables = []
    base = int(round(m * n))
    span = fenetre or max(40, 6 * n)
    for k in range(max(0, base - span), base + span + 1):
        if k % items:
            continue
        if abs(k / n - m) > dm + 1e-12:
            continue
        if not (n * lo <= k <= n * hi):
            continue
        bornes = _bornes_sd(n, k, lo, hi)
        if bornes is not None and not (bornes[0] - ds <= s <= bornes[1] + ds):
            continue        # écart-type hors des bornes atteignables pour cette somme
        # somme de carrés attendue
        q_cible = s * s * (n - 1) + k * k / n
        q_lo, q_hi = int(math.floor(q_cible)) - span * 2, int(math.ceil(q_cible)) + span * 2
        for q in range(max(k, q_lo), q_hi + 1):
            var = (q - k * k / n) / (n - 1)
            if var < 0:
                continue
            sd_calc = math.sqrt(var)
            if abs(sd_calc - s) <= ds + 1e-12:
                if q < k:            # inégalité de Cauchy-Schwarz discrète
                    continue
                faisables.append((k, q))
                break
        if len(faisables) >= 5:
            break

    if faisables:
        return Verdict("GRIMMER", True,
                       f"(M = {m}, SD = {s}) est réalisable avec n = {n}.",
                       {"n": n, "items": items, "solutions": faisables[:5]})
    return Verdict("GRIMMER", False,
                   f"(M = {m}, SD = {s}) est impossible avec n = {n} entiers : "
                   "aucune somme de carrés compatible.",
                   {"moyenne": m, "sd": s, "n": n, "items": items,
                    "motif": "aucune somme de carrés entière ne reproduit cet écart-type"})


def _bornes_sd(n: int, S: int, lo: int, hi: int) -> tuple[float, float] | None:
    """Bornes exactes de l'écart-type pour n entiers de somme S dans [lo, hi].

    • variance minimale : valeurs aussi égales que possible (répartition f / f+1) ;
    • variance maximale : valeurs aussi extrêmes que possible (autant de hi que permis).
    Si la cible tombe hors de ces bornes, la combinaison est *impossible*.
    """
    if n < 2 or S < n * lo or S > n * hi:
        return None
    f, r = divmod(S, n)
    if f < lo or (r and f + 1 > hi):
        return None
    q_min = (n - r) * f * f + r * (f + 1) ** 2
    if hi == lo:
        q_max = n * lo * lo
    else:
        t = (S - n * lo) // (hi - lo)          # nombre de hi
        t = min(t, n)
        reste = S - t * hi - (n - t) * lo
        if t >= n:
            q_max = n * hi * hi
        else:
            q_max = t * hi * hi + (n - t - 1) * lo * lo + (lo + reste) ** 2
    var_min = max(0.0, (q_min - S * S / n) / (n - 1))
    var_max = max(0.0, (q_max - S * S / n) / (n - 1))
    return math.sqrt(var_min), math.sqrt(var_max)


def sprite(mean: float, sd: float, n: int, lo: int, hi: int,
           decimals_mean: int = 2, decimals_sd: int = 2,
           items: int = 1, essais: int = 2000, graine: int = 0) -> Verdict:
    """SPRITE : (M, SD) est-il compatible avec n entiers bornés [lo, hi] ?

    1. test analytique : pour chaque somme S compatible avec la moyenne arrondie,
       on calcule l'intervalle exact des écarts-types atteignables ;
    2. confirmation par construction aléatoire d'une distribution réalisable.
    """
    if n < 2 or hi <= lo:
        return Verdict("SPRITE", False, "Paramètres invalides", {"n": n, "lo": lo, "hi": hi})
    dm = 0.5 * 10 ** (-decimals_mean)
    ds = 0.5 * 10 ** (-decimals_sd)
    cible = int(round(mean * n))
    sommes = [S for S in range(max(0, cible - 3 * n), cible + 3 * n + 1)
              if S % items == 0 and abs(S / n - mean) <= dm + 1e-12
              and n * lo <= S <= n * hi]
    if not sommes:
        return Verdict("SPRITE", False,
                       f"Aucune somme entière ne donne M = {mean} avec n = {n} "
                       f"(test GRIM échoué).", {"moyenne": mean, "n": n})

    compatibles, borne_min, borne_max = [], None, None
    for S in sommes:
        b = _bornes_sd(n, S, lo, hi)
        if b is None:
            continue
        smin, smax = b
        borne_min = smin if borne_min is None else min(borne_min, smin)
        borne_max = smax if borne_max is None else max(borne_max, smax)
        if smin - ds <= sd <= smax + ds:
            compatibles.append((S, smin, smax))

    if not compatibles:
        return Verdict("SPRITE", False,
                       f"SD = {sd} est hors des bornes atteignables "
                       f"[{borne_min:.3f} ; {borne_max:.3f}] pour n = {n} entiers dans "
                       f"[{lo}, {hi}] avec M = {mean}.",
                       {"moyenne": mean, "sd": sd, "n": n, "lo": lo, "hi": hi,
                        "sd_min": borne_min, "sd_max": borne_max})

    # confirmation constructive : on échantillonne des vecteurs de somme S fixée
    rnd = random.Random(graine)
    for S, smin, smax in compatibles[:6]:
        for _ in range(essais // max(1, len(compatibles[:6]))):
            vals = [rnd.randint(lo, hi) for _ in range(n - 1)]
            dernier = S - sum(vals)
            if not lo <= dernier <= hi:
                continue
            vals.append(dernier)
            m = S / n
            s = math.sqrt(sum((v - m) ** 2 for v in vals) / (n - 1))
            if abs(s - sd) <= ds + 1e-12:
                return Verdict("SPRITE", True,
                               f"(M = {mean}, SD = {sd}) est réalisable : n = {n}, "
                               f"valeurs entières dans [{lo}, {hi}].",
                               {"somme": S, "exemple": sorted(vals),
                                "sd_obtenu": round(s, 4), "sd_min": smin, "sd_max": smax})
    return Verdict("SPRITE", True,
                   f"(M = {mean}, SD = {sd}) tombe dans les bornes atteignables "
                   f"[{borne_min:.3f} ; {borne_max:.3f}] : jugé plausible.",
                   {"moyenne": mean, "sd": sd, "n": n, "lo": lo, "hi": hi,
                    "sd_min": borne_min, "sd_max": borne_max,
                    "note": "plausible mais non confirmé par construction aléatoire"})


def audit_descriptifs(lignes, lo: int = 1, hi: int = 5) -> dict:
    """Audite une liste de descriptifs : [{n, mean, sd, decimals_mean, decimals_sd, label}]."""
    resultats = []
    for L in lignes:
        n = int(L["n"])
        m = float(L["mean"])
        dm = int(L.get("decimals_mean", 2))
        dd = int(L.get("decimals_sd", 2))
        g = grim(m, n, dm)
        item = {"label": L.get("label", ""), "n": n, "mean": m, "sd": L.get("sd"),
                "grim": g.dict()}
        if L.get("sd") is not None:
            item["grimmer"] = grimmer(m, float(L["sd"]), n, dm, dd, lo=lo, hi=hi).dict()
            if lo is not None and hi is not None:
                item["sprite"] = sprite(m, float(L["sd"]), n, lo, hi, dm, dd).dict()
        resultats.append(item)
    nb_echecs = sum(1 for r in resultats if not r["grim"]["possible"]
                    or any(not r[k]["possible"] for k in ("grimmer", "sprite") if k in r))
    return {"descriptifs": resultats, "nb_incoherents": nb_echecs,
            "taux": round(nb_echecs / len(resultats), 4) if resultats else None}
