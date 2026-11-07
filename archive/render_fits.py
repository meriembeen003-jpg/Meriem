"""Render calibrated astronomical FITS products into publication-grade colour images.

Every product keeps its own observational footprint: no synthetic content is added,
only a perceptual (asinh / log / sinh) stretch and a false-colour palette that is
stated explicitly in the accompanying caption.
"""
import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from astropy.io import fits  # noqa: E402
from astropy.wcs import WCS  # noqa: E402
from astropy.visualization import ZScaleInterval  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "final")

INK = {"thermal": ["#000004", "#3b0f70", "#8c2981", "#de4968", "#fe9f6d", "#fcfdbf"],
       "xray": ["#04040f", "#1c2b63", "#2f7ab8", "#7fd4e3", "#f7f0c0", "#ffffff"],
       "gamma": ["#02030c", "#16305c", "#5d2f8f", "#c94b8b", "#f6b06a", "#fff8d6"],
       "radio": ["#000000", "#2b1055", "#7b2d8e", "#e0559c", "#ffb75e", "#fffdf0"],
       "uv": ["#05010d", "#2a1361", "#7b2ea0", "#e0448b", "#ffb06b", "#fffbe8"],
       "hi": ["#000000", "#0b1d51", "#2b6cb0", "#7fd3e0", "#f2f2c8", "#ffffff"]}


def cmap(name):
    return LinearSegmentedColormap.from_list(name, INK[name])


def stretch(data, lo=0.5, hi=99.85, mode="asinh", clip=None):
    """Normalise to 0-1 with a robust stretch. `clip` sets the value mapped to
    white when the dynamic range is dominated by a single bright core."""
    d = np.asarray(data, dtype=float)
    d = np.where(np.isfinite(d), d, np.nan)
    good = d[np.isfinite(d)]
    if good.size == 0:
        return None
    med = np.nanmedian(good)
    d = d - med
    if mode == "asinh":
        out = np.arcsinh(d / max(3.0 * np.nanstd(good), 1e-30))
    else:
        out = np.log10(np.clip(d, 1e-30, None))
    vlo, vhi = np.nanpercentile(out, [lo, hi])
    out = (out - vlo) / (vhi - vlo)
    if clip is not None:
        out = out / clip
    return np.clip(out, 0, 1)


def save(fig, name, dpi=300, face="#000000"):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, facecolor=face, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print("wrote", path)


def figsize(shape, base=9.0):
    shp = getattr(shape, "shape", shape)
    h, w = int(shp[0]), int(shp[1])
    return (base, base * h / float(w))


# ---------------------------------------------------------------- radio (MeerKAT)
def meerkat():
    f = os.path.join(RAW, "NGC1044-MeerKAT-data-products", "L_7arc-StokesI-MFS-image.fits")
    with fits.open(f) as h:
        d = np.squeeze(h[0].data).astype(float)
        hd = h[0].header
    floor = 3 * 0.00042            # 3 sigma of the published image rms
    img = np.clip((np.log10(np.clip(d, floor, None)) - np.log10(floor)) /
                  (np.log10(0.02) - np.log10(floor)), 0, 1)
    fig, ax = plt.subplots(figsize=figsize(img, 9))
    ax.imshow(img, cmap=cmap("radio"), origin="lower")
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    save(fig, "09_NGC1044_MeerKAT_Lband_radio.png")
    return hd


# ---------------------------------------------------------------- X-ray (Chandra ACIS)
def chandra():
    f = os.path.join(RAW, "astropy-data", "chandra_events.fits")
    with fits.open(f) as h:
        ev = h["EVENTS"].data
        x, y, e = ev["x"], ev["y"], ev["energy"]
        keep = (e > 500) & (e < 8000)
        x, y = x[keep], y[keep]
        hd = h[0].header
    # 1" bins, then a light Gaussian smoothing for display only
    bins = (int((y.max() - y.min()) / 4.0), int((x.max() - x.min()) / 4.0))
    img, _, _ = np.histogram2d(y, x, bins=bins)
    from scipy.ndimage import gaussian_filter  # noqa: E402

    img = gaussian_filter(img.astype(float), 1.2)
    st = stretch(img, 15, 99.95, "asinh")
    st = np.clip(st / 0.35, 0, 1)
    fig, ax = plt.subplots(figsize=figsize(st, 8))
    ax.imshow(st, cmap=cmap("xray"), origin="lower", interpolation="nearest")
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    save(fig, "10_HCG62_Chandra_ACIS_xray.png")
    return hd, len(x)


# ---------------------------------------------------------------- sub-mm (Herschel SPIRE)
def herschel():
    f = os.path.join(RAW, "astropy-data", "herschel-350.fits.gz")
    with fits.open(f) as h:
        d = h[1].data.astype(float)
        hd = h[1].header
    lo_v, hi_v = 0.1, 15.0
    st = np.clip((np.arcsinh(d / 0.6) - np.arcsinh(lo_v / 0.6)) /
                 (np.arcsinh(hi_v / 0.6) - np.arcsinh(lo_v / 0.6)), 0, 1)
    fig, ax = plt.subplots(figsize=figsize(st, 8))
    ax.imshow(st, cmap=cmap("thermal"), origin="lower")
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    save(fig, "13_Herschel_SPIRE_350um_submm.png")
    return hd


# ---------------------------------------------------------------- gamma (Fermi-LAT)
def fermi():
    f = os.path.join(RAW, "gammapy-data", "fermi_3fhl_events_selected.fits.gz")
    with fits.open(f) as h:
        ev = h["EVENTS"].data
        ra, dec, en = ev["RA"], ev["DEC"], ev["ENERGY"]
        zen = ev["ZENITH_ANGLE"]
    keep = zen < 100
    ra, dec, en = ra[keep], dec[keep], en[keep]
    # equal-area count map: 2 deg pixels
    rab = np.arange(0, 361, 1.0)
    decb = np.arange(-90, 91, 1.0)
    img, _, _ = np.histogram2d(dec, ra, bins=[decb, rab])
    from scipy.ndimage import gaussian_filter  # noqa: E402

    img = gaussian_filter(img.astype(float), 1.5)
    st = np.clip(stretch(img, 30, 99.8, "log") / 0.45, 0, 1)
    fig = plt.figure(figsize=(16, 8.6))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(st, cmap=cmap("gamma"), aspect="auto", origin="lower",
              extent=[0, 360, -90, 90])
    ax.set_axis_off()
    save(fig, "15_FermiLAT_gamma_ray_sky_map.png")
    return len(ra)


# ---------------------------------------------------------------- HI 21 cm cube (HI4PI)
def hi_cube():
    f = os.path.join(RAW, "astropy-data", "reduced_TAN_C14.fits")
    with fits.open(f) as h:
        cube = h[0].data.astype(float)
        hd = h[0].header
    # channel map at the local-standard-of-rest velocity slice nearest v=0
    v3 = hd["CRVAL3"] + (np.arange(cube.shape[0]) - (hd.get("CRPIX3", 1) - 1)) * hd["CDELT3"]
    idx = int(np.argmin(np.abs(v3 - 0)))
    sl = cube[idx]
    st = stretch(sl, 25, 99.0, "asinh")
    st = np.where(np.isfinite(sl), np.nan_to_num(st), np.nan)
    fig, ax = plt.subplots(figsize=figsize(st, 7))
    ax.imshow(st, cmap=cmap("hi"), origin="lower", interpolation="nearest")
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    save(fig, "14_HI4PI_21cm_channelmap.png")
    return hd, float(v3[idx])


# ---------------------------------------------------------------- CMB (Planck)
def planck():
    import glob

    files = sorted(glob.glob(os.path.join(RAW, "planck_cmb_cubemaps", "*_cmb_planck_1024.png")))
    return files


# ---------------------------------------------------------------- solar (SDO/AIA, SOHO/EIT)
def solar():
    out = []
    for f, cm, name, lo, hi in [
        (os.path.join(RAW, "sunpy", "aia_171_level1.fits"), "uv", "12_SDO_AIA_171A_corona.png", 5, 99.9),
        (os.path.join(RAW, "sunpy", "efz20040301.000010_s.fits"), "thermal", "11_SOHO_EIT_195A_corona.png", 5, 99.9),
    ]:
        with fits.open(f) as h:
            d = h[0].data.astype(float)
            hd = h[0].header
        st = stretch(d, lo, hi, "asinh")
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.imshow(st, cmap=cmap(cm), origin="lower")
        ax.set_axis_off()
        fig.subplots_adjust(0, 0, 1, 1)
        save(fig, name)
        out.append(hd)
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    hd = meerkat()
    print("MeerKAT CRVAL", hd["CRVAL1"], hd["CRVAL2"], hd["CRVAL3"] / 1e9, "GHz")
    hd, n = chandra()
    print("Chandra photons", n)
    hd = herschel()
    print("Herschel wcs", hd["CRVAL1"], hd["CRVAL2"], hd["CDELT1"] * 3600)
    n = fermi()
    print("Fermi photons", n)
    hd, v = hi_cube()
    print("HI slice v", v)
    solar()
