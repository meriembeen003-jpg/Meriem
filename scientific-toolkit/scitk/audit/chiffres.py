# -*- coding: utf-8 -*-
"""Tests sur les chiffres eux-mêmes : uniformité des décimales, loi de Benford,
valeurs dupliquées, cohérence des pourcentages et des effectifs.

Un excès de zéros/« 5 » terminaux, des moyennes identiques au centième sur des
groupes indépendants ou des pourcentages qui ne totalisent pas 100 sont des
signaux classiques d'erreur de recopie ou de fabrication.
"""
from __future__ import annotations
import math
import re
from collections import Counter
from . import stats as S


def _dernier_chiffre(x: float, decimales: int = 2) -> int:
    return int(round(abs(x) * 10 ** decimales)) % 10


def uniformite_decimales(valeurs: list[float], decimales: int = 2) -> dict:
    """Les chiffres terminaux doivent être uniformément répartis (0–9)."""
    if len(valeurs) < 20:
        return {"test": "uniformité des décimales", "n": len(valeurs),
                "interpretation": "n < 20 : test non informatif"}
    compteur = Counter(_dernier_chiffre(v, decimales) for v in valeurs)
    counts = [compteur.get(d, 0) for d in range(10)]
    chi2, p, df = S.chisq_uniform_test(counts)
    exces_0_5 = (compteur.get(0, 0) + compteur.get(5, 0)) / len(valeurs)
    return {
        "test": "uniformité des décimales",
        "n": len(valeurs),
        "distribution": counts,
        "chi2": round(chi2, 3),
        "df": df,
        "p": round(p, 6),
        "part_0_et_5": round(exces_0_5, 4),
        "interpretation": (
            "excès de chiffres terminaux 0/5 : arrondis suspects ou valeurs inventées"
            if p < 0.01 and exces_0_5 > 0.30 else
            "distribution des décimales compatible avec des mesures réelles"
        ),
    }


def benford(valeurs: list[float], base: int = 10) -> dict:
    """Loi de Benford sur les premiers chiffres significatifs."""
    chiffres = []
    for v in valeurs:
        a = abs(v)
        if a <= 0 or not math.isfinite(a):
            continue
        while a < 1:
            a *= 10
        while a >= 10:
            a /= 10
        chiffres.append(int(a))
    if len(chiffres) < 50:
        return {"test": "Benford", "n": len(chiffres), "interpretation": "n < 50"}
    obs = Counter(chiffres)
    attendus = {d: math.log10(1 + 1 / d) for d in range(1, 10)}
    n = len(chiffres)
    chi2 = sum((obs.get(d, 0) - n * attendus[d]) ** 2 / (n * attendus[d]) for d in range(1, 10))
    p = S.chi2_sf(chi2, 8)
    return {
        "test": "Benford",
        "n": n,
        "chi2": round(chi2, 3),
        "p": round(p, 6),
        "ecarts": {str(d): round(obs.get(d, 0) / n - attendus[d], 4) for d in range(1, 10)},
        "interpretation": (
            "écart à la loi de Benford : anomalie possible (à interpréter avec prudence "
            "— beaucoup de données légitimes ne suivent pas Benford)"
            if p < 0.01 else "compatible avec la loi de Benford"
        ),
    }


def doublons_numeriques(valeurs: list[float], decimales: int = 2,
                        seuil_repetition: int = 3) -> dict:
    """Détecte des valeurs identiques répétées anormalement (M, SD, %) dans
    un tableau : motif fréquent de copier-coller entre lignes."""
    cles = Counter(round(v, decimales) for v in valeurs)
    suspects = {str(k): c for k, c in cles.items() if c >= seuil_repetition}
    return {
        "test": "valeurs répétées",
        "n": len(valeurs),
        "valeurs_repetees": suspects,
        "nb_suspects": len(suspects),
        "interpretation": (
            "plusieurs valeurs identiques répétées : vérifier les tableaux"
            if suspects else "pas de répétition anormale"
        ),
    }


def pourcentages(total: float, parts: list[float], tolerance: float = 0.5) -> dict:
    """Les pourcentages totalisent-ils bien 100 % ?"""
    s = sum(parts)
    return {
        "test": "somme des pourcentages",
        "somme": round(s, 3),
        "ecart": round(s - 100, 3),
        "coherent": abs(s - 100) <= tolerance,
        "interpretation": "cohérent" if abs(s - 100) <= tolerance else
                          f"la somme vaut {s:.1f} % au lieu de 100 %",
    }


def effectifs(n_total: int, parts: list[int]) -> dict:
    """Les effectifs des sous-groupes totalisent-ils N ?"""
    s = sum(parts)
    return {
        "test": "somme des effectifs",
        "somme": s,
        "N": n_total,
        "coherent": s == n_total,
        "interpretation": "cohérent" if s == n_total else f"{s} ≠ N = {n_total}",
    }


def granularite_moyenne(mean: float, n: int, minimum: float = 1.0,
                        maximum: float = 5.0) -> dict:
    """Une moyenne peut-elle provenir de n entiers dans [minimum, maximum] ?"""
    atteignable = minimum * n <= mean * n <= maximum * n
    return {
        "test": "granularité de la moyenne",
        "moyenne": mean, "n": n, "intervalle": [minimum, maximum],
        "coherent": atteignable,
        "interpretation": "cohérent" if atteignable else
                          f"moyenne hors de l'intervalle possible [{minimum}, {maximum}]",
    }


def extraire_nombres(texte: str) -> list[float]:
    return [float(x.replace(",", ".")) for x in
            re.findall(r"[-+]?\d+(?:[.,]\d+)?", texte)]
