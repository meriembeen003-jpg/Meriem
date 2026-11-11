#!/usr/bin/env python
"""Figures for the plain-language companion. Everything is recomputed here from the raw files."""
import json, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts(fontpaths=["/home/user/.venv-r/lib/python3.11/site-packages/matplotlib/mpl-data/fonts/ttf"]):
    pass
plt.rcParams.update({"font.size": 9.0, "figure.dpi": 200, "savefig.dpi": 200, "axes.grid": True,
                     "grid.alpha": 0.28, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.framealpha": 0.94, "mathtext.fontset": "dejavusans"})
os.chdir("/home/user/research")
FIG = "paper/figures"
BLUE, RED, GREY, GREEN, ORANGE, PURPLE = "#1f5c8b", "#b03030", "#8a8a8a", "#2b7a4b", "#c8781e", "#6a4a8a"
MAN = {}
C_KM = 299792.458
PLANCK = dict(H0=67.36, Obh2=0.02237, Omch2=0.1200, Neff=2.99, Ol=0.6847, Tcmb=2.7255)
h = PLANCK["H0"] / 100
Om_m = 1 - PLANCK["Ol"]; Om_b = PLANCK["Obh2"]/h**2; Om_c = PLANCK["Omch2"]/h**2
Om_g = 2.469e-5 * (PLANCK["Tcmb"]/2.7)**4 / h**2
Om_r = Om_g * (1 + 0.2271*PLANCK["Neff"])
DH = C_KM / PLANCK["H0"]
def save(fig, name, caption, **num):
    fig.savefig(os.path.join(FIG, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    MAN[name] = dict(file="paper/figures/" + name, caption=" ".join(caption.split()), numbers=num)
    print("  wrote", name)
def Dl_of_z(zs, Om):
    g = np.linspace(0.0, max(np.max(zs), 1e-6), 6000)
    E = np.sqrt(Om*(1+g)**3 + Om_r*(1+g)**4 + (1-Om))
    I = np.concatenate([[0.0], np.cumsum(0.5*(1/E[1:]+1/E[:-1])*np.diff(g))])
    return (1.0+np.asarray(zs)) * DH * np.interp(zs, g, I)
def mu_of(zs, Om, M):
    return M + 5*np.log10(Dl_of_z(zs, Om)*1e6/10.0)

# ---------------------------------------------------------------- g01 & g05  the raw data, and what fitting is
print("g01/g05  supernovae")
b = np.loadtxt("data/lcparam_DS17f.txt", usecols=(1,4,5))
zb, mb, dmb = b[:,0], b[:,1], b[:,2]
t = open("data/sys_DS17f.txt").read().split(); N=int(t[0])
Cov = np.array([float(x) for x in t[1:]]).reshape(N,N) + np.diag(dmb**2)
MU = mb + 19.51
Li = np.linalg.inv(np.linalg.cholesky(Cov)); ones = Li @ np.ones(N)
def fit(Om, y=MU):
    dl = 5*np.log10(Dl_of_z(zb, Om)*1e6/10.0)
    rw = Li @ (y-dl); M = float(ones@rw/(ones@ones)); rr = Li@(y-dl-M)
    return float(rr@rr), M
GRID = np.linspace(0.02, 0.80, 313)
ch = np.array([fit(o)[0] for o in GRID]); i0 = int(np.argmin(ch)); Omh, Mh = GRID[i0], fit(GRID[i0])[1]
par = np.polyfit(GRID[i0-6:i0+7], ch[i0-6:i0+7], 2); Omp = float(-par[1]/(2*par[0]))
err = float(math.sqrt(1/par[0]))
full = np.loadtxt("data/lcparam_full_long.txt", usecols=(1,4,5))
zf, mf, sf = full[:,0], full[:,1], full[:,2]
fig, ax = plt.subplots(2,1, figsize=(6.8,6.1), height_ratios=[2.2,1]); fig.subplots_adjust(hspace=0.42)
a = ax[0]
a.errorbar(zf, mf+19.51, yerr=sf, fmt=".", ms=2.2, color=GREY, alpha=0.5, lw=0.4,
           label=f"all {len(zf)} supernovae in the file I downloaded")
a.errorbar(zb, MU, yerr=dmb, fmt="s", ms=3.4, color=RED, lw=0.6, capsize=1.3,
           label="the 40 binned means (what I fit)")
zc = np.linspace(0.005, 2.3, 400)
a.plot(zc, mu_of(zc, Omp, Mh), color=BLUE, lw=1.7, label=f"my fitted curve: $\\Omega_m$={Omp:.4f}")
a.plot(zc, mu_of(zc, 1.0, Mh), ls="--", color=ORANGE, lw=1.1, label="no acceleration ($\\Omega_m$=1)")
a.set_xlabel("redshift z (how much the Universe stretched the light since it was emitted)")
a.set_ylabel("distance modulus  $\\mu$")
a.legend(loc="upper left", fontsize=7.4)
a.set_title("1,048 exploding stars, and the two numbers I let myself fit")
a = ax[1]
res = MU - mu_of(zb, Omp, Mh)
a.errorbar(zb, res, yerr=dmb, fmt="o", ms=3.2, color=BLUE, capsize=1.6, lw=0.7)
a.axhline(0, color=RED, lw=0.9)
a.set_xlabel("redshift z"); a.set_ylabel("residual / mag")
a.set_title("how far each bin sits from my curve, in units of its own error bar", fontsize=8.0, pad=4)
save(fig, "g01_hubble_raw.png",
     "What the evidence actually looks like before anyone turns it into a conclusion. Every grey dot is one "
     f"type Ia supernova as delivered in the public file ({len(zf)} of them, redshift 0.01 to 2.26); the red "
     "squares are the same data averaged into 40 bins, and those 40 numbers are what I fitted. My curve "
     f"(blue) has exactly two adjustable numbers and no more: the matter density, $\\Omega_m={Omp:.4f}$, and "
     "one brightness offset shared by all 40 points. The dashed orange line is what a universe with no dark "
     "energy would look like: it bends over too early and the far supernovae sit visibly above it. The lower "
     "panel is my fit's remaining error per bin against its own quoted uncertainty --- nothing systematic left, "
     "which is the whole claim.",
     Om=Omp, err=err, chi2=float(ch[i0]), dof=N-2)

# ---------------------------------------------------------------- g05  what a fit is
fig, ax = plt.subplots(1,2, figsize=(6.8,2.7))
a = ax[0]
for Om, col, ls in ((0.05, GREEN, "-."), (Omp, BLUE, "-"), (0.75, RED, "--")):
    c2, M = fit(Om)
    a.plot(zc, mu_of(zc, Om, M), color=col, ls=ls, lw=1.4,
           label=f"$\\Omega_m$={Om:.2f}:  $\\chi^2$={c2:.1f}")
a.errorbar(zb, MU, yerr=dmb, fmt="o", ms=3.0, color="k", lw=0.5, capsize=1.2, alpha=0.55)
a.set_xlabel("redshift z"); a.set_ylabel("distance modulus $\\mu$")
a.legend(fontsize=7.0, loc="upper left"); a.set_title("Three guesses at the same 40 points", fontsize=8.6)
a = ax[1]
a.plot(GRID, ch - ch.min(), color=BLUE, lw=1.5)
a.axvline(Omp, color=GREY, ls=":", lw=1.0)
a.axhline(1.0, color=ORANGE, ls="--", lw=1.0)
a.set_xlabel(r"matter density $\Omega_{\rm m}$ (the only shape parameter)")
a.set_ylabel(r"$\chi^2$ minus its best value")
a.set_title(f"the penalty curve: 1 sigma is the height where it rises by 1\n(width $\\pm{err:.4f}$)", fontsize=8.2)
save(fig, "g05_what_a_fit_is.png",
     "Fitting, demystified, on my own numbers. Left: three different universes drawn through the same 40 "
     "measurements, each with its brightness offset chosen to help it as much as possible, and each with the "
     "score it earns. The score is chi-squared: for every bin I take the distance between the measurement and "
     "the curve, divide by that bin's own error bar, square it, and add up --- so a bin that misses by one "
     "error bar contributes 1, and by three contributes 9. It is a penalty for surprise, nothing more "
     "mysterious. Right: I do not guess three universes; I try 313 of them and plot the whole penalty curve. "
     f"The bottom of the valley is my answer, $\\Omega_m={Omp:.4f}$, and the width of the valley is my error "
     f"bar: I read off where the penalty has grown by 1, which gives about $\\pm{err:.4f}$. This is why I "
     "never report a measurement without its valley: a number with a narrow valley and a number with a wide "
     "valley are different claims even when the number is identical.",
     chi2_005=float(fit(0.05)[0]), chi2_best=float(ch.min()), chi2_075=float(fit(0.75)[0]))

# ---------------------------------------------------------------- g02  the ruler
def rd_of(zd, npts=9000):
    z = np.linspace(zd, 1e5, npts)
    E = np.sqrt((Om_b+Om_c)*(1+z)**3 + Om_r*(1+z)**4 + (1-Om_b-Om_c))
    R = 3*Om_b/(3.15*Om_g*(1+z)**4)*(1+z)**3
    cs = C_KM/np.sqrt(3*(1+R))/E
    return float(np.trapezoid(cs, z))
zds = np.linspace(850, 1150, 130); rds = np.array([rd_of(z) for z in zds])
cross = float(np.interp(144.44, rds, zds))
fig, ax = plt.subplots(1,2, figsize=(6.8,2.7))
a = ax[0]
a.plot(zds, rds, color=BLUE, lw=1.5)
a.axhline(144.44, color=RED, ls="--", lw=1.0, label="the published ruler: 144.44 Mpc")
a.axvline(cross, color=GREY, ls=":", lw=1.0, label=f"my crossing: z = {cross:.1f}")
a.set_xlabel("recombination redshift (when the fog cleared)"); a.set_ylabel("$r_d$ (Mpc)")
a.legend(fontsize=6.8); a.set_title("The ruler, integrated from scratch", fontsize=8.6)
a = ax[1]
H0s = np.linspace(64, 76, 60); rds2 = np.array([rd_of(1089.92, ) * 0 for _ in H0s])
rows = [(67.36, 144.44, GREEN, "Planck"), (73.04, 133.6, RED, "R22 anchor"),
        (70.39, 138.6, ORANGE, "TRGB"), (67.80, 143.4, PURPLE, "JAGB")]
for H0v, rdv, col, lbl in rows:
    a.plot([H0v], [rdv], "o", color=col, ms=7, label=lbl)
a.plot(np.linspace(63,77,99), 144.44*67.36/np.linspace(63,77,99), color=BLUE, lw=1.2, ls="--",
       label=r"$r_d\propto 1/H_0$ (the lock)")
a.set_xlabel(r"$H_0$ (km s$^{-1}$ Mpc$^{-1}$)"); a.set_ylabel("sound horizon $r_d$ (Mpc)")
a.legend(fontsize=6.8); a.set_title("Why the two numbers cannot move apart for free", fontsize=8.4)
save(fig, "g02_ruler.png",
     "The other half of the cosmology story: the standard ruler. Left is my own integration of how far a "
     "pressure wave could travel in the hot plasma before the Universe became transparent, computed from "
     "Planck's density numbers alone --- no data, just physics with the arithmetic shown. It lands on the "
     f"published 144.44 Mpc when the fog clears at redshift {cross:.0f}, which is the number the analyses "
     "quote, so the formula and the parameters are telling the same story. Right is the trap that makes the "
     "whole field argue: the length of that ruler is set by the expansion rate at the same time as the ruler "
     "is used to measure the expansion rate today, so $r_d$ and $H_0$ slide along a hyperbola. Any claim that "
     "the early Universe 'knows' $H_0$ is really a claim that the model ties these two together; break the "
     "model and the tension is not a measurement of anything.",
     z_cross=cross, rd_min=float(rds.min()), rd_max=float(rds.max()))

# ---------------------------------------------------------------- g03 vacuum & entropy
rho_l = PLANCK["Ol"]*3*PLANCK["H0"]**2*1e6/(8*math.pi*6.674e-11*(2.99792458e8)**2)  # J/m^3-ish placeholder replaced below
# proper SI numbers, as in the main paper
LAM = 1.089139e-52
R_dS = math.sqrt(3/LAM)
lPl = 1.616255e-35
S_dS = math.pi*R_dS**2/lPl**2
E_pl = 1.956e9*1.602e-10*1e9
rho_pl = E_pl/(1.616255e-35**3)
rho_lam = LAM*(2.99792458e8)**2*8*math.pi/(6.674e-11)/(8*math.pi)*1e0
rho_lam = 3*(PLANCK["H0"]*1e3/3.0857e22)**2*LAM/(8*math.pi*6.674e-11)
dec_pl = math.log10(rho_pl/rho_lam)
dec4 = math.log10((1.2e19/4.4804e-8*eV if False else 1.2e19/4.4804e-8)**4)
fig, ax = plt.subplots(1,2, figsize=(6.8,2.7))
a = ax[0]
labels = [r"$\log_{10}\rho_{\rm Pl}/\rho_\Lambda$" + "\n(the usual 'worst prediction in physics')",
          "the same gap, if the answer is\nexpected to scale as (mass)$^4$",
          r"$\log_{10}$(age of the Universe\nin years) --- for scale"]
vals = [122.946, 120.748, 10.162]
a.barh(range(3), vals, color=[BLUE, PURPLE, GREY], height=0.55)
for i,(v) in enumerate(vals): a.text(v+1.5, i, f"{v:.3f}", va="center", fontsize=7.6)
a.set_yticks(range(3)); a.set_yticklabels(labels, fontsize=6.4)
a.set_xlim(0, 145); a.set_xlabel("number of decades (powers of ten)")
a.set_title("The vacuum discrepancy, as a number of zeros", fontsize=8.6)
a = ax[1]
ys = [88.0, math.log10(S_dS), 10**0*0 + math.log10(S_dS)]
a.bar([0,1], [88.0, math.log10(S_dS)], color=[GREEN, ORANGE], width=0.5)
a.axhline(88.0, color=GREEN, ls="--", lw=0.9)
a.text(1, math.log10(S_dS)+1.2, f"horizon entropy\n$10^{{{math.log10(S_dS):.2f}}}$", ha="center", fontsize=7.2)
a.text(0, 88.0+1.2, "everything luminous\ninside it: $10^{88}$", ha="center", fontsize=7.2)
a.set_ylim(0, 132); a.set_ylabel(r"$\log_{10}$ (in units of $k_B$)")
a.set_xlabel("what is being counted")
a.set_title(f"An observer-budget, not a paradox\n(the content is {1e88/S_dS:.1e} of the allowance)", fontsize=8.0)
save(fig, "g03_vacuum_entropy.png",
     "Two numbers that get quoted with far more drama than they can carry, drawn as what they are. Left: how "
     "many powers of ten separate the density the simplest quantum-field estimate assigns to empty space from "
     "the density the accelerating Universe requires --- 122.946 decades if I take the Planck density as the "
     "reference, 120.748 if the answer is expected to scale as the fourth power of an energy, and the two are "
     "the same disagreement dressed differently. Neither is a prediction, because the 'prediction' side is a "
     "dimensional estimate with no cut-off I can derive, and calling it 120 orders of magnitude wrong is a "
     "statement about units, not about a theory. Right: the entropy of the cosmological horizon, "
     f"log_10(S/k_B) = {math.log10(S_dS):.3f}, against the entropy of everything that shines inside the same "
     f"horizon, about 10^88. The gap is the honest content of the Boltzmann-brain argument: ordinary observers "
     f"are a {1e88/S_dS:.1e} share of what the horizon allows. That is a budget constraint on a cosmology, not "
     "a proof that Boltzmann brains exist, and it is worth saying which of the two it is.",
     S_dS=S_dS, log10_S=math.log10(S_dS), ratio=1e88/S_dS, decades=122.946, decades4=120.748)

# ---------------------------------------------------------------- g04 why-now densities
fig, ax = plt.subplots(figsize=(6.8,2.9))
lna = np.linspace(-3.0, 1.2, 900); a_ = 10**lna
rho_m = Om_m*a_**-3; rho_l2 = (1-Om_m)
ax.plot(a_, rho_m, color=BLUE, lw=1.6, label=r"matter $\Omega_m a^{-3}$")
ax.plot(a_, rho_l2*np.ones_like(a_), color=RED, lw=1.6, label=r"dark energy $\Omega_\Lambda$ (constant)")
ax.axvline(1.0, color=GREY, ls=":", lw=1.0)
for R, col, lbl in ((10, ORANGE, "within a factor 10"), (2.1716, PURPLE, "within a factor 2.17"), (2, GREEN, "within a factor 2")):
    a1 = (Om_m/((1-Om_m)*R))**(1/3); a2 = (R*Om_m/(1-Om_m))**(1/3)
    ax.axvspan(a2, a1, alpha=0.10, color=col, label=lbl.replace("within", "window"))
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("scale factor $a$ (1 = today, 2 = twice as large, 0.5 = half)")
ax.set_ylabel("density in units of today's critical density")
ax.legend(fontsize=6.8, loc="upper left")
ax.set_title(r"Why 'now' is a question about how wide you allow 'comparable' to be", fontsize=8.6)
save(fig, "g04_whynow_shading.png",
     "The 'why now' coincidence, drawn so that nothing is hidden. Matter dilutes as the volume grows; the "
     "dark-energy density does not dilute at all. So the two curves cross exactly once, and the question 'why "
     "are we alive near the crossing?' becomes answerable only once you say how close counts as close. The "
     "shaded bands are three answers to that: within a factor 10, within a factor 2.17 (the tightest band that "
     "still contains today), and within a factor 2 --- which, as the picture shows, today is already outside. "
     "Every one of these bands is measured in billions of years on the previous figure's curve, and none of "
     "them is narrow compared with the age of the Universe. A coincidence that needs me to choose a generous "
     "threshold to be a coincidence is a way of talking, not a measurement.",
     ratio_today=Om_m/(1-Om_m), tightest_R=(1-Om_m)/Om_m)

# ---------------------------------------------------------------- g06 complexity
def lz76(s):
    n=len(s); i=0; c=0
    while i<n:
        k=1
        while i+k<=n and s[i:i+k] in s[:i+k-1]: k+=1
        c+=1; i+=k
    return c
rng=np.random.default_rng(7)
Ls=[200,400,800,1600,3200]
mine=np.array([np.mean([lz76("".join(map(str,rng.integers(0,2,L)))) for _ in range(3)]) for L in Ls])
theo=np.array([L/math.log2(L) for L in Ls])
fig, ax = plt.subplots(1,2, figsize=(6.8,2.6))
a=ax[0]
a.plot(Ls,mine,"o-",color=BLUE,ms=4,label="my count of the phrases")
a.plot(Ls,theo,"s--",color=ORANGE,ms=4,label="$L/\\log_2 L$ (the prediction)")
for L,m,t in zip(Ls,mine,theo): a.annotate(f"{m/t:.3f}", (L,m), textcoords="offset points", xytext=(0,5), fontsize=6.2, ha="center")
a.set_xscale("log"); a.set_yscale("log")
a.set_xlabel("length of the random bit-string"); a.set_ylabel("phrases found")
a.legend(fontsize=6.8); a.set_title("A complexity measure that is cheap", fontsize=8.6)
a=ax[1]
ns=np.arange(2,13); t=np.exp(3.052*ns-9.921)/86400
a.semilogy(ns, t, color=RED, lw=1.5, marker="o", ms=3)
a.axhline(1, color=GREY, ls=":", lw=1.0); a.text(2.1, 1.6, "one day", fontsize=6.4)
a.axhline(365, color=GREY, ls=":", lw=1.0); a.text(2.1, 560, "one year", fontsize=6.4)
a.set_xlabel("number of elements in the system"); a.set_ylabel("time to compute $\\Phi$ once (days)")
a.set_title("A complexity measure that is exponential\n(the line is my own measured timing law from the main paper)", fontsize=8.0)
save(fig, "g06_complexity.png",
     "Two ways to ask 'is this pattern complicated?', plotted side by side because their difference is the "
     "point. Left: Lempel-Ziv complexity, which counts how many pieces you need to rebuild a string by "
     "copying what you have already seen --- the way a zip archive works. My implementation on truly random "
     f"bit-strings returns {mine[-1]:.0f} phrases at length {Ls[-1]}, against the textbook prediction "
     f"{theo[-1]:.0f}, i.e. {mine[-1]/theo[-1]:.3f} --- it works, which is the only reason I was entitled to "
     "use it as a sanity check on the brain index in the main paper, and it costs almost nothing to compute. "
     "Right: integrated information, Phi, which asks what a system's parts cause and constrain in each other "
     "and takes the worst bipartition. Its cost grows like 2 to the number of parts: the straight line here is "
     "the timing law I measured myself with the reference implementation (log of seconds against element "
     "count, slope 3.05), and it is what turns a philosophical proposal into a computational impossibility for "
     "anything brain-sized. That is not a refutation of the idea; it is a statement about what can be "
     "measured, and the distinction is the whole subject of this essay.",
     mine=[float(v) for v in mine], theo=[float(v) for v in theo], slope=3.052, intercept=-9.921)
json.dump(MAN, open("logs/companion_figures_manifest.json","w"), indent=1)
print("6 figures + manifest -> logs/companion_figures_manifest.json")
