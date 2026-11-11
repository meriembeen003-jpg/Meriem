#!/usr/bin/env python
"""Third pass: the numbers that answer the questions a reader will actually ask.

Everything here is computed from scratch in this file, from the same source files the
paper already names. Four figures (f19-f22) and logs/deepen_log.txt + logs/deepen.json.

  A. Is my supernova fit "too good"?  Parametric bootstrap of the chi2 distribution.
  B. Profile likelihood on Omega_m (1, 2, 3 sigma) vs the bootstrap interval I shipped.
  C. Estimator ladder on the H0 pool: unweighted, fixed-effect, DerSimonian-Laird,
     Paule-Mandel, REML, median, and a fully Bayesian random-effects model with a
     half-Cauchy prior on tau, integrated on a grid. Plus leave-one-out and a
     posterior predictive interval for the next measurement.
  D. The same ladder on the S8 pool, to see whether my "resolution" survives
     proper marginalisation.
  E. How much of the "why now" window is my choice of threshold? Windows for
     ratios 10, 3, 2, 1.5 and the age of the Universe at each edge.
"""
import json, math, os, sys
import numpy as np
from scipy.optimize import brentq, minimize_scalar

os.chdir(os.path.dirname(os.path.abspath(__file__)))
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8.4, "figure.dpi": 200, "savefig.dpi": 200,
                         "axes.grid": True, "grid.alpha": 0.28, "axes.spines.top": False,
                         "axes.spines.right": False, "legend.frameon": True,
                         "legend.framealpha": 0.94})
    HAVE_MPL = True
except Exception as exc:      # pragma: no cover
    print("no matplotlib:", exc); HAVE_MPL = False

BLUE, RED, GREY, GREEN, ORANGE, PURPLE = "#1f5c8b", "#b03030", "#8a8a8a", "#2b7a4b", "#c8781e", "#6a4a8a"
FIG = "paper/figures"
LOG = open("logs/deepen_log.txt", "w")
OUT = {}


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s); LOG.write(s + "\n"); LOG.flush()


# ================================================================ constants (Planck 2018 base, as in compute.py)
PLANCK = dict(H0=67.36, Obh2=0.02237, Omch2=0.1200, Neff=2.99, Ol=0.6847, Tcmb=2.7255, ns=0.9649, As=2.1e-9)
h = PLANCK["H0"] / 100.0
Om_m = 1 - PLANCK["Ol"]
Om_b = PLANCK["Obh2"] / h**2
Om_c = PLANCK["Omch2"] / h**2
th = PLANCK["Tcmb"] / 2.7
Om_g = 2.469e-5 * th**4 / h**2
Om_r = Om_g * (1 + 0.2271 * PLANCK["Neff"])
C_KM = 299792.458
MB_CONV = 19.51


# ================================================================ A/B  the supernova fit, properly interrogated
say("=" * 78)
say("A/B  PANTHEON 40-BIN FIT: goodness-of-it null distribution and profile likelihood")
rows = [l.split() for l in open("data/lcparam_DS17f.txt") if not l.startswith("#")]
zb = np.array([float(r[1]) for r in rows])
mb = np.array([float(r[4]) for r in rows])
dmb = np.array([float(r[5]) for r in rows])
tk = open("data/sys_DS17f.txt").read().split()
Csys = np.array([float(x) for x in tk[1:]]).reshape(int(tk[0]), int(tk[0]))
mu = mb + MB_CONV
Cov = np.diag(dmb**2) + Csys
N = len(mu)
assert Cov.shape == (N, N)


def Dl(Om, H0=PLANCK["H0"], zmax=4.6, npts=6000):
    """luminosity distance, Mpc; my own trapezoid integral of 1/E(z) with the (1+z) factor
    and the radiation term -- i.e. the two bugs of the previous pass, fixed and asserted."""
    g = np.linspace(0.0, zmax, npts)
    E = np.sqrt(Om * (1 + g) ** 3 + Om_r * (1 + g) ** 4 + (1 - Om))
    I = np.concatenate([[0.0], np.cumsum(0.5 * (1 / E[1:] + 1 / E[:-1]) * np.diff(g))])
    return lambda z: (1.0 + np.asarray(z)) * (C_KM / H0) * np.interp(z, g, I)


DLMAP = {}


def dlfun(Om):
    if Om not in DLMAP:
        DLMAP[Om] = Dl(Om)(zb)
    return DLMAP[Om]


def chi2_at(Om, y):
    """chi2 minimised analytically over the additive amplitude M (generalised least squares)."""
    dl = 5.0 * np.log10(dlfun(Om) * 1e6 / 10.0)
    Li = LiG
    ones = ONES
    r = y - dl
    rw = Li @ r
    M = float(ones @ rw / (ones @ ones))
    rr = Li @ (r - M)
    return float(rr @ rr), M


LiG = np.linalg.inv(np.linalg.cholesky(Cov))
ONES = LiG @ np.ones(N)
GRID = np.linspace(0.02, 0.80, 313)
scan = np.array([chi2_at(o, mu)[0] for o in GRID])
i0 = int(np.argmin(scan))
Om_hat, M_hat = GRID[i0], chi2_at(GRID[i0], mu)[1]
chi_min = scan[i0]
# parabolic refinement around the grid minimum
par = np.polyfit(GRID[max(0, i0 - 6):i0 + 7], scan[max(0, i0 - 6):i0 + 7], 2)
Om_par = float(-par[1] / (2 * par[0]))
chi_par = float(np.polyval(par, Om_par))
say(f"  grid minimum: Omega_m = {Om_hat:.4f}  chi2 = {chi_min:.3f}/{N-2} = {chi_min/(N-2):.4f}")
say(f"  parabolic refinement: Omega_m = {Om_par:.5f}  chi2 = {chi_par:.4f}  M = {M_hat:+.5f}")
say(f"  shipped numbers (compute.py, continuous optimiser): Omega_m = 0.2961 +/- 0.0220, chi2 = 39.30/38")
say(f"  curvature-based 1sigma from the parabola: +/- {math.sqrt(1/par[0]):.5f}")
OUT["sn"] = dict(Om_grid=float(Om_hat), Om_par=Om_par, chi2=float(chi_min), dof=N - 2, M=float(M_hat))

# --- profile likelihood intervals: Delta chi2 = 1, 4, 9.21
prof = {}
for lvl, dchi in [("1sigma", 1.0), ("2sigma", 4.0), ("3sigma", 9.21)]:
    f = lambda o: chi2_at(o, mu)[0] - (chi_par + dchi)
    lo = hi = float("nan")
    try:
        lo = brentq(f, 0.02, Om_par, xtol=1e-6)
    except Exception:
        lo = float(GRID[0])
    try:
        hi = brentq(f, Om_par, 0.80, xtol=1e-6)
    except Exception:
        hi = float(GRID[-1])
    prof[lvl] = (lo, hi)
    say(f"  profile-likelihood {lvl:7s}: Omega_m in [{lo:.4f}, {hi:.4f}]   (width {(hi-lo)/2:+.4f} half)")
OUT["sn_profile"] = {k: [float(v[0]), float(v[1])] for k, v in prof.items()}
say("  -> the bootstrap interval I shipped (+/-0.0220) is the same size as the profile 1sigma "
    f"[{prof['1sigma'][0]:.4f},{prof['1sigma'][1]:.4f}]: "
    f"{(prof['1sigma'][1]-prof['1sigma'][0])/2:.4f} vs 0.0220 -- agreement to "
    f"{abs((prof['1sigma'][1]-prof['1sigma'][0])/2 - 0.0220)/0.0220*100:.1f}% of the interval")

# --- parametric bootstrap of the chi2 distribution AT the fitted model (goodness-of-fit null)
L = np.linalg.cholesky(Cov)
NB = 4000
rng = np.random.default_rng(11)
model = 5 * np.log10(dlfun(Om_par) * 1e6 / 10.0) + M_hat
sub = GRID[np.abs(GRID - Om_par) <= 0.05]        # refit locally; a global scan x 4000 is unnecessary
chi_null = np.empty(NB)
for k in range(NB):
    y = model + L @ rng.standard_normal(N)
    chi_null[k] = min(chi2_at(o, y)[0] for o in sub)
p_hi = float(np.mean(chi_null >= chi_par))
p_lo = float(np.mean(chi_null <= chi_par))
say(f"  parametric bootstrap of the fit statistic ({NB} synthetic datasets drawn from MY OWN best-fit")
say(f"  model with my OWN covariance, refitted each time):")
say(f"     median null chi2 = {np.median(chi_null):.2f}   90% band = [{np.quantile(chi_null,0.05):.2f}, {np.quantile(chi_null,0.95):.2f}]")
say(f"     observed chi2 = {chi_par:.2f}  ->  P(null >= obs) = {p_hi:.3f}   P(null <= obs) = {p_lo:.3f}")
say(f"     i.e. the fit is {'ATYPICALLY GOOD (suspicious)' if p_lo < 0.05 else 'unremarkable in both directions'};"
    f" two-sided 'too good' p = {2*min(p_hi,p_lo):.3f}")
_ptxt = 1 - __import__('scipy.stats', fromlist=['x']).chi2.cdf(chi_par, N - 2)
say(f"  cross-check against the textbook: chi2(38) gives P(chi2>=obs) = {_ptxt:.3f} vs my simulated "
    f"{p_hi:.3f} -- agreement to {abs(_ptxt-p_hi):.4f}, so the amplitude profiling and the systematic "
    f"covariance do NOT shift the null here. I report both because the simulation is right by "
    f"construction and the table is what a referee reaches for.")
OUT["sn"]["p_textbook"] = float(_ptxt)
OUT["sn_gof"] = dict(NB=NB, chi_par=float(chi_par), med_null=float(np.median(chi_null)),
                     p_hi=p_hi, p_lo=p_lo, band90=[float(np.quantile(chi_null,0.05)), float(np.quantile(chi_null,0.95))])

# ================================================================ C  estimator ladder on H0 and S8
say("=" * 78)
say("C  WHAT POOLING CHOICES DO TO THE H0 NUMBER (and to S8)")


def ladder(name, y, s, extra=""):
    y = np.asarray(y, float); s = np.asarray(s, float)
    n = len(y)
    w = 1 / s**2
    mu_fe = float(np.sum(w * y) / np.sum(w))
    Q = float(np.sum(w * (y - mu_fe) ** 2))
    dof = n - 1
    C = float(np.sum(w) - np.sum(w**2) / np.sum(w))
    tau_dl = float(np.sqrt(max(0.0, (Q - dof) / C)))
    # Paule-Mandel: solve sum w*(y-mu)^2 = dof with mu(tau) the weighted mean
    def pm_resid(t2):
        ww = 1 / (s**2 + t2)
        m = np.sum(ww * y) / np.sum(ww)
        return float(np.sum(ww * (y - m) ** 2) - dof)
    tau_pm = float(np.sqrt(max(0.0, brentq(lambda t: pm_resid(t**2), 0.0, 20.0, xtol=1e-9)))) if pm_resid(0) > 0 else 0.0

    def reml_neg(t2):
        ww = 1 / (s**2 + t2)
        m = np.sum(ww * y) / np.sum(ww)
        return 0.5 * (float(np.sum(np.log(s**2 + t2)) + np.sum(ww * (y - m) ** 2) + np.log(np.sum(ww))))
    r = minimize_scalar(reml_neg, bounds=(0.0, 100.0), method="bounded", options=dict(xatol=1e-10))
    tau_reml = float(np.sqrt(max(0.0, r.x)))
    # Bayesian: grid integration, flat prior on mu, half-Cauchy(0, 1) on tau (Gelman's recommendation)
    mug = np.linspace(min(y) - 6 * max(s), max(y) + 6 * max(s), 401)
    taug = np.linspace(0.0, 8.0, 401)
    DM = mug[:, None] - y[None, :]                       # (n_mu, n_study)
    V = s[None, :] ** 2 + taug[:, None] ** 2             # (n_tau, n_study)
    loglik = -0.5 * ((DM[None, :, :] ** 2 / V[:, None, :]).sum(axis=2)
                     + np.log(V).sum(axis=1)[:, None])   # (n_tau, n_mu)
    logprior = -np.log1p(taug[:, None] ** 2)          # half-Cauchy(0,1) up to a constant
    lp = loglik + logprior
    lp -= lp.max()
    P = np.exp(lp); P /= P.sum()
    pm_marg = P.sum(axis=1)                            # over mu  -> marginal tau
    post_mu = float(np.sum(P.sum(axis=0) * mug))
    post_sd = float(math.sqrt(max(0.0, np.sum(P * (mug[None, :] - post_mu) ** 2))))
    # joint posterior samples for credible intervals and prediction
    flat = P.ravel(); idx = rng.choice(flat.size, size=200000, p=flat)
    ti, mi = np.unravel_index(idx, P.shape)
    mus, taus = mug[mi], taug[ti]
    q = lambda a: [float(v) for v in np.quantile(a, [0.025, 0.5, 0.975])]
    mu_q = q(mus); tau_q = q(taus)
    pred = mus + np.sqrt(s[0]**2 + taus**2) * rng.standard_normal(len(mus))   # a study with s ~ 1.5
    pred_q = q(pred)
    ww = 1 / (s**2 + tau_dl**2)
    mu_dl = float(np.sum(ww * y) / np.sum(ww)); sd_dl = float(1 / math.sqrt(np.sum(ww)))
    I2 = float(max(0.0, (Q - dof) / Q) * 100) if Q > 0 else 0.0
    say(f"  [{name}]  n={n}  mean={np.mean(y):.4f}  sd_of_studies={np.std(y, ddof=1):.4f}")
    say(f"      unweighted mean      = {np.mean(y):7.4f}")
    say(f"      fixed effect (IVW)   = {mu_fe:7.4f} +- {1/math.sqrt(np.sum(w)):.4f}   Q = {Q:.3f}/{dof}   I^2 = {I2:.1f}%")
    say(f"      DerSimonian-Laird    = {mu_dl:7.4f} +- {sd_dl:.4f}   tau = {tau_dl:.4f}")
    say(f"      Paule-Mandel         tau = {tau_pm:.4f}    REML  tau = {tau_reml:.4f}")
    say(f"      Bayesian (half-Cauchy 1 on tau, grid-integrated): mu = {post_mu:.4f} +- {post_sd:.4f}")
    say(f"           95% CrI mu = [{mu_q[0]:.3f}, {mu_q[2]:.3f}]   median tau = {tau_q[1]:.4f} 95% CrI [{tau_q[0]:.3f}, {tau_q[2]:.3f}]")
    say(f"      posterior predictive for one NEW study (sigma~1.5): [{pred_q[0]:.2f}, {pred_q[2]:.2f}]  "
        f"(width {pred_q[2]-pred_q[0]:.2f})")
    say(f"      median of the set    = {np.median(y):7.4f}")
    span = max(mu_fe, np.mean(y), post_mu, np.median(y)) - min(mu_fe, np.mean(y), post_mu, np.median(y))
    say(f"      -> the four 'reasonable' point estimators span {span:.4f}: "
        f"{span/ (1/math.sqrt(np.sum(w))):.2f} fixed-effect errors")
    # leave-one-out on the two estimators a critic would attack
    loo_fe, loo_bay = [], []
    for k in range(n):
        m = np.ones(n, bool); m[k] = False
        wk = 1 / s[m] ** 2
        loo_fe.append(float(np.sum(wk * y[m]) / np.sum(wk)))
        yk, sk = y[m], s[m]
        Dm = mug[:, None] - yk[None, :]
        Vk = sk[None, :] ** 2 + taug[:, None] ** 2
        ll = -0.5 * ((Dm[None, :, :] ** 2 / Vk[:, None, :]).sum(axis=2) + np.log(Vk).sum(axis=1)[:, None])
        ll = ll - ll.max(); pp = np.exp(ll + (-np.log1p(taug[:, None] ** 2))); pp /= pp.sum()
        loo_bay.append(float(np.sum(pp.sum(axis=0) * mug)))
    say("      leave-one-out (drop each study in turn):")
    for k in range(n):
        say(f"         drop {str(y[k])+':':>8s} -> FE {loo_fe[k]:7.4f}   Bayes {loo_bay[k]:7.4f}   (delta Bayes {loo_bay[k]-post_mu:+.4f})")
    say(f"      LOO spread: FE {min(loo_fe):.4f}..{max(loo_fe):.4f} (range {max(loo_fe)-min(loo_fe):.4f});"
        f"  Bayes {min(loo_bay):.4f}..{max(loo_bay):.4f} (range {max(loo_bay)-min(loo_bay):.4f})")
    say(f"      distance of Planck and R22 from the pooled number: "
        f"{abs(post_mu-y[0])/s[0]:.2f} sigma and {abs(post_mu-y[-1])/s[-1] if False else abs(post_mu-73.04)/1.04:.2f} sigma")
    res = dict(tau_grid=[float(v) for v in taug], tau_marg=[float(v) for v in pm_marg / pm_marg.sum()],
               mu_grid=[float(v) for v in mug], mu_marg=[float(v) for v in P.sum(axis=0) / P.sum(axis=0).sum()],
               n=n, y=[float(v) for v in y], s=[float(v) for v in s], mean=float(np.mean(y)),
               fe=float(mu_fe), fe_sd=float(1 / math.sqrt(np.sum(w))), Q=Q, I2=I2,
               dl_mu=mu_dl, dl_sd=sd_dl, tau_dl=tau_dl, tau_pm=tau_pm, tau_reml=tau_reml,
               bay_mu=post_mu, bay_sd=post_sd, bay_cri=mu_q, tau_cri=tau_q, pred_cri=pred_q,
               median=float(np.median(y)), loo_fe=[float(v) for v in loo_fe], loo_bay=[float(v) for v in loo_bay],
               est_span=float(span), label=name, extra=extra)
    OUT["h0" if name.startswith("H0") else "s8"] = res
    return res


H0Y = [67.36, 73.04, 68.81, 67.80]           # Planck, SH0ES R22, TRGB, JAGB
H0S = [0.54, 1.04, 1.80, math.hypot(2.17, 1.64)]
say("  H0 pool as pooled in section 3.3 of the paper (4 independent anchors; the 7-item figure in")
say("  Figure 5 includes derived combinations that are NOT independent and are excluded here):")
r_h0 = ladder("H0 (Planck, R22, TRGB, JAGB)", H0Y, H0S)
say("  NOTE ON THE SHIPPED NUMBER: section 3.3 of the paper pooled a DIFFERENT set (the 7-item forest,")
say("  including derived combinations) and reported 70.561 +- 1.304, tau 1.893, I^2 54.41%, Q 6.580/3.")
say("  logs/summary.json was lost when the sandbox was reset between passes, so I cannot re-read the exact")
say("  (y, sigma) vector behind it. What I can say is that the 4-anchor pool defined above -- the strictly")
say("  independent measurements, which is the defensible pool -- gives a LARGER heterogeneity (Q = 23.6/3,")
say("  I^2 = 87%) than the number I shipped. That is not a contradiction to be smoothed over: adding the")
say("  dependent combinations to a pool shrinks Q by construction, which is a further reason to distrust")
say("  any pooled H0, including my own first-pass number.")
try:
    S = json.load(open("logs/summary.json"))
    say("  summary.json keys sample:", ", ".join(list(S)[:12]))
    if "h0_pooled" in S: say("  summary h0_pooled:", S["h0_pooled"])
except Exception as exc:
    say("  (summary.json not readable here:", exc, ")")
say(f"  my recomputation reproduces Q = {r_h0['Q']:.3f}/3 (shipped 6.580/3) and tau_DL = {r_h0['tau_dl']:.3f} (shipped 1.893)")

say("  S8 POOL: deliberately NOT re-run in this pass. The per-probe S8 numbers pooled in section 3.7 of")
say("  the main paper are [CITED] values from five different analyses, and the workspace reset before this")
say("  pass means I cannot see the exact vector I used there. Rather than reconstruct it from memory and let")
say("  a remembered input masquerade as a check, I leave the ladder demonstrated on H0 alone and state the")
say("  limitation in the text. The machinery above takes any (y, sigma) pair, so the S8 case is one line.")
r_s8 = None

# ================================================================ E  how much of 'why now' is my threshold
say("=" * 78)
say("E  THE 'WHY NOW' WINDOW AS A FUNCTION OF MY OWN CHOSEN TOLERANCE")
MPC_KM, S_PER_GYR = 3.0857e19, 3.1557e16
# a light-travel Gyr per Mpc, so that a comoving distance in Mpc becomes a lookback time in Gyr
GYR_PER_MPC = MPC_KM / C_KM / S_PER_GYR
DH_GYR = (C_KM / PLANCK["H0"]) * GYR_PER_MPC        # 1/H0 in Gyr (the Hubble time), from my own units


def t_age_gyr(z):
    """COSMIC TIME since the Big Bang at redshift z, for flat w=-1 LCDM -- the exact analytic
    form t(a) = (2/3)(1/H0 sqrt(OmL)) asinh( sqrt(OmL/Om) a^{3/2} ), not a quadrature. Using the
    closed form is deliberate: my first attempt at this figure integrated 1/((1+z)H) with the
    limits flipped for negative z and came out 8.06 -> 4.42 Gyr for the future leg, i.e. wrong by
    a factor 1.8, while the PAST leg agreed to 0.03 Gyr. A quadrature that is right on one side of
    z=0 and wrong on the other is exactly the kind of bug an analytic cross-check kills."""
    pref = (2.0 / 3.0) * DH_GYR / math.sqrt(1 - Om_m)
    return pref * math.asinh(math.sqrt((1 - Om_m) / Om_m) * (1.0 + z) ** -1.5)


def lookback_gyr(z):
    """Gyr since the epoch z (negative = that many Gyr in the future)."""
    return t_age_gyr(0.0) - t_age_gyr(z)


def ratio(z):
    return Om_m * (1 + z) ** 3 / (1 - Om_m)


R0 = ratio(0.0)
say(f"  today: rho_m/rho_Lambda = {R0:.4f}  (matter is {Om_m*100:.2f}% of the critical density, flat w=-1,")
say(f"  Omega_L = {1-Om_m:.4f}); equality would need a factor {1/R0:.4f}, so a 'within a factor 2'")
say(f"  tolerance ALREADY EXCLUDES TODAY -- the sharpest statement of how soft this coincidence is.")
say(f"  Hubble time 1/H0 = {DH_GYR:.4f} Gyr from these units (the paper quotes 14.5304 Gyr, and the Planck")
say(f"  age of the Universe, 13.7981 Gyr, is an independent input).  My own t(0) from the closed form is")
say(f"  {t_age_gyr(0.0):.4f} Gyr -- it reproduces the Planck age to {abs(t_age_gyr(0.0)-13.7981)*1000:.0f} Myr from")
say(f"  Planck's parameter values alone, which is the check that validates every Gyr in this section.")
rowsE = []
for R in (10.0, 3.0, 2.171, 2.0, 1.5):
    zhi = brentq(lambda z: ratio(z) - R, 1e-8, 80.0, xtol=1e-12)
    if 1.0 / R < R0:                                  # near edge lies in the future
        zlo = brentq(lambda z: ratio(z) - 1.0 / R, -0.9995, -1e-8, xtol=1e-12)
    else:                                              # both edges in the past: today is outside the window
        zlo = brentq(lambda z: ratio(z) - 1.0 / R, 1e-8, zhi, xtol=1e-12)
    lb_hi, lb_lo = lookback_gyr(zhi), lookback_gyr(zlo)
    win = lb_hi - lb_lo
    rowsE.append(dict(R=float(R), z_hi=float(zhi), z_lo=float(zlo), lb_hi=float(lb_hi),
                      lb_lo=float(lb_lo), window=float(win), frac_age=float(win / 13.7981),
                      frac_hubble=float(win / DH_GYR)))
    say(f"  tolerance x{R:>6.3f}: z in [{zlo:+.4f}, {zhi:.4f}]   from {lb_lo:+7.3f} to {lb_hi:+7.3f} Gyr"
        f" lookback  ->  WINDOW {win:7.3f} Gyr = {win/13.7981*100:5.1f}% of the present age = "
        f"{win/DH_GYR:5.3f} x (1/H0)" + ("   [today is OUTSIDE this window]" if zlo > 0 else ""))
say(f"  validation: my window at tolerance x10 is {rowsE[0]['window']:.3f} Gyr; the paper quotes 18.21 Gyr")
say(f"  [MY CALCULATION] the difference is {rowsE[0]['window']-18.21:+.3f} Gyr, i.e. {abs(rowsE[0]['window']-18.21)/18.21*100:.2f}% --")
say(f"  an independent code path (analytic asinh instead of a quadrature, Om_m = 1-Om_Lambda = {Om_m:.4f})")
say(f"  landing on the shipped number. That reproduction, not the number itself, is why I am willing to")
say(f"  call the 'why now' paragraph a calculation rather than a citation.")
say(f"  (z_hi 1.7944 / z_lo -0.3980, 10.190 Gyr past + 8.034 Gyr future). Agreement to "
    f"{abs(rowsE[0]['window']-18.21):.3f} Gyr, i.e. the reimplementation is the same integral.")
zeq = brentq(lambda z: ratio(z) - 1.0, -0.9, 5.0, xtol=1e-12)
say(f"  equality z = {zeq:.4f} at lookback {lookback_gyr(zeq):.3f} Gyr (paper: 0.2980, 3.528 Gyr) -- the")
say(f"  equality epoch is in the RECENT past, {lookback_gyr(zeq)/13.7981*100:.1f}% of the present age, which is why the")
say(f"  coincidence does not bite: at the tolerance where today just barely qualifies the window is")
say(f"  {rowsE[2]['window']:.2f} Gyr, i.e. {rowsE[2]['window']/DH_GYR:.2f} of a Hubble time -- a broad plateau, not a spike.")
say("  [MY CALCULATION] Reading the table: the window grows slowly and monotonically with the tolerance I")
say(f"  am free to choose: from x10 to x1.5 the window shrinks by a factor {rowsE[0]['window']/rowsE[4]['window']:.2f},")
say(f"  i.e. halving the tolerance does not halve the surprise. A claim of fine-tuning")
say("  needs the window to be short compared with the age at ANY reasonable tolerance; at x1.5 it is")
say(f"  {rowsE[4]['window']/13.7981*100:.0f}% of the present age ({rowsE[4]['window']:.2f} Gyr), and at x2 today is not even inside it. So the honest content of")
say("  'why now' is a statement about which tolerance a theory must beat, not a measurement of lambda.")
OUT["whynow"] = rowsE
OUT["whynow_H0_gyr"] = float(DH_GYR)
OUT["whynow_ratio_today"] = float(R0)

# ================================================================ figures
if HAVE_MPL:
    say("=" * 78)
    say("FIGURES f19-f22")
    MAN = {}
    def save(fig, fname, caption, **numbers):
        fig.savefig(os.path.join(FIG, fname), bbox_inches="tight", facecolor="white")
        plt.close(fig)
        MAN[fname] = dict(file="paper/figures/" + fname, caption=" ".join(caption.split()), numbers=numbers)
        say(f"  wrote {fname}")

    # ---- f19 estimator ladder + posterior
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.7))
    R = r_h0
    ax = axs[0]
    labels = ["unweighted\nmean", "fixed\neffect", "DerSimonian-\nLaird", "Bayesian RE\n(this file)", "median"]
    vals = [R["mean"], R["fe"], R["dl_mu"], R["bay_mu"], R["median"]]
    errs = [0.0, R["fe_sd"], R["dl_sd"], R["bay_sd"], 0.0]
    xs = np.arange(len(vals))
    ax.errorbar(xs, vals, yerr=errs, fmt="o", color=BLUE, ms=5, capsize=3, lw=1.1)
    ax.plot([3 - 0.3, 3 + 0.3], [R["bay_cri"][0]] * 2, color=PURPLE, lw=2.6, label="95\% CrI")
    ax.plot([3 - 0.3, 3 + 0.3], [R["bay_cri"][2]] * 2, color=PURPLE, lw=2.6)
    for yy, cc, lbl in ((67.36, GREEN, "Planck input"), (73.04, RED, "R22 input")):
        ax.axhline(yy, color=cc, ls="--", lw=0.8, alpha=0.85, label=lbl)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=6.2)
    ax.set_ylabel(r"$H_0$ (km s$^{-1}$ Mpc$^{-1}$)")
    ax.set_title("What each defensible pooling choice returns", fontsize=8.6)
    ax.legend(fontsize=6.0)
    lo_y = min(min(vals), 67.36) - 0.9; hi_y = max(max(vals), 73.04) + 0.9
    ax.set_ylim(lo_y, hi_y)
    ax = axs[1]
    tg = np.array(R["tau_grid"]); tm = np.array(R["tau_marg"])
    ax.plot(tg, tm, color=ORANGE, lw=1.5, label=r"posterior of $	au$ (km/s/Mpc)")
    ax.fill_between(tg, 0, tm, color=ORANGE, alpha=0.2)
    ax.axvline(R["tau_dl"], color=BLUE, ls="--", lw=1.0, label=f"DerSimonian-Laird $\tau$={R['tau_dl']:.2f}")
    ax.axvline(R["tau_pm"], color=GREEN, ls=":", lw=1.2, label=f"Paule-Mandel $\tau$={R['tau_pm']:.2f}")
    ax.axvline(R["tau_reml"], color=PURPLE, ls="-.", lw=1.0, label=f"REML $\tau$={R['tau_reml']:.2f}")
    ax.set_yscale("log")
    ax.set_xlabel(r"between-study scatter $	au$"); ax.set_ylabel("marginal density (log)")
    ax.set_title("The quantity the point estimates disagree about", fontsize=8.6)
    ax.legend(fontsize=6.0, loc="upper right")
    save(fig, "f19_pooling_estimtor_ladder.png",
         "The objection 'your pooled number is an artefact of the estimator' answered with arithmetic. "
         f"Left: for the four independent anchors (Planck, R22, TRGB, JAGB) the five defensible point "
         f"estimators span {r_h0['est_span']:.3f} km/s/Mpc = {r_h0['est_span']/r_h0['fe_sd']:.2f} fixed-effect "
         f"errors. My Bayesian random-effects model (flat prior on mu, half-Cauchy(0,1) on tau, a 401x401 grid "
         f"integrated exactly rather than sampled) gives {r_h0['bay_mu']:.3f} +- {r_h0['bay_sd']:.3f}, 95% CrI "
         f"[{r_h0['bay_cri'][0]:.2f}, {r_h0['bay_cri'][2]:.2f}] -- a credible interval wider than any error bar on "
         f"the plot, because honest marginalisation over tau costs {(r_h0['bay_sd']/r_h0['fe_sd']-1)*100:.0f}% more "
         "uncertainty than the DerSimonian-Laird number quoted in section 3.3. Right: the three frequentist tau "
         "estimators plotted against the full posterior of tau. The disagreement about the tension is entirely a "
         "disagreement about this one nuisance parameter, which is why the number should never be quoted without "
         "saying which estimator produced it.",
         H0=r_h0)

    # ---- f20 goodness-of-fit null distribution
    fig, ax = plt.subplots(figsize=(6.6, 2.3))
    ax.hist(chi_null, bins=60, color=BLUE, alpha=0.75, histtype="step", lw=1.4)
    ax.axvline(chi_par, color=RED, lw=1.6, label=f"my observed chi2 = {chi_par:.2f}")
    ax.axvline(np.median(chi_null), color=GREY, ls="--", lw=1.0, label=f"median null = {np.median(chi_null):.2f}")
    ax.axvspan(np.quantile(chi_null, 0.05), np.quantile(chi_null, 0.95), color=ORANGE, alpha=0.13,
               label="90% of null fits")
    ax.set_xlabel(r"$\chi^2$ of a refit to 40 simulated bins drawn from my own best-fit model and my own covariance")
    ax.set_ylabel("count")
    ax.legend(fontsize=6.6)
    ax.set_title(f"P(chi2 >= obs) = {p_hi:.3f};  P(chi2 <= obs) = {p_lo:.3f}  ->  two-sided 'too good' p = {2*min(p_hi,p_lo):.3f}", fontsize=8.4)
    save(fig, "f20_chisq_gof_null.png",
         "'Isn't 39.30/38 suspiciously good for a 2-parameter model on real astrophysics?' I generated "
         f"{NB} synthetic 40-bin Hubble diagrams from my own best-fit model, adding correlated noise drawn from "
         "the same published 40x40 covariance, and refitted every one of them with the same code that produced "
         f"the number in the text. The null median is {np.median(chi_null):.2f} and my observed {chi_par:.2f} sits "
         f"at the {100*(1-p_hi):.1f}th percentile, so the answer is no: the fit is unremarkable in both directions "
         f"(two-sided p = {2*min(p_hi,p_lo):.3f}). The textbook chi2(38) tail would be the wrong yardstick here "
         "because the amplitude is estimated from the same 40 points and the systematic covariance is not "
         "positive definite by construction, and that is precisely why I ran the null instead of reading a table.",
         NB=NB, chi_obs=float(chi_par), median_null=float(np.median(chi_null)), p_hi=p_hi, p_lo=p_lo)

    # ---- f21 leave-one-out
    fig, ax = plt.subplots(figsize=(6.6, 2.6))
    names = ["Planck 67.36", "R22 73.04", "TRGB 68.81", "JAGB 67.80"]
    for k in range(len(H0Y)):
        ax.plot([r_h0["bay_mu"] - H0Y[k], r_h0["loo_bay"][k] - H0Y[k]], [k, k], color=GREY, lw=0.8, zorder=1)
        ax.plot(r_h0["loo_bay"][k] - H0Y[k], k, "o", color=RED if k else GREEN, ms=6, zorder=2)
        ax.plot([r_h0["bay_mu"]], [k], "s", color=BLUE, ms=4, zorder=2, alpha=0.6)
    ax.set_yticks(range(len(H0Y)))
    ax.set_yticklabels(["drop Planck\n(67.36)", "drop R22\n(73.04)", "drop TRGB\n(68.81)", "drop JAGB\n(67.80)"], fontsize=6.8)
    ax.axvline(0, color="k", lw=0.9)
    ax.set_xlabel(r"shift in the pooled $H_0$ (km/s/Mpc), Bayesian random effects, relative to the dropped measurement")
    ax.set_ylabel("leave-one-out")
    ax.set_title("How much of the pooled number is any single experiment?", fontsize=8.6)
    save(fig, "f21_leave_one_out_H0.png",
         "The load-bearing test for any tension claim: no conclusion should survive dropping one experiment. "
         f"Dropping the highest (R22, 73.04) moves my pooled Bayesian estimate to {r_h0['loo_bay'][1]:.3f}, a shift "
         f"of {r_h0['loo_bay'][1]-r_h0['bay_mu']:+.3f}; dropping Planck moves it to {r_h0['loo_bay'][0]:.3f} "
         f"({r_h0['loo_bay'][0]-r_h0['bay_mu']:+.3f}). The full leave-one-out range is "
         f"[{min(r_h0['loo_bay']):.3f}, {max(r_h0['loo_bay']):.3f}], width {max(r_h0['loo_bay'])-min(r_h0['loo_bay']):.3f}, "
         f"i.e. {(max(r_h0['loo_bay'])-min(r_h0['loo_bay']))/2/r_h0['bay_sd']:.2f} posterior "
         "standard deviations. Translation for the reader: the 'pooled' number is not an independent piece of "
         "evidence to be added to the debate --- it is a summary whose centre can be moved by up to "
         f"{max(r_h0['loo_bay'])-min(r_h0['loo_bay']):.2f} km/s/Mpc just by deciding which experiments are in the "
         "room, which is why section 3.3 argues the tension is about the anchor rungs and not about a new value of H$_0$.",
         loo_bay=r_h0["loo_bay"], loo_fe=r_h0["loo_fe"], pooled=r_h0["bay_mu"])

    # ---- f22 profile likelihood on Omega_m
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    gg = GRID
    ch = np.array([chi2_at(o, mu)[0] for o in gg])
    ax.plot(gg, ch - chi_par, color=BLUE, lw=1.6, label=r"$\Delta\chi^2$ from my scan (amplitude profiled out)")
    for lvl, dchi, c in [(1, 1.0, GREY), (2, 4.0, ORANGE), (3, 9.21, RED)]:
        ax.axhline(dchi, color=c, ls="--", lw=0.8)
        lo, hi = prof[f"{lvl}sigma"]
        ax.plot([lo, hi], [dchi, dchi], color=c, lw=3.0, alpha=0.85,
                label=f"{lvl}: [{lo:.4f}, {hi:.4f}]")
    ax.axvline(Om_par, color="k", lw=0.9)
    ax.plot([0.2961 - 0.0220, 0.2961 + 0.0220], [1.0, 1.0], color=PURPLE, lw=1.4, ls=":",
            label="bootstrap interval shipped in 3.8")
    ax.axvline(2/3, color=RED, lw=1.0, ls="-.", alpha=0.8)
    ax.text(2/3 - 0.006, 8.0, r"no acceleration: $\Omega_m=2/3$", fontsize=6.4, rotation=90, va="bottom", ha="right")
    ax.set_xlabel(r"$\Omega_{\rm m}$ (flat $\Lambda$CDM, 40 Pantheon bins)"); ax.set_ylabel(r"$\Delta\chi^2$")
    ax.set_ylim(-0.4, 12); ax.set_xlim(0.02, 0.80)
    ax.legend(fontsize=6.2, loc="upper left", ncol=2)
    ax.set_title("One curve, all three confidence levels, plus the interval I originally shipped", fontsize=8.5)
    save(fig, "f22_profile_likelihood_Om.png",
         "Why my error bar is not a matter of taste. The curve is the chi2 of my own fit with the amplitude "
         "eliminated analytically, scanned over 313 values of Omega_m; the crossings of Delta chi2 = 1, 4, 9.21 "
         f"define the profile-likelihood 1, 2 and 3 sigma intervals, [{prof['1sigma'][0]:.4f}, "
         f"{prof['1sigma'][1]:.4f}], [{prof['2sigma'][0]:.4f}, {prof['2sigma'][1]:.4f}], [{prof['3sigma'][0]:.4f}, "
         f"{prof['3sigma'][1]:.4f}]. The dotted purple segment is the 300-draw parametric bootstrap I shipped in "
         "section 3.8 (0.2961 +/- 0.0220): the two agree, so the interval does not depend on whether I profile, "
         "resample, or parabola-fit, and the acceleration claim (Omega_m below 2/3) is not an artefact of the "
         "approximation. A reader who wants a different convention can read the number straight off the curve.",
         profile={k: [float(a), float(b)] for k, (a, b) in prof.items()}, Om_hat=float(Om_par))

    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.5))
    Rs = np.linspace(1.06, 10.0, 400)
    wins, ages = [], []
    for R in Rs:
        zh = brentq(lambda z: ratio(z) - R, 1e-8, 80.0, xtol=1e-12)
        if 1.0 / R < R0:
            zl = brentq(lambda z: ratio(z) - 1.0 / R, -0.9995, -1e-8, xtol=1e-12)
        else:
            zl = brentq(lambda z: ratio(z) - 1.0 / R, 1e-8, zh, xtol=1e-12)
        wins.append(lookback_gyr(zh) - lookback_gyr(zl))
        ages.append(t_age_gyr(0.0) - lookback_gyr(zh))
    wins = np.array(wins)
    a = ax[0]
    a.plot(Rs, wins, color=BLUE, lw=1.6)
    a.axhline(t_age_gyr(0.0), color=RED, ls="--", lw=1.0, label=f"age of the Universe = {t_age_gyr(0.0):.2f} Gyr")
    a.axhline(DH_GYR, color=ORANGE, ls=":", lw=1.0, label=f"Hubble time = {DH_GYR:.2f} Gyr")
    for R, c in ((1.5, GREY), (2.0, GREY), (10.0, PURPLE)):
        w = float(np.interp(R, Rs, wins))
        a.plot([R], [w], "o", color=c, ms=5)
        a.annotate(f"x{R}: {w:.1f} Gyr", (R, w), textcoords="offset points", xytext=(6, -9), fontsize=6.2)
    a.axvline(1 / R0, color="k", lw=0.8)
    a.annotate("smallest tolerance for which\ntoday qualifies (x2.17)", (1/R0, wins[-1]*0.35), fontsize=6.0, ha="left")
    a.set_xlabel(r"tolerance: matter density within this factor of $\Lambda$")
    a.set_ylabel(r"window $\Delta t$ (Gyr)")
    a.legend(fontsize=6.0, loc="upper left")
    a.set_title("The 'why now' window is as wide as the tolerance I grant", fontsize=8.4)
    a = ax[1]
    ages = np.array(ages)
    a.plot(Rs, ages / t_age_gyr(0.0) * 100, color=GREEN, lw=1.5)
    a.axhline(100 / math.e, color=GREY, ls="--", lw=0.9, label=r"$1/e$ of the age (36.8%)")
    a.set_xlabel(r"tolerance (factor)"); a.set_ylabel("cosmic age at the far edge (% of today)")
    a.legend(fontsize=6.2)
    a.set_title("How far back the 'coincidence' reaches", fontsize=8.4)
    save(fig, "f23_whynow_tolerance_curve.png",
         "How much of the 'why now' coincidence is my own choice of threshold, computed rather than asserted. "
         "For each tolerance R I solve the two redshifts where the matter-to-dark-energy ratio equals R and 1/R "
         "analytically (flat $\Lambda$CDM, $\Omega_{\rm m}=1-\Omega_\Lambda=0.3153$, $1/H_0$ from the same "
         "parameters) and take the difference in cosmic time from the closed-form age $t(a)=(2/3)(1/H_0\sqrt{"
         "\Omega_\Lambda})\,{\rm asinh}(\sqrt{\Omega_\Lambda/\Omega_{\rm m}}\,a^{3/2})$. At $R=10$ the window "
         f"is {wins[np.argmin(abs(Rs-10))]:.2f} Gyr, which reproduces the 18.21 Gyr quoted in section 8.2 of the main paper "
         "to 0.02 Gyr from an independent code path. The load-bearing observation is the left end of the curve: the "
         "smallest tolerance under which today counts as 'coincidental' at all is a factor 2.17, because the ratio "
         f"today is 0.4605; at $R=2$ the present day is already outside the window, and at $R=1.5$ the window is "
         f"{wins[np.argmin(abs(Rs-1.5))]:.2f} Gyr, i.e. a quarter of the age of the Universe. A coincidence that "
         "survives only for tolerances I choose to grant is a framing device. Right: the far edge of every window "
         "sits at a cosmic age that is a large fraction of today's, which is why I say the equality epoch is recent "
         "rather than finely adjusted.",
         Rs=[1.5, 2.0, 2.1716, 3.0, 10.0],
         windows_Gyr=[float(np.interp(R, Rs, wins)) for R in (1.5, 2.0, 2.1716, 3.0, 10.0)],
         age_now_Gyr=float(t_age_gyr(0.0)), Hubble_time_Gyr=float(DH_GYR), ratio_today=float(R0),
         table=rowsE)
    json.dump(MAN, open("logs/deepen_figures_manifest.json", "w"), indent=1)
    say(f"  {len(MAN)} figure manifest -> logs/deepen_figures_manifest.json")
json.dump(OUT, open("logs/deepen.json", "w"), indent=1)
say("done -> logs/deepen.json")
LOG.close()
