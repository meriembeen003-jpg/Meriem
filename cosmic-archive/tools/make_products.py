#!/usr/bin/env python3
"""Derive display/audio products from the archived raw files.
Every step here is ours (this repository); nothing is downloaded.
"""
import os, json, hashlib
import itertools
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.io import fits

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
OUT = {}

def savefig(fig, rel):
    path = P(rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig)
    OUT[rel] = hashlib.sha256(open(path,"rb").read()).hexdigest()
    print("wrote", rel)

def savewav(rel, samples, rate):
    from scipy.io import wavfile
    path = P(rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    s = np.asarray(samples, dtype=np.float32)
    s = s / (np.max(np.abs(s)) + 1e-30) * 0.9
    wavfile.write(path, int(rate), (s * 32767).astype(np.int16))
    OUT[rel] = hashlib.sha256(open(path,"rb").read()).hexdigest()
    print("wrote", rel, f"{rate} Hz, {len(s)/rate:.1f} s")

# ---------------------------------------------------------------- E01 Planck
d = np.loadtxt(P("01_CMB_380ka/raw/COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt"))
ell, TT, TE, EE = d[:,0], d[:,1], d[:,2], d[:,3]
fig, ax = plt.subplots(figsize=(9,4.2))
ax.plot(ell, TT, lw=1.0, label="TT", color="#1f3b73")
ax.set_xlabel("multipole  $\\ell$"); ax.set_ylabel("$D_\\ell$  [$\\mu$K$^2$]")
ax.set_title("Planck 2018 best-fit \u039bCDM TT spectrum (PLA product R3.01) - chart of the archive file, not a sky map")
ax.legend(frameon=False); ax.grid(alpha=.25)
savefig(fig, "01_CMB_380ka/derived/planck2018_TT_spectrum.png")
fig, ax = plt.subplots(figsize=(9,4.2))
for y,c,lab in ((TT,"#1f3b73","TT"),(TE,"#8c2d04","TE"),(EE,"#238b45","EE")):
    ax.plot(ell, y, lw=.9, color=c, label=lab)
ax.set_xlabel("multipole  $\\ell$"); ax.set_ylabel("$D_\\ell$  [$\\mu$K$^2$]")
ax.set_title("Planck 2018 best-fit spectra, TT/TE/EE (same PLA file)")
ax.legend(frameon=False); ax.grid(alpha=.25)
savefig(fig, "01_CMB_380ka/derived/planck2018_TT_TE_EE.png")

# ---------------------------------------------------------------- E04 MAST
h = fits.open(P("05_MAST_star_200ly/raw/gd153_stiswfcnic_003.fits"))
t = h[1].data
wl, fl, fw = t["WAVELENGTH"], t["FLUX"], t["FWHM"]
ok = np.isfinite(fl) & (fl > 0) & (t["DATAQUAL"] == 0)
fig, ax = plt.subplots(figsize=(9,3.8))
ax.plot(wl[ok], fl[ok], lw=.6, color="#111111")
ax.set_yscale("log"); ax.set_xlabel("wavelength [Å]"); ax.set_ylabel("flux [erg s$^{-1}$ cm$^{-2}$ Å$^{-1}$]")
ax.set_title("HST/STIS spectrum of GD153 (MAST product gd153_stiswfcnic_003) - real archival spectrum")
ax.grid(alpha=.25)
savefig(fig, "05_MAST_star_200ly/derived/gd153_stis_spectrum.png")

# ---------------------------------------------------------------- E05 GWOSC
import h5py
from scipy import signal
from scipy.io import wavfile

def load_gw(fn):
    f = h5py.File(P(fn), "r")
    strain = f["strain/Strain"][:]
    att = {k: f["strain/Strain"].attrs[k] for k in f["strain/Strain"].attrs}
    meta = {k: f["meta"][k][()] for k in f["meta"].keys() if f["meta"][k].shape == ()}
    return strain, att, meta

def whiten(strain, fs, band=(20., 300.)):
    f, psd = signal.welch(strain, fs=fs, nperseg=int(4*fs))
    freqs = np.fft.rfftfreq(len(strain), 1/fs)
    S = np.interp(freqs, f, psd)
    w = np.fft.irfft(np.fft.rfft(strain)/np.sqrt(S), n=len(strain))
    sos = signal.butter(4, [band[0], band[1]], btype="band", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, w)

FS = 16384; TC = 1126259462.4
series = {}
for det, fn in (("H1","02_GW150914_1.3Gyr/raw/H-H1_LOSC_16_V1-1126259446-32.hdf5"),
                ("L1","02_GW150914_1.3Gyr/raw/L-L1_LOSC_16_V1-1126259446-32.hdf5")):
    strain, att, meta = load_gw(fn)
    t0 = float(att["Xstart"]); fs = 1.0/float(att["Xspacing"])
    print(det, "strain", strain.shape, "fs", fs, "t0", t0, "meta", {k:str(v)[:40] for k,v in meta.items()})
    w = whiten(strain, fs)
    t = t0 + np.arange(len(w))/fs
    series[det] = (t, w, fs, strain)

fig, axes = plt.subplots(2,1, figsize=(9,5.2), sharex=True)
for ax,(det,(t,w,fs,strain)) in zip(axes, series.items()):
    m = (t > TC-0.45) & (t < TC+0.45)
    ax.plot(t[m]-TC, w[m], lw=.7, color="#0b3d91" if det=="H1" else "#b2182b")
    ax.set_ylabel(f"{det} whitened strain"); ax.grid(alpha=.25)
axes[1].set_xlabel("time relative to GPS 1126259462.4 [s]")
axes[0].set_title("GW150914 strain, whitened + 20-300 Hz band-pass (our processing of GWOSC/LOSC HDF5)")
savefig(fig, "02_GW150914_1.3Gyr/derived/gw150914_whitened_H1_L1.png")

# audio: whitened, band-passed 20-300 Hz, played at the native 16 kHz sample rate
t, w, fs, _ = series["H1"]
savewav("02_GW150914_1.3Gyr/derived/audio/gw150914_H1_sonification.wav", w, fs)

# chirp mass posterior
p = h5py.File(P("02_GW150914_1.3Gyr/raw/gw150914_posteriors_thinned.hdf"), "r")
m1 = p["samples/mass1"][:]; m2 = p["samples/mass2"][:]
mc = (m1*m2)**0.6/(m1+m2)**0.2
fig, ax = plt.subplots(figsize=(7,3.6))
ax.hist(mc, bins=70, color="#3b3b6d", alpha=.9)
ax.axvline(np.median(mc), color="#d95f02", lw=1.4, label=f"median = {np.median(mc):.2f} Msun")
ax.set_xlabel("chirp mass $\\mathcal{M}$ [M$_\\odot$]"); ax.set_ylabel("posterior samples")
ax.set_title("GW150914 chirp mass from the official thinned posterior samples (n=%d)" % len(mc))
ax.legend(frameon=False)
savefig(fig, "02_GW150914_1.3Gyr/derived/gw150914_chirpmass_posterior.png")
json.dump({"chirp_mass_median": float(np.median(mc)), "n_samples": int(len(mc)),
           "mass1_median": float(np.median(m1)), "mass2_median": float(np.median(m2)),
           "distance_median_mpc": float(np.median(p["samples/distance"][:]))},
          open(P("02_GW150914_1.3Gyr/derived/gw150914_posterior_summary.json"),"w"), indent=1)

# ---------------------------------------------------------------- EHT
def read_uvfits(fn):
    """AIPS uvfits: UU/VV are already in seconds after FITS scaling; u_lambda = UU * freq."""
    u = fits.open(P(fn))
    hd = u[0].header
    d = u[0].data
    freq = float(hd["CRVAL4"])
    uu = np.asarray(d["UU---SIN"], float).ravel() * freq
    vv = np.asarray(d["VV---SIN"], float).ravel() * freq
    raw = np.asarray(d["DATA"], float).reshape(len(d), -1)
    re, im, wt = raw[:, 0], raw[:, 1], raw[:, 2]      # first IF, first Stokes
    good = np.isfinite(re) & np.isfinite(im) & np.isfinite(wt) & (wt > 0)
    return uu[good], vv[good], (re[good] + 1j*im[good]), wt[good], freq, hd

def closure_phases(base, V, names):
    """Median closure phase (degrees) for every station triangle."""
    pairs = {}
    for b, v in zip(base.astype(int), V):
        a, c = b // 256, b % 256
        pairs.setdefault((a, c), []).append(v)
        pairs.setdefault((c, a), []).append(np.conj(v))
    ants = sorted({k[0] for k in pairs})
    tris, cps = [], []
    for t in itertools.combinations(ants, 3):
        if all((x, y) in pairs for x, y in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0]))):
            z = (np.median(pairs[(t[0], t[1])]) * np.median(pairs[(t[1], t[2])])
                 * np.median(pairs[(t[2], t[0])]))
            tris.append(t); cps.append(np.degrees(np.angle(z)))
    return ants, tris, np.array(cps)

def uv_amp_closure(tag, fn, fov_label, doy):
    u = fits.open(P(fn)); hd = u[0].header; d = u[0].data
    freq = float(hd["CRVAL4"])
    uu = np.asarray(d["UU---SIN"], float).ravel() * freq / 1e9      # Glambda
    vv = np.asarray(d["VV---SIN"], float).ravel() * freq / 1e9
    base = np.asarray(d["BASELINE"], float).ravel()
    raw = np.asarray(d["DATA"], float).reshape(len(d), -1)
    V = raw[:, 0] + 1j*raw[:, 1]
    good = np.isfinite(V) & np.isfinite(raw[:, 2]) & (raw[:, 2] > 0)
    uu, vv, V, base = uu[good], vv[good], V[good], base[good]
    r = np.hypot(uu, vv)
    bins = np.array([0.05, 0.3, 1.0, 1.5, 2.0, 2.5, 3.0, 3.25, 3.5, 3.75, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0])
    med, lo, hi, nn = [], [], [], []
    for a, b in zip(bins[:-1], bins[1:]):
        m = (r >= a) & (r < b)
        nn.append(int(m.sum()))
        if m.sum():
            med.append(np.median(np.abs(V[m]))); lo.append(np.percentile(np.abs(V[m]), 16))
            hi.append(np.percentile(np.abs(V[m]), 84))
        else:
            med.append(np.nan); lo.append(np.nan); hi.append(np.nan)
    ctr = 0.5*(bins[:-1]+bins[1:])
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    ax.errorbar(ctr, med, yerr=[np.array(med)-np.array(lo), np.array(hi)-np.array(med)],
                fmt="o-", ms=3.5, lw=1.1, color="#0b3d91", ecolor="#999999", capsize=2)
    ax.set_xlabel("projected baseline length  [G$\\lambda$]  at %.1f GHz" % (freq/1e9))
    ax.set_ylabel("median |V| [Jy]  (16-84 pct band)")
    ax.axvspan(3.0, 4.0, color="#d95f02", alpha=.12)
    ax.set_title(f"{tag}  {doy}  -  visibility amplitude vs baseline from the archive UVFITS\n"
                 "minimum near 3-4 G$\\lambda$ is the interferometric 'null' of the crescent/ring geometry")
    ax.grid(alpha=.25)
    tagdir = "03_EHT_M87_55Mly" if tag.startswith("M87") else "04_EHT_SgrA_27kly"
    savefig(fig, tagdir + "/derived/" + ("m87_uv_amplitude.png" if tag.startswith("M87") else "sgra_uv_amplitude.png"))
    ants, tris, cps = closure_phases(base, V, None)
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.hist(cps, bins=np.arange(-180, 181, 10), color="#3b3b6d")
    ax.set_xlabel("closure phase  [deg]"); ax.set_ylabel("number of triangles")
    ax.set_title(f"{tag}  {doy}  -  closure phases of {len(cps)} station triangles\n"
                 "non-zero closure phases = intrinsic source asymmetry (absolute phases are not calibrated in this release)")
    ax.grid(alpha=.25)
    savefig(fig, tagdir + "/derived/" + ("m87_closure_phases.png" if tag.startswith("M87") else "sgra_closure_phases.png"))
    return dict(tag=tag, date=doy, nvis=int(len(V)), stations=[int(a) for a in ants],
                n_triangles=int(len(cps)), median_abs_closure_deg=float(np.median(np.abs(cps))),
                amp_median_by_bin={f"{a:.2f}-{b:.2f}": (float(m_) if np.isfinite(m_) else None)
                                   for a, b, m_ in zip(bins[:-1], bins[1:], med)},
                amp_bin_counts={f"{a:.2f}-{b:.2f}": n_ for a, b, n_ in zip(bins[:-1], bins[1:], nn)},
                freq_hz=freq, max_baseline_glambda=float(r.max()), null_region="3.0-4.0 Glambda")

print("no deconvolved image is produced: the EHT release has uncalibrated absolute phases,")
print("so amplitude-vs-baseline and closure phases are the honest, reproducible reductions.")
eht_log = {}
eht_log["M87*"] = uv_amp_closure("M87*", "03_EHT_M87_55Mly/raw/SR1_M87_2017_096_hi_hops_netcal_StokesI.uvfits", "170 uas", "2017-04-06 (SR1 night 096, high band)")
eht_log["Sgr A*"] = uv_amp_closure("Sgr A*", "04_EHT_SgrA_27kly/raw/ER6_SGRA_2017_097_lo_hops_netcal-LMTcal_StokesI.uvfits", "220 uas", "2017-04-07 (ER6 night 097, low band)")
json.dump(eht_log, open(P("03_EHT_M87_55Mly/derived/eht_reduction_log.json"),"w"), indent=1)

# ---------------------------------------------------------------- E08 SDO
a = fits.open(P("06_SDO_Sun_AIA171/raw/aia_171_level1.fits"))
data = a[0].data.astype(float); hd = a[0].header
fig, ax = plt.subplots(figsize=(5.2,4.6))
im = ax.imshow(np.clip(data, 0, None), origin="lower", cmap="afmhot",
               vmax=np.percentile(data, 99.5))
ax.set_title(f"SDO/AIA {hd['WAVE_STR']}  {hd['T_OBS']}\n{data.shape[1]}x{data.shape[0]} level-1 subset, assigned gold colour")
ax.set_xticks([]); ax.set_yticks([])
fig.colorbar(im, ax=ax, shrink=.8, label="DN")
savefig(fig, "06_SDO_Sun_AIA171/derived/aia171.png")

# ---------------------------------------------------------------- E09 IRIS
from obspy import read
st = read(P("07_IRIS_Earth_seismic/raw/TA.W18A..BHZ.M.2014,076,04:11:34.SAC"))
tr = st[0]; d9 = tr.data.astype(float); sr = tr.stats.sampling_rate
tt = np.arange(len(d9))/sr
fig, ax = plt.subplots(figsize=(9,3.2))
ax.plot(tt/3600, d9, lw=.4, color="#08306b")
ax.set_xlabel("hours from 2014-03-17T04:11:34Z"); ax.set_ylabel("BHZ [counts]")
ax.set_title("IRIS DMC record - station TA.W18A, 40 sps, 612001 samples (real seismogram)")
ax.grid(alpha=.25)
savefig(fig, "07_IRIS_Earth_seismic/derived/ta_w18a_waveform.png")

f, tspec, S = signal.spectrogram(d9, fs=sr, nperseg=2048, noverlap=1024)
fig, ax = plt.subplots(figsize=(9,3.6))
im = ax.pcolormesh(tspec/3600, f, 10*np.log10(S+1e-12), shading="auto", cmap="magma")
ax.set_ylim(0, 20); ax.set_xlabel("hours from 2014-03-17T04:11:34Z"); ax.set_ylabel("frequency [Hz]")
ax.set_title("spectrogram of the same record (our processing; colours assigned, not physical)")
fig.colorbar(im, ax=ax, label="10 log10 power [dB]")
savefig(fig, "07_IRIS_Earth_seismic/derived/ta_w18a_spectrogram.png")

savewav("07_IRIS_Earth_seismic/derived/audio/ta_w18a_sonification.wav", d9, 4000)

# ---------------------------------------------------------------- E10 CMS
import uproot
f = uproot.open(P("08_CERN_LHC_2012/raw/DoubleMu12.root"))
h = f["demo/massZto2muon"]
vals, edges = h.to_numpy()
ctr = 0.5*(edges[1:]+edges[:-1])
fig, ax = plt.subplots(figsize=(8,3.8))
ax.step(ctr, vals, where="mid", color="#67000d", lw=1.1)
ax.set_xlabel("m($\\mu\\mu$) [GeV]"); ax.set_ylabel("events / bin")
ax.set_title("CMS Open Data 2012 (Run2012C DoubleMuParked AOD) - Z->2mu invariant-mass histogram\nas stored in the analysis ROOT file; no event-level file is included here")
ax.grid(alpha=.25)
savefig(fig, "08_CERN_LHC_2012/derived/cms_dimuon_z_peak.png")
peak = ctr[np.argmax(vals)]
json.dump({"hist": "demo/massZto2muon", "n_bins": int(len(vals)), "entries": float(vals.sum()),
           "peak_bin_gev": float(peak), "bin_width_gev": float(edges[1]-edges[0])},
          open(P("08_CERN_LHC_2012/derived/cms_hist_summary.json"),"w"), indent=1)

json.dump(OUT, open(P("_derived_checksums.json"),"w"), indent=1)
print("done", len(OUT), "derived files")
