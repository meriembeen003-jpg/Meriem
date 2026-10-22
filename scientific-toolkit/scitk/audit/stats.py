# -*- coding: utf-8 -*-
"""Distributions et conversions d'effets — 100 % bibliothèque standard.

Aucune dépendance à scipy : les fonctions de répartition sont implémentées via
la fonction bêta incomplète (fraction continue de Lentz) et la fonction gamma
incomplète. Précision vérifiée par tests/test_stats.py contre des valeurs de
référence (R, SciPy, tables statistiques).
"""
from __future__ import annotations
import math
from statistics import NormalDist

_N = NormalDist()


# ─────────────────────────── lois de probabilité ───────────────────────────
def norm_cdf(z: float) -> float:
    return _N.cdf(z)


def norm_sf(z: float) -> float:
    """P(Z > z)."""
    return 1.0 - _N.cdf(z)


def z_two_sided_p(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def norm_ppf(p: float) -> float:
    """Quantile de la loi normale centrée réduite."""
    if not 0 < p < 1:
        raise ValueError("p doit être dans ]0,1[")
    return _N.inv_cdf(p)


def _betacf(a: float, b: float, x: float, itmax: int = 300, eps: float = 3e-16) -> float:
    """Fraction continue de la fonction bêta incomplète (modified Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betainc_reg(a: float, b: float, x: float) -> float:
    """Fonction bêta incomplète régularisée I_x(a,b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log1p(-x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def _gammainc_upper_reg(s: float, x: float) -> float:
    """Q(s,x) = Gamma(s,x)/Gamma(s) : gamma incomplète supérieure régularisée."""
    if x < 0 or s <= 0:
        raise ValueError("paramètres invalides")
    if x == 0:
        return 1.0
    if x < s + 1.0:                       # série pour P(s,x)
        term = 1.0 / s
        total = term
        n = s
        for _ in range(1000):
            n += 1.0
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-16:
                break
        p = total * math.exp(-x + s * math.log(x) - math.lgamma(s))
        return max(0.0, min(1.0, 1.0 - p))
    # fraction continue pour Q(s,x)
    tiny = 1e-300
    b = x + 1.0 - s
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - s)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    return max(0.0, min(1.0, math.exp(-x + s * math.log(x) - math.lgamma(s)) * h))


def t_sf(t: float, df: float) -> float:
    """P(T > t) pour une loi de Student."""
    if df <= 0:
        raise ValueError("df doit être > 0")
    x = df / (df + t * t)
    two_sided = betainc_reg(df / 2.0, 0.5, x)
    return two_sided / 2.0 if t >= 0 else 1.0 - two_sided / 2.0


def t_two_sided_p(t: float, df: float) -> float:
    return betainc_reg(df / 2.0, 0.5, df / (df + t * t))


def f_sf(f: float, df1: float, df2: float) -> float:
    """P(F > f)."""
    if f <= 0:
        return 1.0
    return betainc_reg(df2 / 2.0, df1 / 2.0, df2 / (df2 + df1 * f))


def chi2_sf(x: float, df: float) -> float:
    """P(X² > x)."""
    if x <= 0:
        return 1.0
    return _gammainc_upper_reg(df / 2.0, x / 2.0)


def chisq_uniform_test(counts) -> tuple[float, float, int]:
    """Test du chi² d'uniformité sur des effectifs. -> (chi2, p, df)."""
    counts = [c for c in counts]
    n = sum(counts)
    k = len(counts)
    if k < 2 or n == 0:
        return 0.0, 1.0, 0
    exp = n / k
    chi2 = sum((c - exp) ** 2 / exp for c in counts)
    return chi2, chi2_sf(chi2, k - 1), k - 1


def binomial_two_sided(k: int, n: int, p: float = 0.5) -> float:
    """Test binomial exact bilatéral ( méthode des probabilités cumulées )."""
    if n == 0:
        return 1.0
    if p <= 0 or p >= 1:
        raise ValueError("p doit être dans ]0,1[")
    def pmf(i):
        return math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                        + i * math.log(p) + (n - i) * math.log1p(-p))
    obs = pmf(k)
    total = sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs * (1 + 1e-7))
    return min(1.0, total)


def binomial_sf(k: int, n: int, p: float = 0.5) -> float:
    """P(X >= k)."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


# ─────────────────────────── conversions d'effets ───────────────────────────
def t_to_r(t: float, df: float) -> float:
    return t / math.sqrt(t * t + df)


def t_to_d(t: float, df: float) -> float:
    """d de Cohen à partir d'un t (approx. pour échantillons indépendants)."""
    return 2.0 * t / math.sqrt(df)


def f_to_eta2(f: float, df1: float, df2: float) -> float:
    return (df1 * f) / (df1 * f + df2)


def f_to_f2(f: float, df1: float, df2: float) -> float:
    """Taille d'effet f² de Cohen (régression/multivarié)."""
    n = df1 + df2 + 1
    return (f * df1) / df2


def chi2_to_v(chi2: float, n: int, k: int = 2) -> float:
    """V de Cramér."""
    if n <= 0 or k < 2:
        return float("nan")
    return math.sqrt(chi2 / (n * (k - 1)))


def z_to_r(z: float, n: int) -> float:
    return z / math.sqrt(n) if n > 0 else float("nan")


def r_to_z(r: float) -> float:
    """Transformation de Fisher."""
    return 0.5 * math.log((1 + r) / (1 - r)) if -1 < r < 1 else float("inf")


def z_to_p_one_sided(z: float) -> float:
    return norm_sf(z)


def p_to_z(p: float) -> float:
    """Convertit une p-value bilatérale en z (signe positif)."""
    p = max(min(p, 1.0), 1e-300)
    return -norm_ppf(p / 2.0)


def p_interval(p_reported: float, decimals: int) -> tuple[float, float]:
    """Intervalle compatible avec une p arrondie (p = .03 -> [.025, .035[)."""
    half = 0.5 * 10 ** (-decimals)
    return max(0.0, p_reported - half), min(1.0, p_reported + half)


# ─────────────────────────── tests de forme ───────────────────────────
def ks_uniform(pvals: list[float]) -> tuple[float, float]:
    """Statistique de Kolmogorov–Smirnov contre U(0,1) + p approximée."""
    n = len(pvals)
    if n < 5:
        return float("nan"), float("nan")
    xs = sorted(pvals)
    d = max(max(abs((i + 1) / n - x), abs(x - i / n)) for i, x in enumerate(xs))
    # approximation de la valeur-p (série de Kolmogorov)
    lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
    p = 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam) for k in range(1, 101))
    return d, min(max(p, 0.0), 1.0)


def chi2_variance_test(sample: list[float], sigma0: float = 1.0) -> tuple[float, float, int]:
    """Test du chi² sur la variance observée (indicateur de manipulation)."""
    n = len(sample)
    if n < 3:
        return float("nan"), float("nan"), 0
    mean = sum(sample) / n
    var = sum((x - mean) ** 2 for x in sample) / (n - 1)
    stat = (n - 1) * var / (sigma0 ** 2)
    # p bilatéral (queue basse = variance trop faible)
    p = min(1.0, 2 * min(chi2_sf(stat, n - 1), 1 - chi2_sf(stat, n - 1)))
    return stat, p, n - 1
