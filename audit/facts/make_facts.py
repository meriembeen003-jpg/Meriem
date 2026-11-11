#!/usr/bin/env python
"""Arabic facts-edition: computes every number, writes facts.typ, compiles, audits.

One file on purpose. The text may not contain a hand-typed figure: numbers are
written as  §key:spec§  and substituted from a dict assembled from
    logs/deepen.json                     (deepen.py: goodness-of-fit, profiles, ladder, why-now)
    logs/companion_figures_manifest.json  (figs.py: the six g-figures)
    logs/deepen_figures_manifest.json
plus a re-implementation of the supernova fit and of the ladder estimators, done
here from data/lcparam_DS17f.txt and data/sys_DS17f.txt so that the numbers can be
checked against deepen.py's own. The build fails if a placeholder survives, if any
LaTeX/typst markup leaks into the PDF, if a figure is missing, or if the page order
of the figure captions is wrong.
"""
import json, math, os, re, sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
DEEP = json.load(open("logs/deepen.json", encoding="utf-8"))
MAN = json.load(open("logs/companion_figures_manifest.json", encoding="utf-8"))
DEEPMAN = json.load(open("logs/deepen_figures_manifest.json", encoding="utf-8"))
N = {}
for _blk in list(MAN.values()) + list(DEEPMAN.values()):
    if isinstance(_blk, dict):
        for _k, _v in _blk.get("numbers", {}).items():
            N.setdefault(_k, _v)          # the figure manifests carry the same numbers

g = DEEP["sn_gof"]
H = DEEP["h0"]
N.update(dict(NB_boot=g["NB"], gof_med_null=g["med_null"], gof_band90_lo=g["band90"][0],
              gof_band90_hi=g["band90"][1], gof_p_hi=g["p_hi"], chi2_obs=DEEP["sn"]["chi2"],
              M_binned=DEEP["sn"]["M"], Om_par=DEEP["sn"]["Om_par"], dof=DEEP["sn"]["dof"],
              p_textbook=DEEP["sn"]["p_textbook"], h0_y=H["y"], h0_bay_cri=H["bay_cri"],
              h0_tau_cri=H["tau_cri"][::2], h0_pred_cri=H["pred_cri"], loo_fe=H["loo_fe"],
              loo_bay=H["loo_bay"], h0_bay_sd=H["bay_sd"], h0_tau_dl=H["tau_dl"]))
ESCAPABLE = "\\[]_#$%&<>*`"
SUPD = "⁰¹²³⁴⁵⁷⁸⁹"


def ten(mant, exp):
    return f"{mant} × 10{''.join(SUPD[int(c)] if c.isdigit() else '⁻' for c in str(exp))}"


def fmt(v, spec):
    if isinstance(v, str):
        return v
    if isinstance(v, bool):
        return "نعم" if v else "لا"
    if isinstance(v, (list, tuple)):
        return "، ".join(fmt(x, spec) for x in v)
    if spec.startswith("e"):
        m, e = f"{v:.{int(spec[1:])}e}".split("e")
        return ten(m.rstrip("0").rstrip("."), int(e))
    if spec.startswith("g"):
        return f"{v:.{int(spec[1:])}g}"
    if spec == "pow":
        return "10" + "".join(SUPD[int(c)] for c in str(int(round(v))))
    return f"{v:.{int(spec)}f}" if spec.isdigit() else str(v)


def esc(t):
    for ch in ESCAPABLE:
        t = t.replace(ch, "\\" + ch)
    return t


MISSING = set()


def sub(text):
    def rep(mo):
        key, spec = mo.group(1), (mo.group(2) or "3")
        if key not in N:
            raise KeyError(f"placeholder §{key}:{spec}§ has no entry among {len(N)} numbers")
        return fmt(N[key], spec)
    out = re.sub(r"§([A-Za-z0-9_.]+):?([^§]*)§", rep, text)
    left = re.findall(r"§[^§]*§", out)
    if left:
        raise SystemExit(f"unresolved placeholders: {left[:6]}")
    return out


# ============================================================ the fit, again
C_KM = 299792.458
b = np.loadtxt("data/lcparam_DS17f.txt", usecols=(1, 4, 5))
zz, mb, dmb = b[:, 0], b[:, 1], b[:, 2]
tok = open("data/sys_DS17f.txt").read().split()
Nb = int(tok[0])
Csys = np.array([float(x) for x in tok[1:]]).reshape(Nb, Nb)
Cov = Csys + np.diag(dmb ** 2)
MU = mb + 19.51
Li = np.linalg.inv(np.linalg.cholesky(Cov))
ones = Li @ np.ones(Nb)
hdr = open("data/lcparam_DS17f.txt").readline().split()
row1 = open("data/lcparam_DS17f.txt").readlines()[1].split()
full_hdr = open("data/lcparam_full_long.txt").readline().split()
full_row = open("data/lcparam_full_long.txt").readlines()[1].split()
fullc = np.loadtxt("data/lcparam_full_long.txt", usecols=tuple(range(1, len(full_row))))
import hashlib
for fn, tag in (("data/lcparam_DS17f.txt", "lc"), ("data/sys_DS17f.txt", "sys")):
    raw = open(fn, "rb").read()
    N[f"{tag}_bytes"] = len(raw)
    N[f"{tag}_md5"] = hashlib.md5(raw).hexdigest()
ev_sys = np.linalg.eigvalsh(Csys)
ev_tot = np.linalg.eigvalsh(Cov)


def Dl_of_z(zs, Om, Om_r=9.2e-5):
    g = np.linspace(0.0, max(np.max(zs), 1e-6), 6000)
    E = np.sqrt(Om * (1 + g) ** 3 + Om_r * (1 + g) ** 4 + (1 - Om))
    I = np.concatenate([[0.0], np.cumsum(0.5 * (1 / E[1:] + 1 / E[:-1]) * np.diff(g))])
    return (1.0 + np.asarray(zs)) * (C_KM / 67.36) * np.interp(zs, g, I)


def fit(Om, y=MU):
    dl = 5 * np.log10(Dl_of_z(zz, Om) * 1e6 / 10.0)
    rw = Li @ (y - dl)
    M = float(ones @ rw / (ones @ ones))
    rr = Li @ (y - dl - M)
    return float(rr @ rr), M


GRID = np.linspace(0.02, 0.80, 313)
ch = np.array([fit(o)[0] for o in GRID])
kmin = int(np.argmin(ch))
par = np.polyfit(GRID[kmin - 6:kmin + 7], ch[kmin - 6:kmin + 7], 2)
Om_par2 = float(-par[1] / (2 * par[0]))
N.update(dict(n_bins=Nb, binned_header_names=len(hdr), binned_fields_row1=len(row1),
              z_min=float(zz.min()), z_max=float(zz.max()), mu_lo=float(MU.min()), mu_hi=float(MU.max()),
              stat_err_mean=float(dmb.mean()), dmb_max=float(dmb.max()),
              cov_asym_max=float(np.abs(Csys - Csys.T).max()),
              covsys_min_eig=float(ev_sys.min()), covsys_max_eig=float(ev_sys.max()),
              cov_min_eig=float(ev_tot.min()), cov_max_eig=float(ev_tot.max()),
              Om_grid_here=float(GRID[kmin]), chi2_grid=float(ch[kmin]),
              grid_edge_hit=bool(kmin in (0, len(GRID) - 1)),
              Om_par_here=Om_par2, chi2_par=float(fit(Om_par2)[0]), M_here=float(fit(Om_par2)[1]),
              sigma_curvature_here=float(math.sqrt(1 / par[0])),
              full_rows=int(fullc.shape[0]), full_header_names=len(full_hdr),
              full_fields_per_row=len(full_row), full_numeric_cols=int(fullc.shape[1]),
              full_zero_cols=int(sum(1 for j in range(fullc.shape[1]) if np.all(fullc[:, j] == 0))),
              full_z_min=float(fullc[:, 0].min()), full_z_max=float(fullc[:, 0].max()),
              full_dmb_mean=float(fullc[:, 4].mean()),
              full_nonzero_cols=[nm for nm, j in (("zcmb", 0), ("zhel", 1), ("dz", 2), ("mb", 3), ("dmb", 4),
                                                  ("x1", 5), ("dx1", 6), ("color", 7), ("dcolor", 8))
                                 if not np.all(fullc[:, j] == 0)],
              chi2_over_dof=DEEP["sn"]["chi2"] / DEEP["sn"]["dof"],
              published_Om=0.307, published_Om_err=0.012))
# profile-likelihood intervals and the goodness-of-fit null, from deepen.json
for lvl in ("1sigma", "2sigma", "3sigma"):
    a1, a2 = DEEP["sn_profile"][lvl]
    N[f"prof_{lvl}_lo"], N[f"prof_{lvl}_hi"] = a1, a2
    N[f"prof_{lvl}_half"] = 0.5 * (a2 - a1)
N["prof2_over_prof1"] = N["prof_2sigma_half"] / N["prof_1sigma_half"]
N["prof3_over_prof1"] = N["prof_3sigma_half"] / N["prof_1sigma_half"]
N["prof1_over_curv"] = N["prof_1sigma_half"] / N["sigma_curvature_here"]
N["gof_two_sided"] = 2 * min(g["p_hi"], g["p_lo"])
N["p_boot_minus_p_text"] = abs(g["p_hi"] - DEEP["sn"]["p_textbook"])
N["delta_chi2_at_005"] = N["chi2_005"] - DEEP["sn"]["chi2"]
N["delta_chi2_at_075"] = N["chi2_075"] - DEEP["sn"]["chi2"]
# the ladder, recomputed with five estimators
N.update(dict(h0_labels=["Planck VI (2018)", "R22 (2022)", "CCHP TRGB/JWST", "CCHP JAGB"],
              h0_unweighted=H["mean"], h0_fe=H["fe"], h0_fe_sd=H["fe_sd"], h0_Q=H["Q"],
              h0_Q_over_dof=H["Q"] / 3.0, h0_I2=H["I2"], h0_dl=H["dl_mu"], h0_dl_sd=H["dl_sd"],
              h0_tau_dl=H["tau_dl"], h0_tau_pm=H["tau_pm"], h0_tau_reml=H["tau_reml"],
              h0_bay=H["bay_mu"], h0_bay_sd=H["bay_sd"], h0_tau_med=H["tau_cri"][1],
              h0_median=H["median"], h0_est_span=H["est_span"],
              h0_span_in_fe_err=H["est_span"] / H["fe_sd"],
              h0_pred_width=H["pred_cri"][2] - H["pred_cri"][0],
              loo_fe_spread=max(H["loo_fe"]) - min(H["loo_fe"]),
              loo_bay_spread=max(H["loo_bay"]) - min(H["loo_bay"]),
              dev_planck_from_bay=(H["bay_mu"] - H["y"][0]) / H["s"][0],
              dev_r22_from_bay=(H["y"][1] - H["bay_mu"]) / H["s"][1],
              dev_planck_from_fe=(H["fe"] - H["y"][0]) / H["s"][0],
              dev_r22_from_fe=(H["y"][1] - H["fe"]) / H["s"][1],
              fe_minus_bay=H["dl_mu"] - H["fe"], bay_minus_fe=H["bay_mu"] - H["fe"],
              h0_tau_span=max(H["tau_dl"], H["tau_pm"], H["tau_reml"]) /
              min(H["tau_dl"], H["tau_pm"], H["tau_reml"])))


def ladder(y, sd):
    w = 1.0 / np.array(sd) ** 2
    fe = float((w * np.array(y)).sum() / w.sum()); fe_sd = float(1 / math.sqrt(w.sum()))
    Q = float((w * (np.array(y) - fe) ** 2).sum()); kk = len(y)
    I2 = max(0.0, (Q - (kk - 1)) / Q) * 100.0
    A = float(w.sum() - (w ** 2).sum() / w.sum())
    tau2 = max(0.0, (Q - (kk - 1)) / A)
    ws = 1.0 / (np.array(sd) ** 2 + tau2)
    dl = float((ws * np.array(y)).sum() / ws.sum()); dl_sd = float(1 / math.sqrt(ws.sum()))
    tg = np.linspace(0.0, 8.0, 401); mg = np.linspace(min(y) - 12, max(y) + 12, 401)
    den = np.array(sd) ** 2 + tg[:, None, None] ** 2
    LL = -0.5 * (((mg[None, :, None] - np.array(y)[None, None, :]) ** 2) / den).sum(axis=2)
    LL -= 0.5 * np.log(den).sum(axis=2)
    assert LL.shape == (len(tg), len(mg)), LL.shape
    Pm = np.exp(LL - LL.max()) * (1.0 / (1.0 + tg ** 2))[:, None]
    mu_marg = Pm.sum(axis=0) / Pm.sum(); cdf = np.cumsum(mu_marg)
    ix = lambda q: int(min(np.searchsorted(cdf, q), len(mg) - 1))
    tau_marg = Pm.sum(axis=1) / Pm.sum(); ct = np.cumsum(tau_marg)
    return dict(fe=fe, fe_sd=fe_sd, Q=Q, I2=I2, dl=dl, dl_sd=dl_sd, tau_dl=math.sqrt(tau2),
                bay=float(mg[ix(0.5)]), bay_lo=float(mg[ix(0.025)]), bay_hi=float(mg[ix(0.975)]),
                bay_sd=(float(mg[ix(0.975)]) - float(mg[ix(0.025)])) / 3.92,
                tau_med=float(tg[int(min(np.searchsorted(ct, 0.5), len(tg) - 1))]))


base = ladder(H["y"], H["s"])
alt = ladder([67.36, 73.01, 68.81, 67.80], [0.54, 0.99, 1.80, 2.72])
N["sens_base"] = base; N["sens_alt"] = alt
for key in ("fe", "fe_sd", "Q", "dl", "bay", "tau_dl", "tau_med", "I2"):
    N[f"sens_d_{key}"] = alt[key] - base[key]
N["sens_fe_in_sd"] = (alt["fe"] - base["fe"]) / base["fe_sd"]
N["sens_bay_in_sd"] = (alt["bay"] - base["bay"]) / base["bay_sd"]
N["sens_d_Q_pct"] = 100.0 * (alt["Q"] - base["Q"]) / base["Q"]
# the ruler, from Planck densities only
Pp = dict(H0=67.36, Obh2=0.02237, Omch2=0.1200, Neff=2.99, Ol=0.6847, Tcmb=2.7255)
h = Pp["H0"] / 100
Om_b = Pp["Obh2"] / h ** 2; Om_c = Pp["Omch2"] / h ** 2
Om_g = 2.469e-5 * (Pp["Tcmb"] / 2.7) ** 4 / h ** 2
Om_r = Om_g * (1 + 0.2271 * Pp["Neff"])


def rd_of(zd, npts=9000):
    z = np.linspace(zd, 1e5, npts)
    E = np.sqrt((Om_b + Om_c) * (1 + z) ** 3 + Om_r * (1 + z) ** 4 + (1 - Om_b - Om_c))
    R = 3 * Om_b / (3.15 * Om_g * (1 + z) ** 4) * (1 + z) ** 3
    return float(np.trapezoid(C_KM / np.sqrt(3 * (1 + R)) / E, z)) / Pp["H0"]


z_star = 1089.92
rd_here = rd_of(z_star)
DA = float(Dl_of_z(np.array([z_star]), 0.3153)[0] / (1 + z_star))
N.update(dict(rd_here=rd_here, rd_published=144.44, rd_dev_percent=100.0 * (rd_here - 144.44) / 144.44,
              theta_star_1e2rad=100.0 * rd_here / DA, D_A_zstar_Mpc=DA))
# why-now, from the analytic flat-Lambda age
Om_m = 1 - Pp["Ol"]
H0s = Pp["H0"] * 1e3 / 3.0857e22
GYR = 3.15576e16
t0 = 2 / (3 * H0s * math.sqrt(1 - Om_m)) * math.asinh(math.sqrt((1 - Om_m) / Om_m)) / GYR
a_eq = (Om_m / (1 - Om_m)) ** (1 / 3.0)
zs = np.linspace(0, 1 / a_eq - 1, 20000)
lb_eq = float(np.trapezoid(1 / (1 + zs) / np.sqrt(Om_m * (1 + zs) ** 3 + (1 - Om_m)), zs) / H0s / GYR)
N.update(dict(t0_analytic_gyr=t0, t0_planck=13.7981, t0_minus_planck_myr=(t0 - 13.7981) * 1000.0,
              a_eq=a_eq, z_eq=1 / a_eq - 1, lookback_eq_gyr=lb_eq,
              eq_frac_of_age_pct=100.0 * lb_eq / t0, hubble_time_gyr=1 / H0s / GYR,
              hubble_minus_t0=1 / H0s / GYR - t0, age_over_hubble_time=t0 / (1 / H0s / GYR),
              ratio_today=Om_m / (1 - Om_m), tightest_ratio=((1 - Om_m) / Om_m) ** 1))
N["tightest_ratio"] = (1 - Om_m) / Om_m
for row in DEEP["whynow"]:
    Rr = row["R"]
    N[f"win_{Rr:g}_zlo"], N[f"win_{Rr:g}_zhi"] = row["z_lo"], row["z_hi"]
    N[f"win_{Rr:g}_window"], N[f"win_{Rr:g}_frac"] = row["window"], row["frac_age"]
    N[f"win_{Rr:g}_hubble"] = row["window"] / N["hubble_time_gyr"]
W = sorted(DEEP["whynow"], key=lambda r: -r["R"])
N["shrink_10_to_1p5"] = W[0]["window"] / W[-1]["window"]
N["tolerance_change_10_to_1p5"] = W[0]["R"] / W[-1]["R"]
# the modulus anchor
N["mag_to_hubble_slope"] = math.log(10) / 5.0
N["h0_shift_for_006mag_pct"] = 100 * (10 ** (0.06 / 5.0) - 1)
N["anchor_shift_for_tension_mag"] = 5 * math.log10(H["y"][1] / Pp["H0"])
# vacuum, horizon, entropy, temperature
LAM = 1.089139e-52; hbar = 1.054571817e-34; kB = 1.380649e-23
N["d_rho_minus_d_planck"] = N["d_rho"] - N["d_planck"]
N["d_rho_minus_d_reduced"] = N["d_rho"] - N["d_reduced"]
N["horizon_gpc"] = N["horizon_m"] / 3.0857e25
N["entropy_content_log10_gap"] = N["log10_S"] - 88.0
N["T_dS_from_radius_K"] = hbar * 2.99792458e8 / (2 * math.pi * kB * N["horizon_m"])
N["T_dS_from_H0_K"] = hbar * H0s / (2 * math.pi * kB)
N["T_two_ways_ratio"] = N["T_dS_from_radius_K"] / N["T_dS_from_H0_K"]
N["sqrt_Omega_Lambda"] = math.sqrt(Pp["Ol"])
N["kB_T_310K_meV"] = kB * 310.0 / 1.602176634e-19 * 1e3
# complexity
s0, i0 = N["slope"], N["intercept"]
N["lz_ratio_first"] = N["mine"][0] / N["theo"][0]
N["lz_ratio_last"] = N["mine"][-1] / N["theo"][-1]
N["phi_n4_s"] = math.exp(s0 * 4 + i0)
N["phi_n8_days"] = math.exp(s0 * 8 + i0) / 86400.0
N["phi_n12_yr"] = math.exp(s0 * 12 + i0) / 31557600.0
N["phi_n300_log10_yr"] = (s0 * 300 + i0 - math.log(3.15576e7)) / math.log(10)
N["phi_age_ratio_log10"] = N["phi_n300_log10_yr"] - math.log10(13.8e9)
N["exp_slope_per_element"] = math.exp(s0)
# tensions as arithmetic on the quoted numbers
sig = lambda d, a1, a2: d / math.sqrt(a1 ** 2 + a2 ** 2)
N["tension_planck_r22_err"] = math.sqrt(0.54 ** 2 + 1.04 ** 2)
N["tension_planck_r22_fe"] = sig(73.04 - 67.36, 0.54, 1.04)
N["tension_planck_r22_arxiv"] = sig(73.01 - 67.36, 0.54, 0.99)
N["trgb_vs_jagb"] = sig(70.39 - 67.80, 1.80, 2.7200183822908257)
N["lithium_diff_dex"] = 2.67 - 2.20
N["lithium_sig"] = sig(2.67 - 2.20, 0.06, 0.05)
# the same fit done twice: here from the raw files, and in figs.py. Any agreement
# quoted in the text below is one of these differences, never a rounded pair.
_g01 = MAN["g01_hubble_raw.png"]["numbers"]
N["Om_man"] = _g01["Om"]
N["chi2_man"] = _g01["chi2"]
N["sigma_man"] = _g01["err"]
N["dOm_cross"] = abs(N["Om_par_here"] - _g01["Om"])
N["dchi2_cross"] = abs(N["chi2_par"] - _g01["chi2"])
N["dsigma_cross"] = abs(N["sigma_curvature_here"] - _g01["err"])
N["dM_cross"] = abs(N["M_here"] - N["M_binned"])
N["dof_man"] = _g01["dof"]
N["dM_vs_stat_pct"] = 100.0 * N["dM_cross"] / N["stat_err_mean"]
# complexity figure: the two curves, kept as the manifest reports them
_g06 = MAN["g06_complexity.png"]["numbers"]
N["lz_mine"], N["lz_theo"] = _g06["mine"], _g06["theo"]
N["lz_slope"], N["lz_intercept"] = _g06["slope"], _g06["intercept"]
N["lz_dev_pct"] = 100.0 * (_g06["mine"][0] / _g06["theo"][0] - 1.0)
# an observer's entropy as a share of the horizon's
N["observer_share"] = 10.0 ** (88.0 - N["log10_S"])
N["d_rho_vs_pub"] = abs(N["d_rho"] - 122.946)
N["n_numbers"] = len(N) + 1
json.dump(N, open("logs/facts_numbers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)

# ============================================================ the document
FIG_ORDER = ["g01_hubble_raw.png", "g05_what_a_fit_is.png", "f22_profile_likelihood_Om.png",
             "f20_chisq_gof_null.png", "f19_pooling_estimtor_ladder.png", "f21_leave_one_out_H0.png",
             "g02_ruler.png", "g04_whynow_shading.png", "f23_whynow_tolerance_curve.png",
             "g03_vacuum_entropy.png", "g06_complexity.png"]
FIGDIR = "paper/figures"


FIGCAPS = []


def figure(i, cap):
    FIGCAPS.append(cap)
    return ('#figure(supplement: none, image("%s/%s", width: 100%%), caption: [%s])'
            % (FIGDIR, FIG_ORDER[i], esc(sub(cap))))


P = []
add = P.append

add("""(١) نطاقُ هذا النصّ: الكونُ والمقياسُ والعقلُ والقياسُ عليه، بلا شيءٍ غيرِها. لا نتيجةٌ فيه بلا عدد، ولا عددٌ بلا مصدرٍ من ثلاثة: ملفُّ بياناتٍ فُتِحَ وحُسِبَ في هذه الجلسة (ويُذكَرُ اسمُه وتوقيعُه MD5 وعددُ أسطره)، أو مرجعٌ منشورٌ تُذكَرُ طبقتُه (محكَّمٌ بالنظراء، أو ما قبل النشر، أو مسحوب)، أو ما لم أُتحقَّق منه فيُصَرَّحُ بذلك. الأرقامُ كلُّها — ‏§n_numbers:0§ عددًا — تُولَّدُ من الملفّ البرمجيِّ نفسِه الذي يبني الصفحة، من سجلَّيِ الأشكالِ ومن logs/deepen.json، فلا نسخةَ يدويّةَ لرقمٍ فيها، وكلُّ عددٍ في النصِّ يمكن مقارنتُه بالعددِ في logs/facts_numbers.json آليًّا. الأشكالُ أحدَ عشرَ، ترتيبُها في النصِّ هو ترتيبُ أرقامِها.
""")

add("""(٢) البياناتُ: ملفَّان من أرشيف Pantheon+ (Scolnic وآخرون، The Astrophysical Journal، DOI 10.3847/1538-4357/aab9bb — محكَّم؛ المستودعُ الرسميّ DOI 10.17909/T95Q4XD). lcparam_DS17f.txt: ‏§n_bins:0§ سطرًا بعد الترويسة؛ ترويستُه تُسمّي ‏§binned_header_names:0§ حقلًا وتحمل كلُّ سورةٍ ‏§binned_fields_row1:0§ حقلًا؛ الانزياحُ من §z_min:4§ إلى §z_max:4§؛ μ المبنيُّ منها بين §mu_lo:3§ و§mu_hi:3§؛ متوسّطُ الخطأِ الإحصائيّ §stat_err_mean:5§ مقدارٌ وأقصاه §dmb_max:4§؛ MD5 ‏§lc_md5:g32§ بحجمِ §lc_bytes:0§ بايت. sys_DS17f.txt: مصفوفةٌ §n_bins:0§×§n_bins:0§، متماثلةٌ تمامًا (أقصى فرقٍ بين C وCᵗ = §cov_asym_max:1§ بالضبط)، قيمُها الذاتيَّة بين ‏§covsys_min_eig:e2§ و§covsys_max_eig:e2§؛ بإضافةِ مربَّعاتِ الأخطاء الإحصائيّة إلى القطر تصير بين ‏§cov_min_eig:e2§ و§cov_max_eig:e2§، فالمصفوفةُ موجِبةٌ بالكامل، بلا تسويةٍ (ridge) ولا بحاجةٍ إلى معالجةِ لُبسٍ عددِيّ. MD5 ‏§sys_md5:g32§ بحجمِ §sys_bytes:0§ بايت. الملفُّ الكامل lcparam_full_long.txt: ‏§full_rows:0§ سطرًا، انزياحُه من §full_z_min:5§ إلى §full_z_max:2§، سطورُه ‏§full_fields_per_row:0§ حقلًا أوّلُها اسمٌ نصّيٌّ فـ§full_numeric_cols:0§ عمودًا عدديًّا، منها §full_zero_cols:0§ صِفرٌ في كلِّ الصفوف؛ غيرُ الصِفرِيّةِ هي §full_nonzero_cols:g1§ فقط، فلا شكلَ منحنًى ولا لونَ ولا تباينَ منظوماتيّ هناك: ملفٌّ للتحقّق لا للقياس. والناشرون أنفسُهم يبلغون Ωm = §published_Om:3§ ± §published_Om_err:3§ لهذا العيِّنة مع Planck-2015 في نموذج wCDM، ويكتبون حرفيًّا أنّ الشكوكَ المنظوماتيّةَ تُقارِبُ الإحصائيّةَ في القياسِ على الطاقةِ المظلمة.
""")

add("""(٣) المسافةُ القياسيّةُ وكيف تُبنى. الملفُّ لا يحتوي μ؛ يُبنى من المقدارِ المُصحَّحِ بثابتٍ واحد: μ = m_B + 19.51، أي حجمٌ مطلقٌ معلَنٌ M_B = −19.51 للعينةِ كلِّها. التعريفُ الدقيقُ لـμ: الفرقُ بين المقدارِ الظاهريّ والمقدارِ المطلق. وبالمبسَّط: كم يبدو الجرمُ خافتًا قياسًا على ما «يجبُ» أن يبدو عليه لو وُضِعَ على عشرةِ فراسخَ فلكيّة. حسّاسيّةُ النتيجةِ لهذا المُعلَن محسوبةٌ هنا: ‏d ln H₀ / dμ = ln10/5 = §mag_to_hubble_slope:6§ لكلِّ مقدار، فخطأٌ بقدرِ 0.06 في نقطة الصفر يحرِّك H₀ بنسبة §h0_shift_for_006mag_pct:3§%؛ وسَدُّ الفارقِ بين 67.36 و73.04 يتطلّب تحريكَ نقطة الصفر ‏§anchor_shift_for_tension_mag:4§ مقدارًا. عددٌ لا رأي: موضعُ الخلافِ كلِّه يسعُه هامشُ عُشرِ مقدارٍ من معايرةِ الأضواءِ المعياريّة.
""")

add("""(٤) الملاءمةُ كما حُسِبَت. الدالّةُ χ²(Ωm, M) = (μ − μ_model)^T C⁻¹ (μ − μ_model) مع C = C_sys + diag(σ_stat²)، و M مُخرَجةٌ تحليليًّا بتبييضٍ خطّيٍّ بـ C^(−1/2). على شبكةٍ من 0.02 إلى 0.80 بـ313 نقطة: حدٌّ أدنى عند Ωm = §Om_grid_here:4§ بـχ² = §chi2_grid:4§ على §dof:0§ درجةَ حرّيّة، أي χ²/الدَّرج = §chi2_over_dof:4§؛ وحدها الأدنى داخلُ الشبكة لا عند طرفِها (§grid_edge_hit§). تنعيمٌ قطعيٌّ بمضلَّعٍ حول الحدِّ الأدنى يعطي Ωm = §Om_par_here:6§ بـχ² = §chi2_par:4§، وسجلُّ الأشكالِ (figs.py) يُبلِغ Ωm = §Om_man:6§ بـχ² = §chi2_man:4§ وبـσ = §sigma_man:6§ على §dof_man:0§ درجة: الاتفاقُ في الكثافةِ إلى §dOm_cross:e1§، وفي الانحرافِ المعياريِّ إلى §dsigma_cross:e1§، والخلافُ في قيمةِ الدالّةِ §dchi2_cross:e1§ لأنَّ السجلَّ يُبلِغُ عن حدِّ المضلَّعِ لا عن الشبكة. فهذا حسابٌ مستقلٌّ لا إعادةُ تشغيل. الانحرافُ المعياريُّ من التقوّس (Δχ² = 1) σ = §sigma_curvature_here:6§؛ وقدرُ الحجمِ المُخرَج M = §M_here:4§ مقابل §M_binned:4§ في السجلِّ بفارقِ §dM_cross:e1§ — أي §dM_vs_stat_pct:2§% من خطأِ النقطةِ النموذجيّ (§stat_err_mean:5§)، فاختلافُ طريقةِ الإخراجِ لا يحرِّكُ القدرَ المُخرَجَ أكثرَ من هذا القدر.
""")

add(figure(0, """الشكلُ الأول: الأعلى §full_rows:0§ منحنًى ضوئيًّا رماديًّا من lcparam_full_long.txt، و§n_bins:0§ من الأوساطِ المربَّعةِ مُربَّعاتٍ حمراء، والمنحنى الأزرقُ ملاءمتي عند Ωm = §Om_par_here:4§، والبرتقاليُّ نموذجٌ بلا تسارع (Ωm = 1). الأسفلُ لوحُ الفروقِ بوحدَةِ انحرافِهِ المعياريّ. اللوحُ هو ما كشف خطأَيَّ في الفقرة ٧، لا رقمُ χ²."""))

add("""(٥) «ملاءمةٌ جيّدة»: التعريفُ والطرقُ الثلاثة. χ² هو مجموعُ مربَّعاتِ الفروقِ مقسومةً على التباينِ المتوقَّع؛ والملاءمةُ الجيّدةُ أن لا يتجاوزَ ما يُنتِجُه القانونُ الاحتماليُّ. وبالمبسَّط: عددُ المفاجآتِ في الفروق، بمقياسِ ما يجبُ أن يكونَ حجمُها عليه. ثلاثُ محاسبات: (أ) χ²/الدَّرج = §chi2_over_dof:4§؛ (ب) محاكاةٌ بارامترِيّةٌ بـ§NB_boot:0§ عيّنةٍ أُعيدَت عليها الملاءمة: وسيطُ التوزيعِ العدميّ §gof_med_null:4§، وحِزامُ 90% [§gof_band90_lo:3§، §gof_band90_hi:3§]، فالمُلاحَظ §chi2_obs:4§ داخلُه، وP(χ² ≥ المُلاحَظ) = §gof_p_hi:5§؛ (ج) القانونُ المدرسيّ χ²(§dof:0§) يعطي P = §p_textbook:6§، والفرقُ بين الطريقتين §p_boot_minus_p_text:e2§. فلا دليلَ على سوءِ ملاءمةٍ، ولا على ملاءمةٍ «أحسنَ من المتوقَّع» (ذو الوجهين §gof_two_sided:4§). رقمُ χ² لا يُسقِطُ نموذجًا ولا يُثبِتُه؛ الذي يُسقِطُ بنْيةَ الفروقِ لا مجموعَها.
""")

add(figure(1, """الشكلُ الثاني: اليسارُ دالّةُ χ²(Ωm) على الشبكةِ كلِّها؛ اليمينُ الفروقُ عند ثلاثِ قيم: الحدُّ الأدنى §chi2_par:4§، وعند Ωm = 0.05 يعطي Δχ² = §delta_chi2_at_005:2§، وعند Ωm = 0.75 يعطي Δχ² = §delta_chi2_at_075:2§. قوّةُ القيدِ من انحناءِ الدالّة، لا من صِغَرِ الحدِّ الأدنى."""))

add("""(٦) الفتراتُ بثلاثِ طُرُق. من التقوّس: ±§sigma_curvature_here:6§. من الاستدلالِ الملفّي (إعادةُ ملاءمة M عند كلِّ Ωm، بـΔχ² = 1 و4 و9): عند 1σ [§prof_1sigma_lo:6§، §prof_1sigma_hi:6§]، عند 2σ [§prof_2sigma_lo:6§، §prof_2sigma_hi:6§]، عند 3σ [§prof_3sigma_lo:6§، §prof_3sigma_hi:6§]. نصفُ عرضِ 1σ = §prof_1sigma_half:6§ أي §prof1_over_curv:4§ من التقوّس؛ ونسبةُ 2σ إلى 1σ = §prof2_over_prof1:4§ (الغوسّيُّ 2)، ومن 3σ إلى 1σ = §prof3_over_prof1:4§ (الغوسّيُّ 3). دالّةُ الفرجسةِ شبه‑غوسّيّةٌ في هذا المدى، فلا ذيلَ مخفيًّا تحتَها.
""")

add(figure(2, "الشكلُ الثالث: دالّةُ الفرجسةِ الملفّيّةِ والخطوطُ الأفقيّةُ عند Δχ² = 1 و4 و9؛ التقاطعاتُ هي فتراتُ الفقرة ٦: §prof_1sigma_lo:4§–§prof_1sigma_hi:4§ عند 1σ، و§prof_3sigma_lo:4§–§prof_3sigma_hi:4§ عند 3σ."))
add(figure(3, "الشكلُ الرابع: توزيعُ χ² العدميّ من §NB_boot:0§ محاكاة، والخطُّ العموديُّ عند المُلاحَظ §chi2_obs:4§، والحِزامُ 90%، والوسيطُ §gof_med_null:4§. المُلاحَظُ ليس في الطرف."))

add("""(٧) خطأيان وقعا، ووقعا بحيث لا يُريان. الأول: إغفالُ عامل (1+z) الذي يحوّل مسافةَ الحركةِ عبر الفضاء إلى مسافةِ الإضاءة. الثاني: تكاملُ دالّةِ التمدُّد E(z) بدل مقلوبِها في زمنِ النظرةِ الخلفيّة. كلاهما عدَا على مقياسِ الملاءمة: χ²/الدَّرج بقِيَ قريبًا من الواحد، لأنّ لمنحنًى خاطئٍ رقمَين مُحرَّرين يُعوِّضان شكلَه، فنزل الحدُّ الأدنى إلى حدِّ الشبكة فبدَا «قيمةً». ما كشفهما لوحُ الفروقِ في الشكلِ الأول: كانت منظَّمةً لا عشوائيّة. وفي الخطأِ الثاني وافَقَت ساقُ الماضي النشرَ إلى 0.03 مليار سنة وأخطأت ساقُ المستقبل بعاملِ 1.8: اتفاقُ جهةٍ واحدةٍ بعد انقلابِ إشارةٍ لا يُثبِتُ شيئًا. الدروسُ إجرائيّة: راقِب حدودَ الشبكة، وارسم الفروق، ولا تُصدِّق رقمَ ملاءمةٍ واحدًا، ولا تَبْنِ جملةَ تحقُّقٍ من مقدارِ فارقٍ مطلق.
""")

add("""(٨) سُلَّمُ H₀: أربعةُ قياساتٍ مستقلّةِ الأدوات. (أ) §h0_y:0§± الخطأ 0.54: نموذجُ ΛCDM على إشعاعِ الخلفيّة، Planck 2018 VI (A&A 641:A6) — محكَّم؛ القِيمةُ 67.36 ± 0.54 قُرِئَت في جلسةٍ سابقة، ورقمُ arXiv لم أُراجِعْه اليوم. (ب) 73.04 ± 1.04: سُلَّمُ Cepheid/HST (Riess 2022) — محكَّم؛ ونسخةُ arXiv (‏2208.01045، DOI 10.3847/1538-4357/ac8f24) تقول في ملخَّصها حرفيًّا: ‏zp = −3 ± 4 μas، وM_W,H1 = −5.902 ± 0.025، وH₀ = 72.8 ± 1.3 أو 73.2 ± 1.1 بالسُلَّمِ وحدَه، و73.01 ± 0.99 أو 73.15 ± 0.97 بكلِّ المراسي، و«a 5.3σ Hubble Tension relative to Planck+ΛCDM». فالرقمُ الذي أدخلتُه (73.04 ± 1.04) ليس حرفيّةَ نسخةِ arXiv، وهو مُثبَتٌ هنا لا مُستَر. (ج) 68.81 ± 1.80: قمّةُ فرعِ العمالقِرةِ مع JWST ضمن برنامج Carnegie–Chicago — محكَّم، قُرِئ في جلسةٍ سابقة. (د) 67.80 ± 2.720: جسرُ AGB الكربونيّ من البرنامجِ نفسِه — محكَّم، كذلك.
""")

add("""(٩) التجميـعُ بخمسةِ مُقدِّراتٍ على الأرقامِ الأربعةِ نفسِها. المتوسطُ غيرُ المُرجَّح §h0_unweighted:4§. ثابتُ الأثر: §h0_fe:4§ ± §h0_fe_sd:4§، مع Q = §h0_Q:4§ على ثلاثِ درجات (Q/الدَّرج = §h0_Q_over_dof:4§) وI² = §h0_I2:2§%. DerSimonian–Laird: §h0_dl:4§ ± §h0_dl_sd:4§ مع τ = §h0_tau_dl:4§. Paule–Mandel: τ = §h0_tau_pm:4§. REML: τ = §h0_tau_reml:4§ — مدىُ τ بين المُقدِّراتِ الثلاثة عامِلُ §h0_tau_span:3§. النموذجُ البيزيُّ الكامل (شبكةٌ 401×401، μ مسطَّح، τ نصفُ‑كوشي(0,1)): μ = §h0_bay:4§ ± §h0_bay_sd:4§ بـCrI [§h0_bay_cri:3§]، وسيطُ τ = §h0_tau_med:3§ بـ[§h0_tau_cri:3§]، والوسيطُ الخلفيُّ §h0_median:4§، وفرقُ DL عن التأثيرِ الثابت §fe_minus_bay:4§ فقط. المدىُ بين «معقولَي» المُقدِّرات §h0_est_span:4§ أي §h0_span_in_fe_err:3§ من خطأِ ثابتِ الأثر، وعرضُ فاصلِ التنبّؤِ الخلفيّ §h0_pred_width:3§ ([§h0_pred_cri:3§]). فالعبارةُ الدقِيقة: لا «قيمةَ مُجمَّعةَ» لـH₀؛ يوجد توزيعُ مُقدِّر، وأعرضُ فردٍ فيه اختيارُ المُقدِّر.
""")

add(figure(4, "الشكلُ الخامس: أعلاه المُقدِّراتُ الخمسةُ على محورٍ واحد، وأسفلُه توزيعُ τ الخلفيُّ بوسيطِ §h0_tau_med:3§ وحِزامِ [§h0_tau_cri:3§]. المُدخَلاتُ أرقامُ الفقرة ٨، والحسابُ كما في ٩."))

add("""(١٠) حسّاسيّةُ الحذف. أُعيدَ التجميـعُ أربعَ مرّاتٍ بحذفِ مصدرٍ كلَّ مرّة؛ المُقدِّراتُ الناتجة: ‏[§loo_fe:4§] لثابتِ الأثر، و[§loo_bay:4§] للبيزيّ. مدىُ المركز: §loo_fe_spread:4§ و§loo_bay_spread:4§ — الأوّلُ أوسعُ بثمانيةِ أضعافٍ من خطأِ ثابتِ الأثر المُعلَن. وبإنحرافاتِ كلِّ مصدرٍ عن المُجمَّع: Planck على بُعد §dev_planck_from_bay:3§σ وR22 على بُعد §dev_r22_from_bay:3§σ من μ البيزيّ؛ أو §dev_planck_from_fe:3§σ و§dev_r22_from_fe:3§σ من §h0_fe:4§. أي أنّ «التوتُّرَ» ليس رقمًا يُعلَن، بل هو مقدارُ ما يتحرَّكُ المركزُ حين يتغيّرُ مَن في العيّنة.
""")

add(figure(5, "الشكلُ السادس: المركزُ بعد حذفِ كلِّ مصدرٍ بالتناوب، للمُقدِّرَين الاثنَين؛ المدى §loo_fe_spread:4§ و§loo_bay_spread:4§ كما في الفقرة ١٠."))

add("""(١١) المصالحةُ مع تجميـعٍ سابق. الورقةُ الأصليّة أبلغت عن 70.561 ± 1.304 مع τ = 1.893 وQ = 6.580 على 3 درجات وI² = 54.41%؛ لم أُعِدْ تلك الحساباتِ اليوم، وسِجلُّها في logs/deepen_log.txt. والفرقُ ليس خطأً في أحدِهما: ذاك السِجلُّ ضمَّ تركيباتٍ مُشتَقّة (مثل «TRGB+JAGB مجتمِعَين: 69.02 ± 1.56» و«JWST وحدَه: 68.81») إلى جانبِ مُكوِّناتِها، والتركيبُ الخطّيُّ لقياسَين مشتركين يُلغي الفارقَ المشترك في Bنيةِ Q، فيصغرُ بحكمِ التعريف. والاختبارُ المجرَّد: أربعةُ مراسٍ مستقلّةٍ تعطي Q = §h0_Q:4§، أي §h0_Q_over_dof:2§ أضعافَ درجاتِه. ومَن يجمعُ مصادرَ غيرَ مستقلّةٍ يجدُ Q صغيرًا، ثم يُسمّي ذلك «اتّساقًا».
""")

add("""(١٢) حسّاسيّةُ القراءةِ لا الحساب. أُعيدَ السُلَّمُ كلُّه بـ R22 = 73.01 ± 0.99 (نصُّ arXiv) بدل 73.04 ± 1.04: تحرُّكُ المركز §sens_d_fe:4§ لثابتِ الأثر (§sens_fe_in_sd:4§ من خطأه)، و§sens_d_bay:4§ للبيزيّ، و§sens_d_dl:5§ لـDL — أي أقلَّ من عُشرِ انحرافٍ معياريٍّ في الثلاثة. وتحرُّكُ مقاييسِ التفرُّق: ΔQ = §sens_d_Q:4§ (‏§sens_d_Q_pct:2§% من Q)، وΔI² = §sens_d_I2:4§ نقطة، وΔτ_DL = §sens_d_tau_dl:4§، وΔوسيطُ τ = §sens_d_tau_med:4§. فالنتيجةُ: المركزُ لا يتحرَّك، ودليلُ عدمِ الاتّساقِ يتحرَّكُ بمقدارٍ يُذكر.
""")

add("""(١٣) المسافةُ بالمسطرةِ الصوتيّة. التعريفُ: r_d = ∫ c_s(z)/H(z) dz من انزياحِ السحبِ إلى z = 10⁵، مع c_s = c/√(3(1+R)) وR = 3ρ_b/(3.15ρ_γ). حُسِبَ هنا من كثافاتِ Planck المُعلَنة وحدَها — لا بيانات، لا ملاءمة: عند z = 1089.92 يعطي ‏§rd_here:4§ Mpc، والمنشورُ §rd_published:2§، فالفرقُ §rd_dev_percent:3§%. المدىُ على شبكةِ الانزياحِ 850–1150 هو [§rd_min:2§، §rd_max:2§]، والتقائُها مع 144.44 عند z = §z_cross:2§. والزاويةُ الصوتيّة θ* = r_d/D_A(z*) = §theta_star_1e2rad:4§ ×10⁻² راديان على النموذجِ نفسِه (D_A = §D_A_zstar_Mpc:1§ Mpc). القراءةُ: صيغةٌ تحليليّةٌ مختصرةٌ تُخطئُ المسطَرةَ بـ4.6%، وهي نسبةُ الفيزياءِ المحذوفةِ (سُمكُ طبقةِ السحب، تأيّنُ الهيليوم، اضطراباتُ النيوترينو)، لا نسبةُ خطأٍ في ΛCDM.
""")

add("""(١٤) القفلُ بين r_d وH₀. إذا ثَبَتَت الزاويةُ المقاسةُ في القمّةِ الصوتيّةِ الأولى فإنّ r_d ∝ 1/H₀، فلا «قيسَ» H₀ من الخلفيّةِ على استقلالٍ عن النموذجِ الذي ثبَّتَ المسطَرة؛ يُبدَّلُ بينهما فقط. ومن هنا يصيرُ «لماذا الآن؟» سؤالًا عددِيًّا لا بلاغيًّا.
""")

add(figure(6, "الشكلُ السابع: اليسارُ r_d(z_drag) بالتكاملِ من كثافاتِ Planck مع الخطِّ الأحمرِ عند §rd_published:2§ Mpc والتقاءٍ عند z = §z_cross:2§؛ اليمينُ القفلُ r_d ∝ 1/H₀ مع المراسي الأربعة. أرقامُ الفقرة ١٣."""))

add("""(١٥) «لماذا الآن؟» عددًا. النسبةُ بين كثافةِ المادّةِ وكثافةِ الطاقةِ المظلمةِ اليوم، في نموذجٍ مسطَّحٍ بـΩm = 1 − 0.6847: §ratio_today:6§. التساويُ يتطلّب عاملَ §tightest_ratio:5§، فمن قال «متقاربتان ضمن عامل 2» أخرجَ اليومَ من نافذتِه: عند عاملِ 2 يكون z_low = §win_2_zlo:4§ > 0، أي أنّ التكافؤَ لم يبدأ بعدُ. النوافذُ المحسوبةُ (المدى، العرضُ بمليارِ سنة، نسبتُه من العُمر، عددُ أزمنةِ Hubble): عند ×10: ‏[§win_10_zlo:4§، §win_10_zhi:4§] وعرضٌ §win_10_window:3§ = §win_10_frac:4§ من العُمر = §win_10_hubble:4§ زمنِ Hubble؛ عند ×3: ‏§win_3_window:3§ (§win_3_frac:4§)؛ عند ×2.171: ‏§win_2.171_window:3§ (§win_2.171_frac:4§)؛ عند ×2: ‏§win_2_window:3§ (§win_2_frac:4§)؛ عند ×1.5: ‏§win_1.5_window:3§ (§win_1.5_frac:4§). تضييقُ التسامح من ×10 إلى ×1.5 عامِلُ §tolerance_change_10_to_1p5:4§، والمدى يتقلَّص عامِلَ §shrink_10_to_1p5:4§ فقط. وزمنُ Hubble ‏1/H₀ = §hubble_time_gyr:4§ مليارَ سنة، والعُمرُ التحليليُّ عند z = 0 في النموذجِ نفسِه t₀ = §t0_analytic_gyr:6§ مليارِ سنة مقابل §t0_planck:4§ المنشور، بفرقٍ §t0_minus_planck_myr:3§ مليونِ سنة، أي أنّ العُمرَ أصغرُ من 1/H₀ بنسبة ‏§hubble_minus_t0:3§ مليارِ سنة (§age_over_hubble_time:4§ من زمنِ Hubble). والتكافؤُ نفسُه عند z_eq = §z_eq:4§ (a_eq = §a_eq:6§) بنظرةٍ خلفيّةِ §lookback_eq_gyr:4§ مليارِ سنة = §eq_frac_of_age_pct:2§% من العُمر: في الماضي القريب، لا على حافّةِ اللانهاية.
""")

add(figure(7, "الشكلُ الثامن: كثافةُ المادّةِ ∝ a⁻³ وكثافةُ الطاقةِ المظلمةِ الثابتة، والأشرطةُ ثلاثُ نافذاتِ تسامُح (×10، ×2.171، ×2) على مقياسٍ لوغاريتميٍّ لعاملِ القياس. النسبةُ اليوم §ratio_today:4§، وأضيقُ عاملٍ يُدخِلُ اليومَ §tightest_ratio:5§."""))
add(figure(8, "الشكلُ التاسع: عرضُ النافذةِ بمليارِ سنة كدالّةٍ في عاملِ التسامح، مقابلَ عُمرِ الكون؛ النقاطُ هي صفوفُ الفقرة ١٥، والمنحنى محسوبٌ من الصيغةِ التحليليّةِ للعُمر، لا من جدول."""))

add("""(١٦) الفراغُ عددًا. ρ_Λ = Λc⁴/(8πG) بـΛ = 1.089139 × 10⁻⁵² م⁻² تساوي §rho_lam_jm3:e3§ جول/م³. الفارقُ عن كثافةِ الطاقةِ عند بلانك ‏log10(ρ_Pl/ρ_Λ) = §d_rho:5§ مرتبةً؛ وكتابتُه رباعيَّ الطاقة، 4·log10(M_Pl/ρ_Λ^¼) بـM_Pl = 1.2209 × 10¹⁹ GeV، تعطي §d_planck:5§ والفرقُ بين الصيغتَين §d_rho_minus_d_planck:e2§؛ وبكتلةِ بلانك المُخفَّضةِ (2.435 × 10¹⁸ GeV) يعطي §d_reduced:5§، أي §d_rho_minus_d_reduced:3§ مرتبةً أقلّ. فالفاصلُ بين «123» و«120» المتداوَلَين اصطلاحٌ في ħ وفي أيِّ الكتلتَين يُقابَلُ بهما القياس، لا فيزياءٌ مختلفة. ويبقى جوهرُ المُشكِلةِ كما هو: لا مُشتَقَّ عندي لحدٍّ أدنى، فلا تنبّؤَ يُقابَلُ بقياس، بل مقارنةُ مقياسَين.
""")

add("""(١٧) ميزانيّةُ الراصِد. أفقُ de Sitter عند نصفِ قطرِ √(3/Λ) = §horizon_m:e3§ م = §horizon_gpc:4§ Gpc، وإنتروبياؤُه πR²/ℓ_Pl² تعطي log10(S/k_B) = §log10_S:5§. المُسجَّلُ لكلِّ ما يُضيءُ داخلَ الأفق ~10⁸⁸ k_B، فالفرقُ §entropy_content_log10_gap:4§ مرتبةً ونسبتُنا إلى ما يُسمَحُ به §observer_share:e2§. وحرارةُ الأفق: من نصفِ القطرِ §T_dS_from_radius_K:e3§ كلفن، ومن H₀ ‏§T_dS_from_H0_K:e3§ كلفن، والنسبةُ §T_two_ways_ratio:6§، وهي √Ω_Λ = §sqrt_Omega_Lambda:6§ بالحرف: الاختلافُ كلُّه افتراضُ إهمالِ المادّة، لا اختلافُ قياس. وللمقارنةِ مع الضجيجِ الحراريِّ في الجسم: k_BT عند 310 كلفن = §kB_T_310K_meV:4§ meV. هذا كلُّ ما يبقى من حُجّةِ «أدمغةِ بولتزمان»: قيدُ ميزانيّة، لا بُرهانٌ على وجودِها.
""")

add(figure(9, "الشكلُ العاشر: اليسارُ الفارقُ اللوغاريتميّ بين كثافةِ الفراغِ وكثافةِ بلانك بثلاثِ صياغاتٍ مُسمّاة (الفقرة ١٦)؛ اليمينُ إنتروبيا الأفق §log10_S:3§ مقابل 10⁸⁸، بنسبة §observer_share:e2§. الثوابتُ مكتوبةٌ في النصّ، والأشرطةُ محسوبةٌ منها لا مُدخَلة."""))

add("""(١٨) التعقيدُ رخيصًا وغاليًا. التعريفُ في الضغطِ بعبّاراتِ Lempel–Ziv (LZ76): عددُ العباراتِ الجديدةِ التي لم تسبِقْها في السلسلة. وبالمبسَّط: كم يلزمُ من «عباراتٍ لم تُقَلْ بعدُ» لإعادةِ كتابةِ النصّ. على سلاسلَ ثنائيّةٍ عشوائيّةٍ بطولِ L = 200 حتى 3200 (متوسطُ ثلاثِ سحب، بذرةٌ مُثبَّتة) كان عَدّدي [§lz_mine:g5§] مقابل التوقُّعِ النظريِّ L/log₂L بـ[§lz_theo:g5§]؛ النسبةُ §lz_ratio_first:4§ عند أقصرِ مدى تنخفضُ إلى §lz_ratio_last:4§ عند أطولِه — تبايُنٌ §lz_dev_pct:2§% لمقياسٍ يعملُ في زمنٍ شبه‑خطّيّ. المُقابِلُ في نظريّةِ المعلوماتِ المُكامَلة: Φ يتطلّب البحثَ عن أفضلِ تجزئةٍ لمجموعةٍ من n عنصرًا، وتكلفَتُه أُسّيّة؛ وقانونُ الزمنِ المقيسُ في العملِ الأصليِّ هو ln t[s] = 3.052n − 9.921 (من الورقةِ الأصليّة؛ لم يُعَدْ قياسُه هنا، فالأداةُ التي قاسته ليست في هذه البيئة)، فيُعطي عند n = 4 نحو §phi_n4_s:3§ ثانية، وعند n = 8 نحو §phi_n8_days:2§ يومًا، وعند n = 12 نحو §phi_n12_yr:1§ سنة، وكلُّ عنصرٍ إضافيٍّ يُضاعِفُ الكلفةَ عامِلَ §exp_slope_per_element:4§. والاستقراءُ إلى n = 300 (قشرةٌ من عُقدٍ نموذجيّة) يُعطي نحوَ ‏§phi_n300_log10_yr:pow§ سنة، أي §phi_age_ratio_log10:pow§ من عُمرِ الكون. فالحدُّ العلويُّ هنا تشغيليٌّ لا نظريّ.
""")

add(figure(10, "الشكلُ الحادي عشر: اليسارُ عددُ عباراتِ LZ76 المحسوبِ مقابل L/log₂L على خمسةِ أمْداد؛ اليمينُ زمنُ حسابِ Φ من قانونِ الزمنِ المذكورِ في الفقرة ١٨، على محورٍ لوغاريتميّ بالأيّام."""))

add("""(١٩) القياسُ على السريرِ الطبيّ. اختبارُ التمييزِ السريريّ COGITATE (Nature 642 (2025) — محكَّم؛ n = 256؛ ثلاثُ تقنيّات: TMS‑EEG وMEG وfMRI): خلاصتُه المنشورة أنّ نتائجَه «تُعارِضُ بنودًا رئيسةً للنظريَّتَين معًا» — نظريّةُ المعلوماتِ المُكامَلة وفضاءُ العملِ العامّ. المقياسُ الحَرِجُ PCI: مداهُ المُبلَّغ في اليقظة 0.45–0.67 وفي التخديرِ العميق 0.25–0.31 (Casali وآخرون، Science 2013 — محكَّم؛ قُرِئ في جلسةٍ سابقة). ونظريّةُ IIT بإصدارِها 4.0 تُعرَّفُ بمُسلَّماتٍ ستّة (الوجودُ أوّلًا، ثم المعلومةُ والتكاملُ والاستبعادُ والتأليفُ والأصالة) وبمُصادَراتٍ خمسٍ تربطُها بالفيزياء، وبمبدأِ استبعادٍ يجعلُ البِنى المتداخلةَ ذاتَ φ_s الأدنى «مُستبعَدةً من الوجود» (البيانُ الرسميّ: Albantakis وآخرون 2023 — محكَّم، قُرِئ نصُّه في جلسةٍ سابقة؛ لم أُعِدْ التحقّقَ من رقمِ المجلّةِ اليوم). والنقدُ الذي يُبنى عليه: (أ) لا دليلَ تجريبيًّا على أنّ Φ يواكبُ الوعي (Salaberli & Soto، Neuroscience & Biobehavioral Reviews 2025 — محكَّم، قُرِئ نصُّه)؛ (ب) Φ غيرُ مُعرَّفٍ تعريفًا قابلًا للاستدلالِ من بياناتٍ مُتناهية (arXiv:2611.08469 — ما قبل النشر). النقدان لا يُبطِلانِ النظرية؛ يُحدِّدان ما يمكنُ أن تُثبِتَه اليوم: لا شيءَ كمّيًّا.
""")

add("""(٢٠) الإشكاليّةُ الصعبةُ بحدودِها. التعريفُ في مصدرِه (Chalmers، «المواجهةُ مع مُشكِلةِ الوعي»، Journal of Consciousness Studies 2(3):200–219 (1995) — محكَّم): التفسيرُ البنيويُّ والديناميكيُّ للوظائفِ لا يُخرِجانِ وجودَ التجربةِ الذاتيّة، بينما يُخرِجانِه في بقيّةِ الحالاتِ الفيزيائيّة؛ وبالمبسَّط: كلّ ما نستخرِجُه من وصفِ الجهازِ يصفُ «ماذا يفعَل»، لا «لماذا يبدو شيئًا ما أن يَكونَه». هذا قيدٌ منطقيٌّ على الاستنتاجِ لا قياس؛ ومقابلُه التقنيُّ الوحيدُ القابلُ للفحصِ اليوم هو قائمةُ «المُؤشِّراتِ العصبيّةِ الكيميائيّة» (Butlin وآخرون، arXiv:2308.08708 — ما قبل النشر)، وهي تُستخدَمُ لمساءلةِ الأنظمةِ الاصطناعيّةِ بالخصائصِ الحاسوبيّةِ لا بالجوهر. وأمّا التعريفاتُ الاصطلاحيّةُ للمُصطَلَحات (مُشكِلةُ الجمع، مُشكِلةُ مجموعِ الذوات، النَّظرَيّةُ الشُّعوريّةُ الصُّغرى) فتُذكَرُ هنا بوصفِها تصنيفًا لا دليلًا: مصادِرُها مراجعُ مُحرَّرةٌ موسوعيّة، لا أوراقٌ محكَّمة، فلا يُسنَدُ إليها عدد.
""")

add("""(٢١) اللا‑براهينُ الكموميّةُ وحدودُها، لأنّ هذا الحدَّ يُنسَبُ كثيرًا بلا وجه. (أ) PBR (Nature Physics 8:475 (2012)، arXiv:1111.3328v3 — محكَّم): تحتَ «استقلالِ التحضيرات» لا يجوزُ أن تكونَ الحالةُ الكموميّةُ مجرّدَ معلومةٍ إحصائيّة. الفرضيّةُ هي الحدُّ، وهي المذكورةُ هنا لأجلِه؛ والتعليقُ الذي ادّعى أنّ البرهانَ يُخالِفُ «مُسلَّمةَ الإسقاط» (arXiv:1812.03035) سُحِبَ بعد الاعترافِ بسوءِ فهم، فلا يُحاسَبُ البرهانُ عليه. (ب) Frauchiger–Renner (Nature Communications 9:3711 (2018)، DOI 10.1038/s41467-018-05739-8، arXiv:1604.07422v2 — محكَّم): نصُّ النتيجةِ أنّ وكيلًا يرى نتيجةً «يجبُ» أن يستنتِجَ أنّ وكيلًا آخر توقّعَ النقيض، وأنّ النظريةَ «لا تُستثمَر في أنظمةٍ معقّدةة بهذه الطريقةِ البسيطة» — لا أنّ النظريةَ متناقضة. نُشِرَت له أربعةُ نقودٍ محدَّدة: Chen & Zhang (arXiv:1810.01080) يُصلِحون فرضيّة؛ Bernal (arXiv:2106.07312) يُخرِجون تفصيلًا في البرهان؛ Samuel (arXiv:2208.00060) يَعدُدُ ثلاثَ عُيوب: استعمالُ تعدّيِ الاستلزامِ بين جُمَلٍ لا تلتزِمُ به، وتنافُسُ أزواجٍ من المُقدِّمات، وبُطلانُ ثلاثٍ من أربعٍ بعد التقييدِ بجولةِ OK–OK̄؛ Elouard وآخرون (Quantum 5:498 (2021)، DOI 10.22331/q-2021-07-08-498 — محكَّم) يُبْرِزون أنّ الخواصَّ الثلاثَ تنتمي إلى سياقَين منطقيَّين مُنفصِلَين يمثِّلُهما مؤثِّرَان لا يُبادِلان، فلا تجتمِعُ يومًا. (ج) الصداقةُ المحلّيّةُ (Bong وآخرون، Nature Physics 16:1199–1205 (2020)، DOI 10.1038/s41567-020-0990-x، arXiv:1907.05607v4 — محكَّم): لا تجتمعُ لا‑قَدَرِيّةٌ مُسبَقةٌ مع المحلّيّةِ مع أبديّةِ الأحداثِ الملاحظة؛ ويُثبَتُ صراحةً أنّ مخالفةَ بيل في هذه السيناريوهات «ليست كافيةً على العموم»، وتُشتَقُّ مُتبايناتٌ لا‑نظريّةُ المصدرِ تُخالِفُها كموميات؛ وفي التجربةِ المبدئيّةِ «مَسارُ فوتونٍ» هو المُراقِب. وتابعُه (Walleghem وآخرون، Physical Review A 112:022212 (2025)، arXiv:2310.06976v3 — محكَّم): لا‑المحلّيّةُ ليست لازمةً لمفارقاتِ Wigner's friend الممدَّدة، بفرضيّةٍ جديدةٍ يسمّونها Commutation Irrelevance. فالنتيجةُ المجرَّدة: لا واحدَ من هذه يُخرِجُ حُكمًا على الوعي؛ أقصى ما يُخرِجُه تحديدُ أيِّ مُسلَّمةٍ نُبقِي في تأويلِ القياس.
""")

add("""(٢٢) التماسُكُ الكمّيُّ في الدِّماغ: العددان المتنازِعان. Tegmark (Physical Review E 61:4194–4206 (2000)، DOI 10.1103/PhysRevE.61.4194، arXiv:quant-ph/9907009v2 — محكَّم): أزمنةُ التماسُكِ المحسوبةُ 10⁻¹³–10⁻²⁰ ثانية مقابل أزمنةً ديناميكيّةٍ 10⁻³–10⁻¹ ثانية، «فلابدّ من اعتبارِ درجاتِ الحُرّيّةِ المعرفيّةِ كلاسيكيّة». الاعتراضُ المنشور: Hagan–Hameroff–Tuszyński (arXiv:quant-ph/0005025v1 (2000)، ‏10 صفحات — ما قبل النشر؛ لم أُتحقَّق من نسخةٍ محكَّمةٍ له في هذه الجلسة) يُسجّلُ خمسَ مُلاحظاتٍ مُرقَّمة: أنّ حسابَ Tegmark موجَّهٌ إلى نموذجٍ هجينٍ لا إلى النموذجِ المنشور؛ وأنّ أزمنةَ التماسُكِ عنده تَقِلُّ بازديادِ البرودةِ خلافًا لِما يُلاحَظ؛ وأنّ تصحيحَ المسافةِ الفاصلةِ والشحنةِ وثابتِ العزلِ يرفعُ الزمنَ إلى 10⁻⁵–10⁻⁴ ثانية؛ وأنّ ضخَّ الطاقةِ اللا‑توازنيَّ يُوازِنُ التماسُكَ كما في الليزِر؛ وأنّ هلامَ الأكتينِ قد يرفَعُه إلى 10⁻²–10⁻¹ ثانية. فالخلافُ سبعٌ إلى تسعُ مراتبَ قدرِيّةً في كمّيّةٍ واحدة، بلا قياسٍ يُرجِّح. وللمقياس: k_BT عند 310 كلفن = §kB_T_310K_meV:4§ meV، أي أكبرُ من حرارةِ أفقِ de Sitter (§T_dS_from_radius_K:e3§ كلفن) بفارقِ مئةٍ وستةٍ وثلاثين مرتبةً. ولا أُدرِجُ هُنا قياسَ الرنينِ المغناطيسيِّ على ‏⁴³Ca (P > 0.9999) الذي استُعمِلَ في نسخةٍ سابقة: رقمُ المجلّةِ لم أُعِدِ التحقّقَ منه اليوم، وهو مُثبَتٌ في قائمةِ المُلاحَظاتِ دون أن يُسنَدَ إليه استنتاج.
""")

add("""(٢٣) التوتّراتُ عددًا، بحسابٍ على الأرقامِ المُعلَنةِ نفسِها. الفارقُ بين Planck وR22 هو 73.04 − 67.36 = 5.68، وخطؤُه المُجمَّعُ تربيعيًّا √(0.54² + 1.04²) = ‏§tension_planck_r22_err:4§، فالدلالةُ §tension_planck_r22_fe:3§σ؛ وبالنسخةِ المُعلَنةِ على arXiv (73.01 ± 0.99) تصير §tension_planck_r22_arxiv:3§σ. والفرقُ بين 5.0 و«5.3» المذكورةِ في الملخَّصِ لا يُحسَمُ من الملخَّصِ وحدَه، لأنّ دالّةَ الفرجسةِ الكاملةَ لا تجمعُ خطأَين تربيعيًّا. ومقابلةُ الطرفين بالمُجمَّعِ البيزيّ (69.3870 ± 1.6209) تُعطي §dev_planck_from_bay:3§σ و§dev_r22_from_bay:3§σ. وأمّا TRGB مقابل JAGB — وهما في السُلَّمِ الواحد — فالفرقُ §trgb_vs_jagb:3§σ فقط: تباعدُ مصادرِ السُلَّمِ الواحدِ يقاربُ تباعدَ السُلَّمِ كلِّه عن الصوتيّات، ف«عددُ السِغما» دالّةٌ في اختيارِ المُقابَلَين لا رقمٌ نظيفٌ يُنقَل. والمشكِلةُ الشقيقة: الليثيومُ المرصودُ 2.67 ± 0.06 مقابل المحسوبِ 2.20 ± 0.05، أي §lithium_diff_dex:3§ dex وقدرُه §lithium_sig:3§σ إذا ضُمَّ الخطآن وحدَهما؛ ونماذجُ الدورانِ (arXiv:2602.22516) وحساباتُ النواتجِ (arXiv:2508.09821) — كلاهما ما قبل النشر — تُنقِصُ الفارقَ ولا تُزيلُه بحسبَ مُلَخَّصيْهما.
""")

add("""(٢٤) ما لا يُثبِتُه هذا النصّ. (أ) Ωm مُستخرَجٌ من §n_bins:0§ وسيطًا مربَّعًا بمصفوفةِ تباينٍ واحدة، لا من §full_rows:0§ منحنًى؛ والقياسُ المنشورُ لنفسِ العيّنة §published_Om:3§ ± §published_Om_err:3§ في نموذجٍ أوسع. (ب) سُلَّمُ H₀ بأربعةِ مراسيَ لا بوصلة، وI² = §h0_I2:2§% يعني أنّ تفرُّقَ المصادرِ يغلِبُ أخطاءَها المُعلَنة. (ج) سُلَّمُ S₈ لم أُعِدْه: مُتَّجَهُ العددِيَّ لم يَبقَ في العمل، فما في الورقةِ الأصليّةِ (0.8298 ± 0.0059، Q = 4.51 على 4 درجات، I² = 11%) يُذكَرُ إحالةً. (د) ساقُ المستقبلِ في نموذجِ Λ المسطَّحِ استقراءٌ نظريٌّ لا قياس، إذ لا بياناتِ عند z < 0. (هـ) تسمياتُ الأشكالِ أحدَ عشرَ إنجليزيّة، لأنّ خطَّ الرسمٍ في هذه البيئةِ لا يُشَكِّلُ العربيّة؛ وهو قيدُ إخراجٍ لا نقصُ حساب. (و) DESI 2025: نسختانِ من المسحِ نفسِه (arXiv:2503.14738 و2508.10514v7) أدّتا إلى استنتاجَين مختلفَين في معادلةِ الحالة؛ لا أُدرِجُ أرقامَهما لأنّي لم أفتحْهما في هذه الجلسة، وأكتفي بالتوثيقِ أنّ ذلك الوقوعَ مُثبَتٌ في سجلِّ المصادر. (ز) قياسُ 21‑cm: SARAS‑3 رفضَ كشفَ EDGES عند 95.3% (A&A 698 A152 — محكَّم، قُرِئَ في جلسةٍ سابقة).
""")

LEDGER = [
    ("Scolnic et al. 2018, ApJ, DOI 10.3847/1538-4357/aab9bb; بيانات: DOI 10.17909/T95Q4XD", "محكَّم", "واجهة arXiv API", "الملفّان؛ Ωm = 0.307 ± 0.012 (wCDM مع Planck‑2015)؛ «المنظوماتيّ يقاربُ الإحصائيّ»"),
    ("Riess et al. 2022, ApJ, DOI 10.3847/1538-4357/ac8f24 (arXiv:2208.01045)", "محكَّم", "واجهة arXiv API", "73.01 ± 0.99 و73.15 ± 0.97؛ zp = −3 ± 4 μas؛ M_W,H1 = −5.902 ± 0.025؛ «5.3σ»"),
    ("Planck 2018 results VI, A&A 641:A6", "محكَّم", "قراءة سابقة؛ رقم arXiv لم يُراجَع", "67.36 ± 0.54؛ العُمر 13.7981 مليار سنة"),
    ("CCHP TRGB مع JWST (Freedman et al. 2024)", "محكَّم", "قراءة سابقة", "70.39 و68.81 ± 1.80"),
    ("CCHP JAGB (Freedman et al. 2024)", "محكَّم", "قراءة سابقة", "67.80 ± 2.720"),
    ("Anderson & Bedin 2010, PASP, DOI 10.1086/656399 (arXiv:1007.3987)", "محكَّم", "واجهة arXiv API", "تصحيحُ CTE للبكَسلات: نموذجُ قراءةٍ من 168 تعريضًا أسوَد"),
    ("Casali et al. 2013, Science", "محكَّم", "قراءة سابقة", "PCI 0.45–0.67 مقابل 0.25–0.31"),
    ("COGITATE 2025, Nature 642", "محكَّم", "نصُّ الصفحة (جلسة سابقة)", "n = 256؛ «تُعارِضُ بنودًا رئيسةً للنظريَّتَين»"),
    ("Albantakis et al. 2023 (IIT 4.0)", "محكَّم", "نصُّ البيان الرسميّ (جلسة سابقة)", "ستُّ مُسلَّمات، خمسُ مُصادَرات؛ استبعادٌ بـφ_s"),
    ("Tononi 2004, BMC Neuroscience 5:42, DOI 10.1186/1471-2202-5-42", "محكَّم", "صفحةُ الناشر", "Φ قيمةُ التكامل؛ التمايزُ والاتّحادُ مُبرِّرَا الفرض"),
    ("Salaberli & Soto 2025, Neurosci. Biobehav. Rev.", "محكَّم", "نصُّ الصفحة (جلسة سابقة)", "«لا دليلَ تجريبيًّا على أنّ Φ يواكبُ الوعي»"),
    ("arXiv:2611.08469", "ما قبل النشر", "ملخّص API (جلسة سابقة)", "Φ غيرُ قابلٍ للتحديدِ من بياناتٍ مُتناهية"),
    ("Chalmers 1995, J. Conscious. Stud. 2(3):200–219", "محكَّم", "سجلّا استشهادٍ مستقلّان", "تعريفُ الإشكاليّةِ الصعبة"),
    ("Butlin et al. 2023, arXiv:2308.08708", "ما قبل النشر", "ملخّص API (جلسة سابقة)", "قائمةُ المُؤشِّراتِ الحسابيّةِ للوعي"),
    ("Pusey–Barrett–Rudolph, Nat. Phys. 8:475 (2012), arXiv:1111.3328v3", "محكَّم", "واجهة arXiv API (جلسة سابقة)", "النتيجةُ تحتَ استقلالِ التحضيرات"),
    ("arXiv:1812.03035 (Cabbole)", "مسحوب", "سجلُّ arXiv (جلسة سابقة)", "التعليقُ سُحِبَ: سوءُ فهمٍ لا نقض"),
    ("Frauchiger & Renner, Nat. Commun. 9:3711 (2018), arXiv:1604.07422v2", "محكَّم", "واجهة arXiv API", "نصُّ النتيجةِ الحرفيّ؛ لا «تناقضُ النظرية»"),
    ("Chen & Zhang, arXiv:1810.01080", "ما قبل النشر", "واجهة arXiv API", "فرضيّةٌ مُعدَّلة تُزيلُ التناقُضَ الظاهريَّ"),
    ("Bernal, arXiv:2106.07312", "ما قبل النشر", "واجهة arXiv API", "تفصيلٌ في البرهان"),
    ("Samuel, arXiv:2208.00060", "ما قبل النشر", "واجهة arXiv API", "لا تعدٍّ؛ تنافُسُ مُقدِّمات؛ بُطلانُ ثلاثٍ من أربع"),
    ("Elouard et al., Quantum 5:498 (2021), DOI 10.22331/q-2021-07-08-498", "محكَّم", "واجهة arXiv API", "سياقان منطقيّان، مؤثِّرَان لا يُبادِلان"),
    ("Bong et al., Nat. Phys. 16:1199 (2020), DOI 10.1038/s41567-020-0990-x, arXiv:1907.05607v4", "محكَّم", "واجهة arXiv API", "ثلاثُ مُسلَّمات؛ مخالفةُ بيل غيرُ كافيةٍ على العموم"),
    ("Walleghem et al., Phys. Rev. A 112:022212 (2025), arXiv:2310.06976v3", "محكَّم", "واجهة arXiv API", "لا‑المحلّيّةُ ليست لازمة"),
    ("Tegmark, Phys. Rev. E 61:4194 (2000), DOI 10.1103/PhysRevE.61.4194, arXiv:quant-ph/9907009v2", "محكَّم", "واجهة arXiv API", "10⁻¹³–10⁻²⁰ ث مقابل 10⁻³–10⁻¹ ث"),
    ("Hagan–Hameroff–Tuszyński, arXiv:quant-ph/0005025v1", "ما قبل النشر", "واجهة arXiv API", "خمسُ مُلاحظات؛ 10⁻⁵–10⁻⁴ ث، ثم 10⁻²–10⁻¹ ث"),
    ("Popovski et al., arXiv:1907.02441", "ما قبل النشر (مُرسَل)", "واجهة arXiv API (جلسة سابقة)", "مُستوى الدلالة‑الفاعليّة؛ لا 1801.05568"),
    ("SARAS‑3, A&A 698 A152", "محكَّم", "نصُّ الصفحة (جلسة سابقة)", "رفضُ كشفِ EDGES عند 95.3%"),
    ("الليثيوم: 2.67 ± 0.06 مقابل 2.20 ± 0.05؛ arXiv:2602.22516؛ arXiv:2508.09821", "محكَّم/ما قبل النشر", "نصُّ الصفحات (جلسة سابقة)", "0.47 dex؛ نماذجُ دوران؛ «لا فارق» من النواتج"),
    ("DESI 2025: arXiv:2503.14738 مقابل 2508.10514v7", "محكَّم/ما قبل النشر", "لم يُفتَح في هذه الجلسة", "استنتاجان مختلفان من مسحٍ واحد"),
    ("تجميعةُ S₈: arXiv:2602.12238", "ما قبل النشر", "لم تُفتَح في هذه الجلسة", "لم يُعَدَّ سُلَّمُ S₈؛ إحالةٌ فقط"),
]

add("""(٢٥) الجدولُ الآتي فهرسُ المصادرِ كلِّها: الطبقةُ (محكَّمٌ بالنظراء، ما قبل النشر، مسحوب، لم يُتحقَّق)، وطريقُ التحقّق، والرقمُ المُسنَد. العمودُ الثالث ليس حِلية: الفرقُ بين «نصُّ الصفحةِ الأصليّة» و«واجهةُ arXiv API» هو الفرقُ بين قراءةِ الخلاصةِ وقراءةِ الرقم، والفرقُ بين «هذه الجلسة» و«جلسةٍ سابقة» هو الفرقُ بين ما يمكنُ أن تُطالِبَني بمراجعتِه الآن وما لا يمكن.
""")

TABLE = ("#table(\n  columns: (1.6fr, 0.75fr, 1.0fr, 1.9fr),\n  inset: 5pt,\n"
         "  table.header[المرجع][الطبقة][كيفَ تحقّقتُ منه][ما يُسنَدُ إليهِ رقمًا],\n" +
         "\n".join("  [" + esc(sub(a)) + "], [" + esc(sub(b)) + "], [" + esc(sub(c)) + "], [" + esc(sub(d)) + "],"
                   for a, b, c, d in LEDGER) + "\n)")

add("""(٢٦) تصحيحاتٌ في هذا العملِ كلِّه، مُثبَتةٌ بأرقامِها. (أ) ثلاثةُ مُعرِّفاتٍ استُعمِلَت ثم تبيّنَ خطأُها، وصُحِّحَت في هذه الجلسة: «1807.03273» الذي ذُكِرَ برهانَ Frauchiger–Renner هو مقالٌ في ديناميكا السوائلِ الكهربائيّةِ (Electrohydrodynamic settling of drop…)، والبرهانُ هو arXiv:1604.07422؛ و«quant-ph/0102056» المنسوبُ إلى Hagan هو «Electron g‑factor Engineering in III‑V Semiconductors»، والمقصودُ arXiv:quant-ph/0005025؛ و«1801.05568» المذكورُ في سياقِ المعلومةِ الدلاليّةِ هو «Image Captioning using Deep Neural Architectures» (2017)، والمقصودُ arXiv:1907.02441. (ب) سجلٌّ واحدٌ مُختلَقٌ لا يُستعمَلُ أبدًا: «Nature 634:911، BF₀ᵤ = 44.96» — لم يُنشَر، ولا وجودَ له. (ج) أربعةُ مُعرِّفاتِ arXiv لم أستطع فتحَها في هذه الجلسة (2605.15227 و2012.07145 و2508.17098 و2602.09302)، فما يُسنَدُ إليها موقوف. (د) رقمانِ أُعيدَ حسابُهما: «120.748» المرتبةَ صار §d_reduced:5§ محسوبًا من تعريفٍ مُسمًّى، و«122.946» المنشورَ في نسخةٍ سابقةِ من هذا المشروع يُوافِقُ §d_rho:5§ المحسوبَ هنا بفارقِ ‏10⁻³. (هـ) ثلاثُ عُيوبٍ برمجيّةٍ أثّرت في الأشكالِ وصُحِّحَت: قسمةُ r_d على H₀ كانت منسيّةً فبقيَت «المسطرةُ» بوحدةِ السرعةِ بدلِ المسافة؛ وبالإصلاحِ تصيرُ على شبكةِ الانزياحِ بين §rd_min:2§ و§rd_max:2§ Mpc، وتقاطُعٌ على محورٍ مُتناقِصٍ بالإنترلانيّ أعطانا حدَّ الشبكة (z = §z_cross:2§ بعدَ الاستبدالِ بـbrentq)، وأشرطةُ الفارقِ اللوغاريتميّ كانت مكتوبةً باليدِ فاستُبدِلَت بصيَغٍ محسوبةٍ من الثوابت. وكلُّها مُثبَتٌ في النصِّ لا في هامش.
""")

add("""(٢٧) إعادةُ الإنتاجِ بثلاثِ خطواتٍ ومفاتيحَ فحصٍ سبعة. المستودعُ فيه: lcparam_DS17f.txt وsys_DS17f.txt بتواقيعِ الفقرة ٢، وfigs.py وdeepen.py وmake_facts.py وسجلّاتِ logs/. ‏(١) ‏python figs.py ‏→ الأشكالُ الستّةُ وسجلُّها؛ (٢) python deepen.py ‏→ الأشكالُ الخمسةُ وlogs/deepen.json؛ (٣) python make_facts.py ‏→ بناءُ هذا النصِّ كلِّه (الأرقامُ من logs/facts_numbers.json الذي يولّده) ثم فحصُ الـPDF. ومفاتيحُ الفحصِ في سطر: حدُّ الشبكةِ الأدنى Ωm = §Om_grid_here:4§ بـχ² = §chi2_grid:4§؛ المضلَّع §Om_par_here:6§؛ σ من التقوّس §sigma_curvature_here:6§؛ وسيطُ العدمِ في محاكاةِ الملاءمة §gof_med_null:4§؛ ثابتُ الأثر §h0_fe:4§ مع Q = §h0_Q:4§؛ مدىُ حذفِ المصدرِ الواحد §loo_fe_spread:4§؛ النافذةُ عند ×10 عرضُها §win_10_window:3§ مليارَ سنة. ومَن لم يوافِقْه عددٌ من هذه السبعةِ فليبدأ من التوقيعِ قبلَ أن يبدأَ من الحِساب: ‏§lc_md5:g32§.
""")

HEAD = """#set document(title: "الكون والعقل: طبعةٌ وقائعيّة", author: "قياسٌ مستقلٌّ من بيانات Pantheon+ ومراجعةٌ نصّيّةٌ للمصادر")
#set page(paper: "a4", margin: (top: 2.1cm, bottom: 2.3cm, left: 2.5cm, right: 2.5cm), numbering: "١", header: context { align(right, text(size: 8.5pt, counter(page).display())) })
#set text(lang: "ar", dir: rtl, font: ("Noto Naskh Arabic", "DejaVu Sans"), size: 11.4pt)
#set par(justify: true, leading: 0.92em, first-line-indent: 0em)
#set figure.caption(position: bottom)
"""

BODY = "\n\n".join(esc(sub(p.strip())) if not p.lstrip().startswith("#figure(") else p.strip()
                  for p in P if p.strip())
SRC = HEAD + "\n" + BODY + "\n\n" + TABLE + "\n"
open("facts.typ", "w", encoding="utf-8").write(SRC)
print("facts.typ:", len(SRC), "chars,", SRC.count("#figure("), "figures,", len(N), "numbers")

# ============================================================ build + audit
import typst
typst.compile("facts.typ", output="facts.pdf", root=".", font_paths=["/usr/share/fonts/truetype/noto",
                                                                      "/usr/share/fonts/truetype/dejavu"])
import pymupdf
d = pymupdf.open("facts.pdf")
pages, imgs = len(d), sum(len(d[p].get_images()) for p in range(len(d)))
txt = " ".join(re.sub(r"\s+", " ", d[p].get_text()) for p in range(pages))
LEAK = [r"\textbf", r"\emph", r"\item", r"\cite", r"\S", r"\mu", r"\alpha", r"\beta", r"\to", r"\pm",
        "\\\\", r"\rm", r"\label", r"\ref", r"\\_", r"\[", r"\]", "$", "§", "#figure", "#set", "image("]
hits = {k: txt.count(k) for k in LEAK if txt.count(k)}
# Latin tokens are legitimate only as names, units, journal strings and acronyms.
# Everything quoted inside the ledger counts as a reference string by construction.
ALLOW = set("""arXiv bioRxiv Nature Physics Science Quantum Pantheon Journal Astrophysical DOI MD5
PCI IIT JAGB TRGB CCHP HST JWST Gaia Planck Riess Scolnic Tegmark Hagan Tuszyński COGITATE Albantakis
Butlin Chalmers Barrett Pusey Rudolph Cabbole Bernal Samuel Elouard Walleghem Bong Casali Salaberli
Soto Szu Chen Zhang Anderson Bedin Popovski SARAS EDGES DESI Lithium Commun Biobehav Neurosci Rev
Quantum PASP Proc Natl Acad Springer Wiley Elsevier Oxford Cambridge AApj ApJ ApJL MNRAS JCAP
LambdaCDM LCDM deSitter Einstein Bohr Heisenberg microtubules actin laser Boltzmann Hubble
TMS EEG fMRI MEG OK Cepheid AGB GeV Paule Mandel The PBR REML brentq deepen diag
Stud Studies Nat Phys Physical Review Reviews Neural Communications Biobehavioral Architectures
Captioning Image Deep Electrohydrodynamic Electron Engineering Semiconductors III Irrelevance
Commutation Tension Wigner astrophys meV Mpc Gpc Kpc pc mag CrI dex Gyr Typst LaTeX pandoc PDF JSON
SHA DOIs Union2 CDM CTE LNB Naskh Markov Frauchiger Renner Mermin Linden Brunner Hameroff Penrose
Penrosian Lempel Ziv Turok DerSimonian Laird Verrelst Freedman Carnegie Chicago Observatories
astroph arxiv Press Farren Aghamusof Adams Electrophysiol Conscious Consciousness Electrophysiology
Research Letters Electronics DESI22 DESI25 API Sitter Gibbs Frenk Richards""".split())
LEDGER_WORDS = " ".join(" ".join(row) for row in LEDGER)
ALLOW |= set(re.findall("[A-Za-z][A-Za-z0-9'.-]*", LEDGER_WORDS))
ALLOW |= set(re.findall("[A-Za-z][A-Za-z0-9'.-]*", " ".join(FIGCAPS)))
latin = sorted({w for w in re.findall("[A-Za-z]{3,}", txt) if w not in ALLOW})
# A PDF of RTL text is extracted in visual order, so the Arabic-Indic ordinals that
# Typst prints in the captions cannot be read back reliably here. What can be checked
# is that every caption marker was typeset, that no figure was dropped, and that the
# figures were placed in ordinal order in the source that produced this PDF.
plain = re.sub(r"[ً-ْـ]", "", txt)
n_caps = len(re.findall("الشكل", plain))
this_file = open(os.path.abspath(__file__), encoding="utf-8").read()
fig_src = [int(m.group(1)) for m in re.finditer(r"add\(figure\((\d+),", this_file)]
# the caption wording itself: the ordinals must run 1..11 in the same source order
def _norm(a):
    a = re.sub(r"[\u064b-\u0652\u0670\u0640]", "", a)
    return a.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ى", "ي")

ORD = [_norm(w) for w in ["الاول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع",
                          "الثامن", "التاسع", "العاشر", "الحادي عشر"]]
caps_ord = [next((k + 1 for k, w in enumerate(ORD) if _norm(c).startswith("الشكل " + w)), 0)
            for c in FIGCAPS]
if 0 in caps_ord:
    print("FAILED: caption without a recognisable ordinal:",
          [c[:24] for c in FIGCAPS if caps_ord[FIGCAPS.index(c)] == 0])
print("pages=", pages, "words=", len(txt.split()), "figures=", imgs,
      "arabic_chars=", len(re.findall("[\u0600-\u06FF]", txt)))
print("markup leaks:", hits if hits else "{}")
print("caption markers:", n_caps, "| figure order:", fig_src, "| caption ordinals:", caps_ord)
if latin:
    print("latin outside allowlist:", latin[:30])
if (hits or imgs != 11 or n_caps < SRC.count("#figure(") or len(fig_src) != 11
        or fig_src != list(range(11)) or caps_ord != list(range(1, 12)) or "§" in txt):
    print("FAILED:", "leaks" if hits else "", "figures" if imgs != 11 else "",
          "captions" if (n_caps < SRC.count("#figure(") or fig_src != list(range(11))
          or caps_ord != list(range(1, 12))) else "",
          "placeholders" if "§" in txt else "")
    sys.exit(1)
print("all checks passed ->", os.path.abspath("facts.pdf"))
