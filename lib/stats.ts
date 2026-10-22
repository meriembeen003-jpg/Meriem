// Distributions et tests statistiques — portage TypeScript de scitk/audit/stats.py.
// Aucune dépendance : utilisable dans le navigateur.

const LANCZOS = [
  676.5203681218851, -1259.1392167224028, 771.32342877765313,
  -176.61502916214059, 12.507343278686905, -0.13857109526572012,
  9.9843695780195716e-6, 1.5056327351493116e-7,
];

export function logGamma(z: number): number {
  if (z < 0.5) {
    return Math.log(Math.PI / Math.sin(Math.PI * z)) - logGamma(1 - z);
  }
  z -= 1;
  let x = 0.99999999999980993;
  for (let i = 0; i < LANCZOS.length; i++) x += LANCZOS[i] / (z + i + 1);
  const t = z + LANCZOS.length - 0.5;
  return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
}

export function erf(x: number): number {
  // Abramowitz & Stegun 7.1.26 — précision ~1.5e-7, suffisante pour l'affichage
  const s = Math.sign(x);
  const a = Math.abs(x);
  const t = 1 / (1 + 0.3275911 * a);
  const y =
    1 -
    ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t +
      0.254829592) *
      t *
      Math.exp(-a * a);
  return s * y;
}

export const normCdf = (z: number) => 0.5 * (1 + erf(z / Math.SQRT2));
export const zTwoSidedP = (z: number) => Math.max(0, Math.min(1, 1 - erf(Math.abs(z) / Math.SQRT2)));

function betacf(a: number, b: number, x: number): number {
  const tiny = 1e-300;
  const qab = a + b, qap = a + 1, qam = a - 1;
  let c = 1, d = 1 - (qab * x) / qap;
  if (Math.abs(d) < tiny) d = tiny;
  d = 1 / d;
  let h = d;
  for (let m = 1; m <= 300; m++) {
    const m2 = 2 * m;
    let aa = (m * (b - m) * x) / ((qam + m2) * (a + m2));
    d = 1 + aa * d;
    if (Math.abs(d) < tiny) d = tiny;
    c = 1 + aa / c;
    if (Math.abs(c) < tiny) c = tiny;
    d = 1 / d;
    h *= d * c;
    aa = (-(a + m) * (qab + m) * x) / ((a + m2) * (qap + m2));
    d = 1 + aa * d;
    if (Math.abs(d) < tiny) d = tiny;
    c = 1 + aa / c;
    if (Math.abs(c) < tiny) c = tiny;
    d = 1 / d;
    const delta = d * c;
    h *= delta;
    if (Math.abs(delta - 1) < 3e-16) break;
  }
  return h;
}

export function betaincReg(a: number, b: number, x: number): number {
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  const bt = Math.exp(logGamma(a + b) - logGamma(a) - logGamma(b) + a * Math.log(x) + b * Math.log1p(-x));
  if (x < (a + 1) / (a + b + 2)) return (bt * betacf(a, b, x)) / a;
  return 1 - (bt * betacf(b, a, 1 - x)) / b;
}

function gammaincUpperReg(s: number, x: number): number {
  if (x === 0) return 1;
  if (x < s + 1) {
    let term = 1 / s, total = term, n = s;
    for (let i = 0; i < 1000; i++) {
      n += 1;
      term *= x / n;
      total += term;
      if (Math.abs(term) < Math.abs(total) * 1e-16) break;
    }
    const p = total * Math.exp(-x + s * Math.log(x) - logGamma(s));
    return Math.max(0, Math.min(1, 1 - p));
  }
  const tiny = 1e-300;
  let b = x + 1 - s, c = 1 / tiny, d = 1 / b, h = d;
  for (let i = 1; i < 1000; i++) {
    const an = -i * (i - s);
    b += 2;
    d = an * d + b;
    if (Math.abs(d) < tiny) d = tiny;
    c = b + an / c;
    if (Math.abs(c) < tiny) c = tiny;
    d = 1 / d;
    const delta = d * c;
    h *= delta;
    if (Math.abs(delta - 1) < 1e-16) break;
  }
  return Math.max(0, Math.min(1, Math.exp(-x + s * Math.log(x) - logGamma(s)) * h));
}

export const tTwoSidedP = (t: number, df: number) =>
  df <= 0 ? NaN : betaincReg(df / 2, 0.5, df / (df + t * t));

export const fSf = (f: number, df1: number, df2: number) =>
  f <= 0 ? 1 : betaincReg(df2 / 2, df1 / 2, df2 / (df2 + df1 * f));

export const chi2Sf = (x: number, df: number) => (x <= 0 ? 1 : gammaincUpperReg(df / 2, x / 2));

export function binomialSf(k: number, n: number, p = 0.5): number {
  let s = 0;
  for (let i = k; i <= n; i++) {
    s += Math.exp(logGamma(n + 1) - logGamma(i + 1) - logGamma(n - i + 1) + i * Math.log(p) + (n - i) * Math.log1p(-p));
  }
  return Math.min(1, s);
}

export function chi2Uniform(counts: number[]): { chi2: number; p: number; df: number } {
  const n = counts.reduce((a, b) => a + b, 0);
  const k = counts.length;
  if (k < 2 || n === 0) return { chi2: 0, p: 1, df: 0 };
  const e = n / k;
  const chi2 = counts.reduce((a, c) => a + ((c - e) ** 2) / e, 0);
  return { chi2, p: chi2Sf(chi2, k - 1), df: k - 1 };
}

// ─────────────────────────── GRIM / GRIMMER / SPRITE ───────────────────────────
export function grim(mean: number, n: number, decimals = 2, items = 1): boolean {
  if (n <= 0) return false;
  const demi = 0.5 * 10 ** -decimals;
  const cible = mean * n;
  for (let k = Math.floor(cible) - 10; k <= Math.ceil(cible) + 10; k++) {
    if (k < 0 || k % items !== 0) continue;
    if (Math.abs(k / n - mean) <= demi + 1e-12) return true;
  }
  return false;
}

/** Bornes exactes de l'écart-type pour n entiers de somme S dans [lo, hi]. */
export function sdBounds(n: number, S: number, lo: number, hi: number): [number, number] | null {
  if (n < 2 || S < n * lo || S > n * hi) return null;
  const f = Math.floor(S / n);
  const r = S % n;
  if (f < lo || (r > 0 && f + 1 > hi)) return null;
  const qMin = (n - r) * f * f + r * (f + 1) ** 2;
  let qMax: number;
  if (hi === lo) qMax = n * lo * lo;
  else {
    const t = Math.min(Math.floor((S - n * lo) / (hi - lo)), n);
    const reste = S - t * hi - (n - t) * lo;
    qMax = t >= n ? n * hi * hi : t * hi * hi + (n - t - 1) * lo * lo + (lo + reste) ** 2;
  }
  const vMin = Math.max(0, (qMin - (S * S) / n) / (n - 1));
  const vMax = Math.max(0, (qMax - (S * S) / n) / (n - 1));
  return [Math.sqrt(vMin), Math.sqrt(vMax)];
}

export function sprite(mean: number, sd: number, n: number, lo: number, hi: number) {
  const cible = Math.round(mean * n);
  const bornes: [number, number][] = [];
  for (let S = Math.max(0, cible - 3 * n); S <= cible + 3 * n; S++) {
    if (Math.abs(S / n - mean) > 0.005) continue;
    const b = sdBounds(n, S, lo, hi);
    if (b && b[0] - 0.005 <= sd && sd <= b[1] + 0.005) bornes.push(b);
  }
  if (bornes.length) return { possible: true, min: bornes[0][0], max: bornes[0][1] };
  // sinon : borner quand même pour expliquer
  let mn = Infinity, mx = -Infinity;
  for (let S = Math.max(0, cible - 3 * n); S <= cible + 3 * n; S++) {
    if (Math.abs(S / n - mean) > 0.005) continue;
    const b = sdBounds(n, S, lo, hi);
    if (b) { mn = Math.min(mn, b[0]); mx = Math.max(mx, b[1]); }
  }
  return { possible: false, min: Number.isFinite(mn) ? mn : NaN, max: Number.isFinite(mx) ? mx : NaN };
}
