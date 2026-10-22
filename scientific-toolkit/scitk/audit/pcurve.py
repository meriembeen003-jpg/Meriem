# -*- coding: utf-8 -*-
"""Tests de distribution des p-values : p-curve, excès de significativité,
variance insuffisante (Carlisle), comparaison à l'uniforme.

Ces tests ne prouvent rien sur un article isolé ; ils sont conçus pour un
*corpus* (une revue, un auteur, une période) et se lisent comme des signaux.
"""
from __future__ import annotations
import math
from . import stats as S


def pcurve(pvals: list[float], alpha: float = 0.05) -> dict:
    """p-curve : les p < .05 sont-elles concentrées près de 0 (effet réel)
    ou étalées uniformément (absence d'effet / sélection) ?
    """
    sig = [p for p in pvals if p < alpha]
    n = len(sig)
    if n < 5:
        return {"n": n, "test": "p-curve", "interpretation": "échantillon trop petit (n < 5)"}
    k = sum(1 for p in sig if p < alpha / 2)
    p_binom = S.binomial_sf(k, n, 0.5)          # queue droite
    # p-curve continue : moyenne des p standardisés sous H0 (uniforme)
    moyenne = sum(sig) / n
    attendu = alpha / 2
    # test de Student approché contre la moyenne attendue
    var = sum((p - moyenne) ** 2 for p in sig) / (n - 1) if n > 1 else 0.0
    t = (moyenne - attendu) / math.sqrt(var / n) if var > 0 else 0.0
    p_t = S.t_two_sided_p(t, n - 1)
    d, p_ks = S.ks_uniform(sig)
    return {
        "test": "p-curve",
        "n_significatifs": n,
        "part_p_inf_025": round(k / n, 4),
        "test_skew_binomial_p": round(p_binom, 6),
        "moyenne_p": round(moyenne, 4),
        "t_vs_attendu": round(t, 3),
        "p_moyenne_vs_attendue": round(p_t, 6),
        "ks_uniforme": {"D": round(d, 4) if d == d else None, "p": round(p_ks, 6) if p_ks == p_ks else None},
        "interpretation": (
            ("courbe pentue à droite : compatible avec des effets réels"
             if p_binom < 0.05 and moyenne < attendu else
             "distribution plate ou en hausse près de .05 : compatible avec "
             "une sélection de résultats / un fichier tiroir")
            + (" — n faible, résultat indicatif" if n < 20 else "")
        ),
    }


def exces_significativite(pvals: list[float], alpha: float = 0.05,
                          puissance_estimee: float = 0.5) -> dict:
    """Test d'excès de résultats significatifs (Ioannidis & Trikalinos).

    Compare le nombre observé de p < alpha au nombre attendu si tous les tests
    avaient la puissance indiquée. Fonctionne aussi avec puissance = alpha
    (hypothèse nulle stricte de tests sans effet).
    """
    n = len(pvals)
    if n < 10:
        return {"test": "exces_significativite", "n": n, "interpretation": "n < 10"}
    obs = sum(1 for p in pvals if p < alpha)
    attendu = n * puissance_estimee
    ecart_type = math.sqrt(n * puissance_estimee * (1 - puissance_estimee))
    z = (obs - attendu) / ecart_type if ecart_type > 0 else 0.0
    p = S.z_two_sided_p(z)
    return {
        "test": "excès de significativité",
        "n_tests": n,
        "observes_significatifs": obs,
        "attendus": round(attendu, 2),
        "part_observee": round(obs / n, 4),
        "z": round(z, 3),
        "p": round(p, 6),
        "interpretation": (
            "excès significatif de résultats positifs : suspicion de biais de "
            "publication ou de sélection" if p < 0.05 and z > 0 else
            "pas d'excès détecté"
        ),
    }


def variance_insuffisante(pvals: list[float]) -> dict:
    """Test de variance (style Carlisle) : les p-values rapportées varient-elles
    assez ? Sous H0 uniforme, Var(p) = 1/12. Une variance trop faible suggère
    des valeurs fabriquées ou recopiées.
    """
    n = len(pvals)
    if n < 10:
        return {"test": "variance_insuffisante", "n": n, "interpretation": "n < 10"}
    m = sum(pvals) / n
    var = sum((p - m) ** 2 for p in pvals) / (n - 1)
    stat = (n - 1) * var / (1 / 12)
    # queue basse : une variance trop faible donne un chi² anormalement PETIT
    p_bas = 1.0 - S.chi2_sf(stat, n - 1)
    return {
        "test": "variance insuffisante (Carlisle)",
        "n": n,
        "variance_observee": round(var, 5),
        "variance_attendue": round(1 / 12, 5),
        "chi2": round(stat, 3),
        "p_variance_trop_faible": round(p_bas, 6),
        "interpretation": (
            "variance anormalement faible : p-values possiblement fabriquées ou recopiées"
            if p_bas < 0.01 else "variance compatible avec une distribution uniforme"
        ) + (" (n faible : indicatif)" if n < 30 else ""),
    }


def compter_significatifs(textes_p: list[str]) -> dict:
    """Statistiques descriptives sur une liste de p rapportées en texte."""
    vals = []
    for t in textes_p:
        try:
            v = float(str(t).replace(",", ".").replace("<", "").replace(">", "").strip())
        except ValueError:
            continue
        if 0 <= v <= 1:
            vals.append(v)
    if not vals:
        return {"n": 0}
    sig = [v for v in vals if v < 0.05]
    return {
        "n": len(vals),
        "significatifs": len(sig),
        "part_significatifs": round(len(sig) / len(vals), 4),
        "p_median": round(sorted(vals)[len(vals) // 2], 4),
        "p_min": min(vals),
        "p_max": max(vals),
        "valeurs_charnieres": sum(1 for v in vals if abs(v - 0.05) < 1e-9),
    }
