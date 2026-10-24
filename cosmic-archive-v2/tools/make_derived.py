#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_derived.py — build the declared derived products from the files that
fetch_primary.py downloaded.  Every figure is labelled with the exact operation
and states whether colour is assigned.

    python tools/make_derived.py --all
    python tools/make_derived.py --event E02

A missing raw file is skipped (and reported), never replaced by synthetic data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from catalog import EVENTS, BY_ID  # noqa: E402

DERIVED = []


# --------------------------------------------------------------------------- helpers
def save(fig, rel, **meta):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    rec = dict(file=rel, bytes=p.stat().st_size,
               sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
               processing=meta.get("processing", "plot"),
               colour=meta.get("colour", "لا شيء"), audio=False)
    DERIVED[:] = [r for r in DERIVED if r["file"] != rel] + [rec]
    (ROOT / "_derived_records.json").write_text(json.dumps(DERIVED, ensure_ascii=False, indent=1),
                                                encoding="utf-8")
    print("  wrote", rel)


def savewav(rel, data, rate, note):
    from scipy.io import wavfile
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    x = np.asarray(data, dtype=np.float64)
    x = np.nan_to_num(x)
    x = x / (np.max(np.abs(x)) + 1e-30) * 0.9
    wavfile.write(p, int(rate), (x * 32767).astype(np.int16))
    rec = dict(file=rel, bytes=p.stat().st_size,
               sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
               processing=note, colour="لا شيء", audio=True, sample_rate=rate)
    DERIVED[:] = [r for r in DERIVED if r["file"] != rel] + [rec]
    (ROOT / "_derived_records.json").write_text(json.dumps(DERIVED, ensure_ascii=False, indent=1),
                                                encoding="utf-8")
    print("  wrote", rel, f"({len(x)/rate:.1f}s @ {rate} Hz)")


def raw(ev, name):
    p = ROOT / ev["folder"] / "raw" / name
    if p.exists():
        return p
    hits = list((ROOT / ev["folder"] / "raw").rglob(name)) if (ROOT / ev["folder"] / "raw").exists() else []
    return hits[0] if hits else None


def build_mp4(frames, dest: Path, *, label: str, fps: int = 12) -> int:
    """Encode a frame sequence to H.264 MP4 with an assigned colour map and label."""
    from astropy.io import fits
    from PIL import Image, ImageDraw

    arrs = []
    for f in frames:
        with fits.open(f) as h:
            d = np.array(h[0].data, dtype="float32")
            exp = float(h[0].header.get("EXPTIME", 1.0)) or 1.0
        arrs.append(d / exp)
    lo, hi = np.percentile(arrs[0], [1, 99.7])
    cmap = plt.get_cmap("inferno")
    imgs = []
    for a in arrs:
        z = np.clip((a - lo) / (hi - lo + 1e-9), 0, 1)
        rgb = (cmap(z)[..., :3] * 255).astype("uint8")
        im = Image.fromarray(rgb).resize((512, 512))
        dr = ImageDraw.Draw(im)
        dr.text((6, 6), label, fill=(255, 255, 255))
        imgs.append(im)
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        import imageio.v2 as imageio
        with imageio.get_writer(str(dest), fps=fps, codec="libx264", quality=8,
                                macro_block_size=1) as w:
            for im in imgs:
                w.append_data(np.asarray(im))
    except Exception:  # noqa: BLE001  fall back to GIF if no ffmpeg
        dest = dest.with_suffix(".gif")
        imgs[0].save(dest, save_all=True, append_images=imgs[1:], duration=int(1000 / fps), loop=0)
    print(f"  wrote {dest.relative_to(ROOT)} ({len(imgs)} frames, {fps} fps, colours assigned)")
    return fps


# --------------------------------------------------------------------------- per event
def e01(ev):
    from astropy.io import fits
    m = raw(ev, "COM_CMB_IQU-smica_2048_R3.00_full.fits")
    if m:
        with fits.open(m, memmap=True) as h:
            hdu = h[1] if len(h) > 1 else h[0]
            data = hdu.data
            if data is not None and data.ndim >= 2:
                tmap = np.array(data[0] if data.ndim > 1 else data, dtype="float64").ravel()
                nside = int(hdu.header.get("NSIDE", 0)) or int(np.sqrt(tmap.size / 12))
                try:
                    import healpy as hp
                    fig = plt.figure(figsize=(9, 5))
                    hp.mollview(tmap * 1e6, fig=fig.number, title="Planck SMICA T [µK] — colours assigned",
                                cmap="RdBu_r", unit="µK")
                    save(fig, f"{ev['folder']}/derived/smica_T_mollview.png",
                         processing="hp.mollview على خريطة SMICA الرسمية (العمود T، I_stokes)",
                         colour="RdBu_r مُسند")
                except Exception:  # noqa: BLE001
                    fig, ax = plt.subplots(figsize=(9, 4))
                    ax.hist(tmap[np.isfinite(tmap)] * 1e6, bins=400, color="#222")
                    ax.set_xlabel("T [µK]"); ax.set_ylabel("pixels")
                    ax.set_title("Planck SMICA T histogram (healpy missing — colours assigned)")
                    save(fig, f"{ev['folder']}/derived/smica_T_hist.png",
                         processing="هستوغرام قيم T من الملف الرسمي (بديل مؤقت لغياب healpy)",
                         colour="لا شيء")
    tabs = {}
    for k in ("TT", "TE", "EE"):
        p = raw(ev, f"COM_PowerSpect_CMB-{k}-full_R3.01.txt")
        if p:
            tabs[k] = np.loadtxt(p, comments="#")
    if tabs:
        fig, ax = plt.subplots(figsize=(9, 4.4))
        colors = {"TT": "#1f3b73", "TE": "#8c2d04", "EE": "#238b45"}
        for k, d in tabs.items():
            ell = d[:, 0]; dl = d[:, 1]
            ax.plot(ell, dl, lw=1.0, color=colors[k], label=f"{k} (measured)")
            if d.shape[1] >= 3:
                err = d[:, 2]
                ax.fill_between(ell, dl - err, dl + err, color=colors[k], alpha=.18, lw=0)
        ax.set_xlabel("multipole $\\ell$"); ax.set_ylabel("$D_\\ell$ [µK²]")
        ax.set_title("Planck 2018 PR3 measured TT/TE/EE spectra (archive files, no model curve)")
        ax.legend(frameon=False); ax.grid(alpha=.25)
        save(fig, f"{ev['folder']}/derived/planck_measured_spectra.png",
             processing="رسم الأعمدة المقاسة كما هي من ملفات R3.01 (بلا منحنى نظري)",
             colour="ألوان تمييز للسلسلة فقط")


def e02(ev):
    import h5py
    from scipy import signal
    png_done = False
    audios = []
    for det, name in (("H1", "H-H1_LOSC_16_V1-1126259446-32.hdf5"),
                      ("L1", "L-L1_LOSC_16_V1-1126259446-32.hdf5")):
        p = raw(ev, name)
        if not p:
            continue
        with h5py.File(p, "r") as f:
            strain = f["strain/Strain"][:]
            att = f["strain/Strain"].attrs
            fs = 1.0 / float(att["Xspacing"])
            t0 = float(att["Xstart"])
        f, psd = signal.welch(strain, fs=fs, nperseg=int(4 * fs))
        fr = np.fft.rfftfreq(len(strain), 1 / fs)
        whitened = np.fft.irfft(np.fft.rfft(strain) / np.sqrt(np.interp(fr, f, psd)), n=len(strain))
        sos = signal.butter(4, [20, 300], btype="band", fs=fs, output="sos")
        w = signal.sosfiltfilt(sos, whitened)
        t = t0 + np.arange(len(w)) / fs
        if det == "H1":
            fig, ax = plt.subplots(figsize=(9, 3.4))
            m = (t > 1126259462.4 - .45) & (t < 1126259462.4 + .45)
            ax.plot(t[m], w[m], lw=.7, color="#0b3d91")
            ax.set_title("GW150914 H1 — whitened, 20–300 Hz (our processing of the GWOSC file)")
            ax.set_xlabel("GPS time [s]"); ax.grid(alpha=.25)
            save(fig, f"{ev['folder']}/derived/gw150914_H1_whitened.png",
                 processing="Welch PSD (4 s) + band-pass 20–300 Hz", colour="لا شيء")
            png_done = True
        audios.append((det, w, fs))
    for det, w, fs in audios:
        savewav(f"{ev['folder']}/derived/audio/gw150914_{det}_sonification.wav", w, fs,
                "صوتنة: انفعال مبيَّض ومرشّح 20–300 Hz بمعدل 16 kHz (تحويل صوتي لا تسجيل)")
    sk = raw(ev, "LALInference_skymap.fits.gz")
    if sk:
        import gzip
        from astropy.io import fits
        with gzip.open(sk) if str(sk).endswith(".gz") else open(sk, "rb") as fh:
            hd = fits.getheader(fh)
        nside = int(hd.get("NSIDE", 0))
        if nside:
            import healpy as hp
            h = fits.open(sk)[1]
            prob = h.data[0] if h.data.ndim > 1 else h.data
            fig = plt.figure(figsize=(8, 4.6))
            hp.mollview(np.asarray(prob, float), fig=fig.number,
                        title="GW150914 skymap — colours assigned", cmap="viridis")
            save(fig, f"{ev['folder']}/derived/gw150914_skymap.png",
                 processing="hp.mollview لخريطة احتمال الموضع الرسمية", colour="viridis مُسند")


def eht(ev):
    from astropy.io import fits
    import itertools
    names = [p.name for p in (ROOT / ev["folder"] / "raw").glob("*.uvfits")]
    if not names:
        return
    p = raw(ev, names[0])
    with fits.open(p, memmap=True) as h:
        hd = h[0].header
        freq = float(hd["CRVAL4"])
        d = h[0].data
        uu = np.asarray(d["UU---SIN"], float).ravel() * freq / 1e9
        vv = np.asarray(d["VV---SIN"], float).ravel() * freq / 1e9
        base = np.asarray(d["BASELINE"], float).ravel()
        vis = np.asarray(d["DATA"], float).reshape(len(d), -1)
        V = vis[:, 0] + 1j * vis[:, 1]
        ok = np.isfinite(V) & np.isfinite(vis[:, 2]) & (vis[:, 2] > 0)
    uu, vv, V, base = uu[ok], vv[ok], V[ok], base[ok]
    r = np.hypot(uu, vv)
    bins = np.array([0.05, .3, 1, 1.5, 2, 2.5, 3, 3.25, 3.5, 3.75, 4, 4.5, 5, 5.5, 6, 7, 8, 9])
    med, lo, hi = [], [], []
    for a, b in zip(bins[:-1], bins[1:]):
        m = (r >= a) & (r < b)
        if m.sum():
            med.append(np.median(np.abs(V[m])))
            lo.append(np.percentile(np.abs(V[m]), 16)); hi.append(np.percentile(np.abs(V[m]), 84))
        else:
            med.append(np.nan); lo.append(np.nan); hi.append(np.nan)
    ctr = .5 * (bins[:-1] + bins[1:])
    fig, ax = plt.subplots(figsize=(8.4, 4))
    ax.errorbar(ctr, med, yerr=[np.array(med) - lo, np.array(hi) - med], fmt="o-", ms=3,
                color="#0b3d91", ecolor="#999", capsize=2, lw=1)
    ax.axvspan(3, 4, color="#d95f02", alpha=.12)
    ax.set_xlabel(f"baseline [G$\\lambda$] @ {freq/1e9:.1f} GHz"); ax.set_ylabel("median |V| [Jy]")
    ax.set_title(f"{hd.get('OBJECT')} {hd.get('DATE-OBS')} — UV amplitude (archive data; no imaging)")
    ax.grid(alpha=.25)
    save(fig, f"{ev['folder']}/derived/uv_amplitude.png",
         processing="وسيط |V| لكل حزمة أساس مع نطاق 16–84%", colour="لا شيء")
    pairs = {}
    for b, v in zip(base.astype(int), V):
        a, c = b // 256, b % 256
        pairs.setdefault((a, c), []).append(v); pairs.setdefault((c, a), []).append(np.conj(v))
    ants = sorted({k[0] for k in pairs})
    cps = []
    for t in itertools.combinations(ants, 3):
        if all((x, y) in pairs for x, y in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0]))):
            z = (np.median(pairs[(t[0], t[1])]) * np.median(pairs[(t[1], t[2])])
                 * np.median(pairs[(t[2], t[0])]))
            cps.append(np.degrees(np.angle(z)))
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.hist(cps, bins=np.arange(-180, 181, 10), color="#3b3b6d")
    ax.set_xlabel("closure phase [deg]"); ax.set_ylabel("triangles")
    ax.set_title(f"{hd.get('OBJECT')} — closure phases of {len(cps)} triangles (asymmetry test)")
    ax.grid(alpha=.25)
    save(fig, f"{ev['folder']}/derived/closure_phases.png",
         processing="طور الإغلاق من وسيط المرئيات لكل مثلث", colour="لا شيء")
    img = raw(ev, "EHT_M87_official_image.fits")
    if img:
        with fits.open(img) as h:
            a = np.array(h[0].data, float)
        fig, ax = plt.subplots(figsize=(5, 4.6))
        ax.imshow(np.clip(a, np.percentile(a, 1), np.percentile(a, 99.7)),
                  origin="lower", cmap="afmhot")
        ax.set_title("Official EHT image product — colours assigned")
        ax.set_xticks([]); ax.set_yticks([])
        save(fig, f"{ev['folder']}/derived/official_image_render.png",
             processing="عرض المنتج الرسمي بمقياس لوغاريتمي", colour="afmhot مُسند")


def e05(ev):
    from astropy.io import fits
    from astropy.visualization import ZScaleInterval, LogStretch, ImageNormalize
    img = raw(ev, "HST_full_frame_flc.fits")
    if img:
        with fits.open(img, memmap=True) as h:
            sci = next((x for x in h if x.name == "SCI" and x.data is not None), h[0])
            d = np.array(sci.data, dtype="float32")
            hd = h[0].header
            filt = hd.get("FILTER") or hd.get("FILTER1")
        if d.ndim == 3:
            d = d[0]
        norm = ImageNormalize(d, interval=ZScaleInterval(), stretch=LogStretch())
        fig, ax = plt.subplots(figsize=(6.4, 5.4))
        ax.imshow(d, origin="lower", cmap="gray", norm=norm)
        ax.set_title(f"HST {hd.get('INSTRUME')}/{hd.get('DETECTOR')} {filt}  {hd.get('DATE-OBS')}\n"
                     "full frame, log stretch — colours assigned")
        ax.set_xticks([]); ax.set_yticks([])
        save(fig, f"{ev['folder']}/derived/hst_full_frame.png",
             processing="ZScale + LogStretch، الإطار الكامل بلا قص", colour="gray مُسند",
             instrument=hd.get("INSTRUME"), date=hd.get("DATE-OBS"), proposid=hd.get("PROPOSID"))
    sp = raw(ev, "gd153_stis_x1d.fits")
    if sp:
        with fits.open(sp) as h:
            t = h[1].data if len(h) > 1 else h[0].data
            cols = getattr(t, "names", [])
            wl = t["WAVELENGTH"] if "WAVELENGTH" in cols else t[cols[0]]
            fl = t["FLUX"] if "FLUX" in cols else t[cols[1]]
            hd = h[0].header
        fig, ax = plt.subplots(figsize=(9, 3.8))
        ax.plot(wl, fl, lw=.6, color="#111")
        ax.set_yscale("log"); ax.set_xlabel("wavelength [Å]"); ax.set_ylabel("flux")
        ax.set_title(f"HST/{hd.get('INSTRUME')} spectrum of {hd.get('TARGNAME')} — PROPOSID "
                     f"{hd.get('PROPOSID')} — {hd.get('DATE-OBS')}")
        ax.grid(alpha=.25)
        save(fig, f"{ev['folder']}/derived/stis_spectrum.png",
             processing="رسم الطيف المرصود كما هو (بلا تصحيح)", colour="لا شيء",
             proposid=hd.get("PROPOSID"), date=hd.get("DATE-OBS"))


def e06(ev):
    from astropy.io import fits
    p = raw(ev, "AIA171_fullframe.fits")
    if p:
        with fits.open(p) as h:
            d = np.array(h[0].data, float)
            hd = h[0].header
        fig, ax = plt.subplots(figsize=(5.6, 5))
        ax.imshow(np.clip(d, 0, None), origin="lower", cmap="inferno",
                  vmax=np.percentile(d, 99.5))
        ax.set_title(f"SDO/AIA {hd.get('WAVE_STR')} {hd.get('T_OBS')}\n"
                     f"{d.shape[1]}×{d.shape[0]} level-1 — assigned colour")
        ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(plt.cm.ScalarMappable(cmap="inferno",
                                           norm=plt.Normalize(0, np.percentile(d, 99.5))),
                     ax=ax, shrink=.8, label="DN")
        save(fig, f"{ev['folder']}/derived/aia171_frame.png",
             processing="عرض الإطار الكامل بمقياس خطي مُشبَع عند 99.5%", colour="inferno مُسند",
             date=hd.get("T_OBS"), instrument=hd.get("INSTRUME"))


def e07(ev):
    from obspy import read
    p = raw(ev, "IRIS_multi_station.mseed")
    if not p:
        return
    st = read(str(p))
    fs = float(st[0].stats.sampling_rate)
    for tr in st[:6]:
        fig, ax = plt.subplots(figsize=(9, 3))
        t = np.arange(tr.stats.npts) / tr.stats.sampling_rate
        ax.plot(t, tr.data, lw=.4, color="#08306b")
        ax.set_xlabel("seconds from record start"); ax.set_ylabel(tr.id)
        ax.set_title(f"IRIS DMC — {tr.id} — {tr.stats.starttime} (real seismogram)")
        ax.grid(alpha=.25)
        save(fig, f"{ev['folder']}/derived/waveform_{tr.id.replace('.', '_')}.png",
             processing="سجل زلزالي كما هو", colour="لا شيء", station=tr.id)
    tr = st[0]
    from scipy import signal
    f, tt, S = signal.spectrogram(tr.data.astype(float), fs=tr.stats.sampling_rate,
                                  nperseg=1024, noverlap=512)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.pcolormesh(tt / 60, f, 10 * np.log10(S + 1e-12), shading="auto", cmap="magma")
    ax.set_ylim(0, min(20, f.max())); ax.set_xlabel("minutes"); ax.set_ylabel("Hz")
    ax.set_title(f"spectrogram {tr.id} — colours assigned")
    save(fig, f"{ev['folder']}/derived/spectrogram_{tr.id.replace('.', '_')}.png",
         processing="STFT 1024/512", colour="magma مُسند")
    savewav(f"{ev['folder']}/derived/audio/{tr.id.replace('.', '_')}_sonification.wav",
            tr.data, 4000, "صوتنة السجل الزلزالي: تصغير 40→4000 Hz (تحويل صوتي مُعلن)")


def e08(ev):
    import uproot
    p = raw(ev, "CMS_Run2012C_DoubleMuParked_AOD.root")
    if not p:
        return
    f = uproot.open(str(p))
    trees = [k for k, v in f.items() if hasattr(v, "arrays")]
    if not trees:
        return
    tree = f[trees[0]]
    branches = list(tree.keys())
    png = 0
    if any("Muon" in b for b in branches):
        pt = tree["Muon_pt"].array(library="np")
        flat = np.concatenate([np.asarray(x) for x in pt if len(x)]) if len(pt) else np.array([])
        if flat.size:
            fig, ax = plt.subplots(figsize=(7.6, 3.6))
            ax.hist(flat, bins=80, color="#67000d", histtype="step", lw=1.2)
            ax.set_xlabel("muon $p_T$ [GeV]"); ax.set_ylabel("muons")
            ax.set_title(f"CMS Open Data 2012 AOD — muon pT from {os.path.basename(p)}")
            save(fig, f"{ev['folder']}/derived/muon_pt.png",
                 processing="حساب من فروع AOD مباشرة", colour="لا شيء")
            png += 1
    json_log = dict(file=os.path.basename(p), branches=branches[:30],
                    events=int(getattr(tree, "num_entries", 0)))
    (ROOT / ev["folder"] / "derived" / "aod_summary.json").write_text(
        json.dumps(json_log, ensure_ascii=False, indent=1), encoding="utf-8")


def e09(ev):
    import nibabel as nib
    for name, tag in (("sub-01_T1w.nii.gz", "T1w"),
                      ("sub-01_task-balloonanalogrisktask_run-01_bold.nii.gz", "BOLD")):
        p = raw(ev, name)
        if not p:
            continue
        img = nib.load(str(p))
        d = np.asanyarray(img.dataobj)
        if d.ndim == 4:
            d = d[..., :1].mean(axis=3)
        z = d.shape[2] // 2
        fig, axes = plt.subplots(1, 3, figsize=(9, 3.2))
        for ax, (sl, lab) in zip(axes, [(d[:, :, z], "axial"),
                                        (d[d.shape[0] // 2, :, :].T, "coronal"),
                                        (d[:, d.shape[1] // 2, :].T, "sagittal")]):
            ax.imshow(np.rot90(sl), cmap="gray", origin="lower")
            ax.set_title(lab); ax.set_xticks([]); ax.set_yticks([])
        fig.suptitle(f"{tag} — {p.name} — colours assigned (grayscale)", fontsize=9)
        save(fig, f"{ev['folder']}/derived/{tag}_slices.png",
             processing="شرائح متعامدة عند المنتصف", colour="gray مُسند")


def e10(ev):
    from astropy.io import fits
    from astropy.visualization import ZScaleInterval, AsinhStretch, ImageNormalize
    p = raw(ev, "JWST_SMACS0723_i2d.fits")
    if not p:
        return
    with fits.open(p, memmap=True) as h:
        d = np.array(h[1].data if len(h) > 1 and h[1].data is not None else h[0].data, float)
        hd = h[0].header
    norm = ImageNormalize(d[np.isfinite(d)], interval=ZScaleInterval(), stretch=AsinhStretch())
    fig, ax = plt.subplots(figsize=(6, 5.4))
    ax.imshow(d, origin="lower", cmap="magma", norm=norm)
    ax.set_title(f"JWST {hd.get('INSTRUME')} {hd.get('FILTER')} — {hd.get('DATE-OBS')}\n"
                 "single channel — colour assigned")
    ax.set_xticks([]); ax.set_yticks([])
    save(fig, f"{ev['folder']}/derived/smacs0723.png",
         processing="ZScale + Asinh على قناة واحدة", colour="magma مُسند",
         date=hd.get("DATE-OBS"), filter=hd.get("FILTER"))


HANDLERS = dict(E01=e01, E02=e02, E03=eht, E04=eht, E05=e05,
                E06=e06, E07=e07, E08=e08, E09=e09, E10=e10)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--event")
    a = ap.parse_args(argv)
    ids = [s.strip().upper() for s in (a.event or "").split(",") if s.strip()]
    todo = [BY_ID[i] for i in ids] if ids else (EVENTS if a.all else EVENTS)
    for ev in todo:
        print(f"== {ev['id']} {ev['title']}")
        try:
            HANDLERS[ev["id"]](ev)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {type(e).__name__}: {e}")
    print(f"derived files: {len(DERIVED)}")


if __name__ == "__main__":
    main()
