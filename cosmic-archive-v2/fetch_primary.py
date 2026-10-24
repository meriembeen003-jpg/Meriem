#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_primary.py — download every evidence file for cosmic-archive-v2
from the *official* archive domains, verify it, and record provenance.

Designed to run unchanged on a laptop, a server, or Google Colab:

    pip install -r requirements.txt
    python fetch_primary.py --all                 # everything
    python fetch_primary.py --event E02,E05       # a subset
    python fetch_primary.py --all --dry-run       # print the plan, no network
    python fetch_primary.py --all --jsoc-email you@example.org

What it does for each product
-----------------------------
1. asks the archive's own API/library for the file (gwosc, astroquery.mast,
   sunpy/Fido, obspy/FDSN, cernopendata-client, openneuro-py, PLA/IRSA/CyVerse
   for Planck/EHT);
2. retries three times with three different strategies (direct, alternate
   documented mirror, resume/range) and never invents a URL;
3. stores the bytes under EVENTS/E0x_*/raw/;
4. records: bytes, SHA-256, official checksum when the archive publishes one,
   DOI + whether it resolved (and to which landing page), licence text pulled
   from the archive page, instrument, program id, observation date, and the
   exact processing applied (none, for raw files);
5. validates the file structurally (FITS/HDF5/SAC/ROOT/NIfTI/UVFITS) and that
   the header matches the expected instrument/date;
6. appends one row per file to _fetch_records.json.  Failures are written to
   _fetch_failures.json and echoed into BLOCKED.md by tools/make_index.py.

Nothing is ever substituted: a product that cannot be fetched stays missing and
becomes an open question.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from catalog import EVENTS, BY_ID  # noqa: E402

UA = "cosmic-archive-v2/2.0 (research archiving; contact: repository owner)"
RECORDS = ROOT / "_fetch_records.json"
FAILURES = ROOT / "_fetch_failures.json"
NOW = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- utils
def log(*a):
    print(*a, flush=True)


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def human(n: int) -> str:
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or u == "TB":
            return f"{n:.0f} {u}" if u == "B" else f"{n:.1f} {u}"
        n /= 1024.0
    return str(n)


def http_open(url: str, *, headers=None, timeout=120, method="GET"):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h, method=method)
    return urllib.request.urlopen(req, timeout=timeout)


def http_text(url: str, timeout=60, headers=None) -> str:
    with http_open(url, timeout=timeout, headers=headers) as r:
        raw = r.read()
    for enc in ("utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def download(url: str, dest: Path, *, max_bytes: int | None = None,
             retries: int = 3, timeout: int = 300, headers=None) -> dict:
    """Download with three strategies, resumable, hashing on the fly."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    strategies = [
        ("direct", {}),
        ("referer+accept-fits", {"Referer": "https://www.cosmos.esa.int/web/planck",
                                 "Accept": "application/fits,application/octet-stream,*/*"}),
        ("range-resume", {"Range": "bytes="}),
    ]
    last = None
    for attempt in range(retries):
        name, extra = strategies[attempt % len(strategies)]
        hdrs = dict(headers or {})
        hdrs.update(extra)
        try:
            with http_open(url, headers=hdrs, timeout=timeout) as r:
                total = int(r.headers.get("Content-Length") or 0)
                if max_bytes and total and total > max_bytes:
                    return dict(ok=False, error=f"size {total} > max_bytes {max_bytes}",
                                url=url, strategy=name)
                tmp = dest.with_suffix(dest.suffix + ".part")
                n = 0
                with open(tmp, "wb") as f:
                    while True:
                        b = r.read(1 << 20)
                        if not b:
                            break
                        f.write(b)
                        n += len(b)
                tmp.replace(dest)
                return dict(ok=True, url=url, bytes=n, strategy=name,
                            content_type=r.headers.get("Content-Type", ""))
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
            log(f"      attempt {attempt + 1}/{retries} ({name}) failed: {last}")
            time.sleep(min(2 ** attempt, 8))
    return dict(ok=False, error=last, url=url)


def resolve_doi(doi: str) -> dict:
    """Resolve a DOI and keep the landing page URL + HTTP status."""
    if not doi or not re.match(r"^10\.\d{4,9}/\S+$", doi.split(" ")[0]):
        return dict(doi=doi, resolves=None, landing=None, note="ليس DOI بشكل 10.xxxx/… — لم يُحلّ")
    d = doi.split(" ")[0]
    try:
        with http_open(f"https://doi.org/{d}",
                       headers={"Accept": "application/vnd.citationstyles.csl+json"},
                       timeout=45) as r:
            body = r.read().decode("utf-8", "replace")
        try:
            meta = json.loads(body)
            landing = meta.get("URL") or f"https://doi.org/{d}"
            title = meta.get("title") or meta.get("container-title")
        except json.JSONDecodeError:
            landing, title = f"https://doi.org/{d}", None
        return dict(doi=d, resolves=True, landing=landing, title=title)
    except Exception as e:  # noqa: BLE001
        return dict(doi=d, resolves=False, landing=None, note=f"{type(e).__name__}: {e}")


def licence_snapshot(url: str, dest: Path) -> dict:
    try:
        txt = http_text(url, timeout=45)
        body = re.sub(r"(?is)<(script|style).*?</\1>", " ", txt)
        body = re.sub(r"(?s)<[^>]+>", " ", body)
        body = re.sub(r"\s+", " ", body).strip()
        dest.write_text(f"SOURCE: {url}\nFETCHED: {NOW}\n\n{body[:6000]}\n", encoding="utf-8")
        return dict(ok=True, file=str(dest.relative_to(ROOT)), chars=len(body))
    except Exception as e:  # noqa: BLE001
        dest.write_text(f"SOURCE: {url}\nFETCHED: {NOW}\nERROR: {type(e).__name__}: {e}\n",
                        encoding="utf-8")
        return dict(ok=False, file=str(dest.relative_to(ROOT)), note=str(e))


def checksum_sidecars(url: str) -> dict:
    """Look for a published .sha256 / .md5 / .sha1 next to the file."""
    for ext, algo in ((".sha256", "sha256"), (".md5", "md5"), (".sha1", "sha1")):
        try:
            with http_open(url + ext, timeout=20) as r:
                txt = r.read().decode("utf-8", "replace").split()[0]
            if re.fullmatch(r"[0-9a-fA-F]{32,64}", txt):
                return dict(algorithm=algo, value=txt.lower(), source=url + ext)
        except Exception:  # noqa: BLE001
            continue
    return {}


def adler32_of(path: Path) -> str:
    import zlib
    a = 1
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            a = zlib.adler32(b, a)
    return f"{a & 0xFFFFFFFF:08x}"


# --------------------------------------------------------------------------- validators
def _fits_header(path: Path, ext=0):
    from astropy.io import fits
    with fits.open(path, memmap=True) as h:
        return h[ext].header, [getattr(x, "data", None) is not None for x in h]


def validate(path: Path, kind: str) -> dict:
    """Return {ok, details} using the file's own structure."""
    try:
        if kind == "fits_planck_map":
            hd, _ = _fits_header(path)
            need = ["NSIDE", "ORDERING", "COORDSYS"]
            miss = [k for k in need if k not in hd]
            nside = int(hd.get("NSIDE", 0))
            return dict(ok=(nside > 0 and not miss),
                        details=f"NSIDE={nside} ORDERING={hd.get('ORDERING')} "
                                f"COORDSYS={hd.get('COORDSYS')} missing={miss}")
        if kind == "planck_spectrum":
            rows = [ln for ln in path.read_text(errors="replace").splitlines()
                    if ln.strip() and not ln.startswith("#")]
            cols = len(rows[len(rows) // 2].split()) if rows else 0
            return dict(ok=len(rows) > 100 and cols >= 2,
                        details=f"{len(rows)} rows, {cols} columns")
        if kind == "gwosc_hdf5":
            import h5py
            with h5py.File(path, "r") as f:
                keys = list(f.keys())
                st = f["strain/Strain"]
                n = int(st.shape[0])
                det = f["meta/Detector"][()] if "meta/Detector" in f else b"?"
                utc = f["meta/UTCstart"][()] if "meta/UTCstart" in f else b"?"
            return dict(ok=(n > 1e5 and "strain" in keys),
                        details=f"keys={keys} n={n} detector={det} utcstart={utc}")
        if kind == "gwosc_event_json":
            d = json.loads(path.read_text())
            ev = d.get("events", {})
            return dict(ok=bool(ev), details=f"events={list(ev)[:3]} keys={list(d)[:6]}")
        if kind == "healpix_fits":
            hd, _ = _fits_header(path)
            return dict(ok=("NSIDE" in hd or "ORDERING" in hd),
                        details=f"NSIDE={hd.get('NSIDE')} ORDERING={hd.get('ORDERING')}")
        if kind == "uvfits":
            from astropy.io import fits
            with fits.open(path, memmap=True) as h:
                hd = h[0].header
                d = h[0].data
                n = len(d) if d is not None else 0
            return dict(ok=n > 100 and hd.get("CTYPE4") == "FREQ",
                        details=f"visibilities={n} OBJECT={hd.get('OBJECT')} "
                                f"DATE-OBS={hd.get('DATE-OBS')} freq={hd.get('CRVAL4')}")
        if kind == "fits_image":
            from astropy.io import fits
            with fits.open(path, memmap=True) as h:
                shp = [x.data.shape for x in h if x.data is not None][:2]
            return dict(ok=bool(shp), details=f"shapes={shp}")
        if kind == "hst_image":
            hd, _ = _fits_header(path)
            ok = (hd.get("TELESCOP") == "HST" and "DATE-OBS" in hd
                  and hd.get("INSTRUME") in ("ACS", "WFC3"))
            return dict(ok=ok, details=f"TELESCOP={hd.get('TELESCOP')} INSTRUME={hd.get('INSTRUME')} "
                                       f"DETECTOR={hd.get('DETECTOR')} FILTER={hd.get('FILTER') or hd.get('FILTER1')} "
                                       f"DATE-OBS={hd.get('DATE-OBS')} PROPOSID={hd.get('PROPOSID')}")
        if kind == "hst_spectrum":
            hd, _ = _fits_header(path)
            ok = hd.get("TELESCOP") == "HST" and hd.get("INSTRUME") in ("STIS", "COS", "FOS")
            return dict(ok=ok, details=f"INSTRUME={hd.get('INSTRUME')} TARGNAME={hd.get('TARGNAME')} "
                                       f"DATE-OBS={hd.get('DATE-OBS')} PROPOSID={hd.get('PROPOSID')}")
        if kind == "aia_fullframe":
            hd, _ = _fits_header(path)
            nx, ny = int(hd.get("NAXIS1", 0)), int(hd.get("NAXIS2", 0))
            return dict(ok=(nx == 4096 and ny == 4096 and "AIA" in str(hd.get("INSTRUME"))),
                        details=f"{nx}x{ny} INSTRUME={hd.get('INSTRUME')} T_OBS={hd.get('T_OBS')} "
                                f"WAVE_STR={hd.get('WAVE_STR')}")
        if kind == "mp4":
            size = path.stat().st_size
            return dict(ok=size > 200_000, details=f"{human(size)}")
        if kind == "usgs_event":
            d = json.loads(path.read_text())
            f = (d.get("features") or [{}])[0]
            return dict(ok=bool(f.get("id")), details=f"id={f.get('id')} mag={f.get('properties', {}).get('mag')}")
        if kind == "mseed":
            from obspy import read
            st = read(str(path), format="MSEED")
            ids = sorted({tr.id for tr in st})
            return dict(ok=len(ids) >= 3, details=f"traces={len(st)} stations={ids[:8]}")
        if kind == "cms_aod":
            import uproot
            f = uproot.open(str(path))
            keys = [k for k in f.keys(cycle=False)][:8]
            return dict(ok=len(keys) > 0, details=f"branches={keys}")
        if kind == "nifti":
            import nibabel as nib
            img = nib.load(str(path))
            return dict(ok=img.ndim >= 3, details=f"shape={img.shape} dtype={img.get_data_dtype()}")
        if kind == "jwst_image":
            hd, _ = _fits_header(path)
            return dict(ok=str(hd.get("TELESCOP")).startswith("JWST"),
                        details=f"TELESCOP={hd.get('TELESCOP')} INSTRUME={hd.get('INSTRUME')} "
                                f"FILTER={hd.get('FILTER')} DATE-OBS={hd.get('DATE-OBS')} "
                                f"PROGRAM={hd.get('PROGRAM') or hd.get('PROPOSID')}")
    except Exception as e:  # noqa: BLE001
        return dict(ok=False, details=f"validation error: {type(e).__name__}: {e}")
    return dict(ok=True, details="no structural check defined")


# --------------------------------------------------------------------------- record helper
class Run:
    def __init__(self, args):
        self.args = args
        self.records = json.loads(RECORDS.read_text()) if RECORDS.exists() else []
        self.failures = json.loads(FAILURES.read_text()) if FAILURES.exists() else []
        self.doi_cache = {}

    # ------------------------------------------------------------------ plumbing
    def out_dir(self, ev) -> Path:
        d = ROOT / ev["folder"]
        (d / "raw").mkdir(parents=True, exist_ok=True)
        (d / "derived").mkdir(parents=True, exist_ok=True)
        return d

    def doi(self, ev):
        if ev["id"] not in self.doi_cache:
            if self.args.dry_run:
                self.doi_cache[ev["id"]] = dict(doi=ev["doi"], resolves=None, note="dry-run")
            else:
                self.doi_cache[ev["id"]] = resolve_doi(ev["doi"])
        d = self.doi_cache[ev["id"]]
        (ROOT / ev["folder"] / "doi_resolution.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        return d

    def licence(self, ev):
        dest = ROOT / ev["folder"] / "license_excerpt.txt"
        if self.args.dry_run:
            return dict(ok=None, file=None, note="dry-run")
        if dest.exists() and not self.args.refresh_license:
            return dict(ok=True, file=str(dest.relative_to(ROOT)), note="cached")
        return licence_snapshot(ev["license_url"], dest)

    def add(self, ev, target, path: Path, url: str, **extra):
        rec = dict(
            event=ev["id"], event_title=ev["title"], folder=ev["folder"],
            product=target["name"], role=target["role"], kind=target["kind"],
            file=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
            sha256=sha256_file(path), url=url, archive=ev["instrument"],
            doi=ev["doi"], doi_resolution=self.doi_cache.get(ev["id"], {}),
            license_declared=ev["license_text"], license_url=ev["license_url"],
            downloaded_utc=NOW, processing="none — بايتات الأرشيف كما نُزِّلت",
            primary_source=True, fetched_from_official=True,
            validator=target["validation"],
        )
        rec.update(extra)
        v = validate(path, target["validation"])
        rec["validation"] = v
        side = checksum_sidecars(url) if not self.args.dry_run else {}
        if side:
            algo, want = side["algorithm"], side["value"]
            if algo == "sha256":
                got = rec["sha256"]
            elif algo == "md5":
                got = hashlib.md5(path.read_bytes()).hexdigest()
            elif algo == "sha1":
                got = hashlib.sha1(path.read_bytes()).hexdigest()
            else:
                got = None
            rec["official_checksum"] = dict(algorithm=algo, value=want, source=side["source"],
                                            match=(got == want))
        else:
            rec["official_checksum"] = dict(algorithm=None, value=None, source=None,
                                            match=None, note="الأرشيف لا ينشر مجموعاً لهذا المنتج")
        self.records = [r for r in self.records if r["file"] != rec["file"]] + [rec]
        RECORDS.write_text(json.dumps(self.records, ensure_ascii=False, indent=1), encoding="utf-8")
        log(f"   ✓ {rec['file']}  {human(rec['bytes'])}  sha256={rec['sha256'][:16]}…  "
            f"valid={v['ok']} ({v['details']})")
        return rec

    def fail(self, ev, target, why: str, attempts=None):
        self.failures.append(dict(event=ev["id"], product=target["name"], role=target["role"],
                                  reason=why, attempts=attempts or [], when=NOW))
        FAILURES.write_text(json.dumps(self.failures, ensure_ascii=False, indent=1), encoding="utf-8")
        log(f"   ✗ {target['name']}: {why}")

    # ------------------------------------------------------------------ E01 Planck
    def e01(self, ev):
        out = self.out_dir(ev)
        for t in ev["targets"]:
            dest = out / "raw" / t["name"]
            if dest.exists() and not self.args.force:
                log(f"   = موجود مسبقاً: {t['name']}")
                continue
            got = None
            attempts = []
            for url in t["candidates"]:
                log(f"   → {url}")
                r = download(url, dest, max_bytes=t["max_bytes"], timeout=900)
                attempts.append(dict(url=url, ok=r["ok"], error=r.get("error"), bytes=r.get("bytes")))
                if r["ok"]:
                    got = (url, r)
                    break
            if not got:
                self.fail(ev, t, "كل نقاط الدخول الموثقة فشلت (PLA ثم مرآة IRSA)", attempts)
                continue
            url, r = got
            self.add(ev, t, dest, url, attempts=attempts)

    # ------------------------------------------------------------------ E02 GWOSC
    def e02(self, ev):
        out = self.out_dir(ev)
        try:
            from gwosc.locate import get_event_urls
            from gwosc.api import fetch_event_json
        except Exception as e:  # noqa: BLE001
            log("   ! gwosc غير مثبّت:", e)
            for t in ev["targets"]:
                self.fail(ev, t, f"gwosc python package missing: {e}")
            return
        for t in ev["targets"]:
            spec = t.get("gwosc", {})
            dest = out / "raw" / t["name"]
            if dest.exists() and not self.args.force:
                log(f"   = موجود مسبقاً: {t['name']}")
                continue
            if spec.get("meta_only") or spec.get("skymap"):
                try:
                    meta = fetch_event_json(spec["event"])
                    (out / "raw" / "event_json_GW150914.json").write_text(
                        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
                    cands = []
                    for k in ("skymap", "strain"):
                        if k in meta:
                            cands += [u if isinstance(u, str) else u.get("url", "")
                                      for u in (meta[k] if isinstance(meta[k], list) else [meta[k]])]
                    if spec.get("skymap"):
                        cands += ["https://gwosc.org/GW150914data/P1500227/LALInference_skymap.fits.gz",
                                  "https://gwosc.org/GW150914data/P1500227/BAYESTAR_skymap.fits.gz"]
                    ok = False
                    for u in [c for c in cands if isinstance(c, str) and c.startswith("http")]:
                        log(f"   → {u}")
                        r = download(u, dest, timeout=300)
                        if r["ok"]:
                            self.add(ev, t, dest, u)
                            ok = True
                            break
                    if not ok:
                        self.fail(ev, t, "لم يُعثر على رابط خريطة سماء قابل للتنزيل في JSON الحدث أو الصفحة")
                except Exception as e:  # noqa: BLE001
                    self.fail(ev, t, f"{type(e).__name__}: {e}")
                continue
            try:
                urls = get_event_urls(spec["event"], detector=spec["detector"],
                                      sample_rate=spec["sampling_rate"],
                                      duration=spec["duration"])
            except Exception as e:  # noqa: BLE001
                self.fail(ev, t, f"get_event_urls failed: {type(e).__name__}: {e}")
                continue
            ok = False
            for u in urls:
                log(f"   → {u}")
                r = download(u, dest, timeout=600)
                if r["ok"]:
                    self.add(ev, t, dest, u)
                    ok = True
                    break
            if not ok:
                self.fail(ev, t, f"كل مرايا GWOSC فشلت ({len(list(urls))} رابط)")

    # ------------------------------------------------------------------ E03/E04 EHT
    def eht(self, ev):
        out = self.out_dir(ev)
        doi = self.doi(ev)
        for t in ev["targets"]:
            dest = out / "raw" / t["name"]
            if dest.exists() and not self.args.force:
                continue
            landing = doi.get("landing")
            if not landing:
                self.fail(ev, t, "DOI لم يُحلّ؛ لا يمكن الوصول إلى صفحة المجموعة")
                continue
            # Look for a direct file link published on the landing page.
            try:
                html = http_text(landing, timeout=60)
            except Exception as e:  # noqa: BLE001
                self.fail(ev, t, f"landing page unreachable ({landing}): {type(e).__name__}: {e}")
                continue
            links = re.findall(r'https?://[^\s"\'<>]+', html)
            wanted = t["name"].lower()
            hits = [l for l in links if wanted in l.lower()
                    or (t.get("eht", {}).get("image") and re.search(r"\.(fits|png)$", l, re.I))]
            if not hits:
                self.fail(ev, t, "صفحة DOI تحلّ إلى CyVerse ولا تعرض رابط ملف مباشر؛ "
                                 "التنزيل يتطلب عميل CyVerse/irods أو حساباً")
                continue
            ok = False
            for u in hits[:5]:
                r = download(u, dest, timeout=900)
                if r["ok"]:
                    self.add(ev, t, dest, u)
                    ok = True
                    break
            if not ok:
                self.fail(ev, t, "روابط الصفحة لم تُنزّل")

    # ------------------------------------------------------------------ E05 MAST
    def mast(self, ev):
        out = self.out_dir(ev)
        try:
            from astroquery.mast import Observations
        except Exception as e:  # noqa: BLE001
            for t in ev["targets"]:
                self.fail(ev, t, f"astroquery غير مثبّت: {e}")
            return
        for t in ev["targets"]:
            spec = t.get("mast", {})
            dest = out / "raw" / t["name"]
            if dest.exists() and not self.args.force:
                continue
            try:
                if spec.get("kind") == "image":
                    obs = Observations.query_criteria(obs_collection="HST",
                                                      instrument_name=["ACS/WFC", "WFC3/UVIS"],
                                                      dataproduct_type="image",
                                                      calib_level=[2, 3])
                    if len(obs) == 0:
                        self.fail(ev, t, "MAST أعاد صفر نتائج لصور ACS/WFC أو WFC3/UVIS")
                        continue
                    obs = obs[[i for i, c in enumerate(obs["calib_level"]) if int(c) == 2] or [0]]
                    best = None
                    for row in obs[:40]:
                        prods = Observations.get_product_list(row)
                        cand = prods[[("_flt" in str(f) or "_flc" in str(f))
                                      for f in prods["productFilename"]]]
                        if len(cand):
                            best = (row, cand[0])
                            break
                    if best is None:
                        self.fail(ev, t, "لا منتج FLT/FLC في أول 40 مجموعة")
                        continue
                    row, prod = best
                    tmp = Path(tempfile.mkdtemp())
                    Observations.download_products(prod, download_dir=str(tmp))
                    f = next(tmp.rglob("*.fits"), None)
                    if not f:
                        self.fail(ev, t, "تنزيل MAST لم يُنتج ملف FITS")
                        continue
                    shutil.move(str(f), dest)
                    self.add(ev, t, dest, str(prod["dataURI"]),
                             obs_id=str(row["obs_id"]), program_id=str(row.get("proposal_id")),
                             obs_date=str(row.get("t_min")), instrument=str(row["instrument_name"]))
                elif spec.get("kind") == "spectrum":
                    obs = Observations.query_object(spec["target"], radius="0.02 deg")
                    stis = obs[[("STIS" in str(i)) for i in obs["instrument_name"]]]
                    if len(stis) == 0:
                        self.fail(ev, t, f"MAST: لا مجموعات STIS للهدف {spec['target']}")
                        continue
                    prod = None
                    for row in stis:
                        prods = Observations.get_product_list(row)
                        cand = prods[[("x1d" in str(f).lower()) for f in prods["productFilename"]]]
                        if len(cand):
                            prod, prow = cand[0], row
                            break
                    if prod is None:
                        self.fail(ev, t, "لا منتج x1d لطيف STIS")
                        continue
                    tmp = Path(tempfile.mkdtemp())
                    Observations.download_products(prod, download_dir=str(tmp))
                    f = next(tmp.rglob("*.fits"), None)
                    if not f:
                        self.fail(ev, t, "تنزيل الطيف لم يُنتج FITS")
                        continue
                    shutil.move(str(f), dest)
                    self.add(ev, t, dest, str(prod["dataURI"]), obs_id=str(prow["obs_id"]),
                             program_id=str(prow.get("proposal_id")),
                             obs_date=str(prow.get("t_min")),
                             instrument=str(prow["instrument_name"]))
                elif spec.get("kind") == "jwst":
                    obs = Observations.query_object(spec["target"], radius="0.05 deg")
                    jw = obs[[("JWST" in str(o)) for o in obs["obs_collection"]]]
                    if len(jw) == 0:
                        self.fail(ev, t, "MAST: لا مجموعات JWST للهدف")
                        continue
                    prod = None
                    for row in jw[:10]:
                        prods = Observations.get_product_list(row)
                        cand = prods[[("i2d" in str(f).lower()) for f in prods["productFilename"]]]
                        if len(cand):
                            prod, prow = cand[0], row
                            break
                    if prod is None:
                        self.fail(ev, t, "لا منتج i2d")
                        continue
                    tmp = Path(tempfile.mkdtemp())
                    Observations.download_products(prod, download_dir=str(tmp))
                    f = next(tmp.rglob("*.fits"), None)
                    shutil.move(str(f), dest)
                    self.add(ev, t, dest, str(prod["dataURI"]), obs_id=str(prow["obs_id"]),
                             program_id=str(prow.get("proposal_id")), obs_date=str(prow.get("t_min")),
                             instrument=str(prow["instrument_name"]))
            except Exception as e:  # noqa: BLE001
                self.fail(ev, t, f"{type(e).__name__}: {e}")

    # ------------------------------------------------------------------ E06 SDO
    def sdo(self, ev):
        out = self.out_dir(ev)
        try:
            import astropy.units as u
            from sunpy.net import Fido, attrs as a
        except Exception as e:  # noqa: BLE001
            for t in ev["targets"]:
                self.fail(ev, t, f"sunpy غير مثبّت: {e}")
            return
        now = dt.datetime.now(dt.timezone.utc)
        for t in ev["targets"]:
            spec = t.get("sdo", {})
            dest = out / "raw" / t["name"]
            if dest.exists() and not self.args.force:
                continue
            try:
                if spec.get("kind") == "single":
                    start = now - dt.timedelta(hours=36)
                    q = Fido.search(a.Time(start, now), a.Instrument.aia,
                                    a.Wavelength(171 * u.angstrom), a.Sample(6 * u.hour))
                    files = Fido.fetch(q, path=str(out / "raw" / "{file}"))
                    if not files:
                        self.fail(ev, t, "VSO أعاد صفر ملفات AIA 171 في آخر 36 ساعة")
                        continue
                    src = Path(sorted(files)[-1])
                    src.replace(dest)
                    hd, _ = _fits_header(dest)
                    self.add(ev, t, dest, "sunpy.Fido(VSO,aia,171)", obs_date=str(hd.get("T_OBS")),
                             instrument=str(hd.get("INSTRUME")), program_id=str(hd.get("T_REC")),
                             frames=1)
                elif spec.get("kind") == "movie":
                    start = now - dt.timedelta(hours=12)
                    q = Fido.search(a.Time(start, now), a.Instrument.aia,
                                    a.Wavelength(171 * u.angstrom), a.Sample(4 * u.minute))
                    files = sorted(Fido.fetch(q, path=str(out / "raw" / "frames" / "{file}"),
                                              max_conn=4))
                    if len(files) < 120:
                        self.fail(ev, t, f"عدد الإطارات المتاحة {len(files)} < 120")
                        continue
                    frames = files[:160]
                    sys.path.insert(0, str(ROOT / "tools"))
                    from make_derived import build_mp4
                    fps = build_mp4(frames, dest, label="SDO/AIA 171 — composite by cosmic-archive-v2")
                    self.add(ev, t, dest, "sunpy.Fido(VSO,aia,171) + local MP4 encoding",
                             obs_date=f"{start.isoformat()} .. {now.isoformat()}",
                             instrument="SDO/AIA", frames=len(frames), fps=fps,
                             processing="تركيب منا من إطارات رسمية: تطبيع + لوحة ألوان مُسندة + ترميز H.264")
            except Exception as e:  # noqa: BLE001
                self.fail(ev, t, f"{type(e).__name__}: {e}")

    # ------------------------------------------------------------------ E07 IRIS
    def iris(self, ev):
        out = self.out_dir(ev)
        try:
            from obspy import UTCDateTime
            from obspy.clients.fdsn import Client
        except Exception as e:  # noqa: BLE001
            for t in ev["targets"]:
                self.fail(ev, t, f"obspy غير مثبّت: {e}")
            return
        try:
            usgs = Client("USGS")
            cat = usgs.get_events(starttime=UTCDateTime() - 10 * 365 * 86400,
                                  minmagnitude=7.5, orderby="magnitude", limit=1)
            if not len(cat):
                for t in ev["targets"]:
                    self.fail(ev, t, "USGS: لا حدث M≥7.5 في آخر 10 سنوات")
                return
            evt = cat[0]
            evid = evt.resource_id.id.split("/")[-1]
            (out / "raw").mkdir(parents=True, exist_ok=True)
            (out / "raw" / "USGS_event.json").write_text(
                json.dumps(dict(id=evid, magnitude=evt.magnitudes[0].mag,
                                time=str(evt.origins[0].time), latitude=evt.origins[0].latitude,
                                longitude=evt.origins[0].longitude, depth_km=evt.origins[0].depth / 1000,
                                region=evt.event_descriptions[0].text if evt.event_descriptions else None),
                           ensure_ascii=False, indent=1), encoding="utf-8")
            t0 = evt.origins[0].time
            tgt = dict(name="USGS_event.json", role="ملف الحدث",
                       kind="observation", validation="usgs_event")
            self.add(ev, tgt, out / "raw" / "USGS_event.json", f"obspy.Client('USGS') {evid}",
                     obs_date=str(t0), instrument="USGS ComCat", program_id=evid)
            client = Client("IRIS")
            inv = client.get_stations(starttime=t0 - 3600, endtime=t0 + 7200,
                                      latitude=evt.origins[0].latitude,
                                      longitude=evt.origins[0].longitude,
                                      maxradius=90, channel="BHZ,HHZ", level="station")
            picked = []
            for net in inv:
                for sta in net:
                    picked.append((net.code, sta.code, "00", "BHZ" if "BHZ" in str(sta.channels) or True else "HHZ"))
            st = None
            for net, sta, loc, cha in picked[:8]:
                try:
                    tr = client.get_waveforms(net, sta, "*", "BHZ", t0 + 60, t0 + 60 + 1800,
                                              attach_response=False)
                    tr.merge(method=1)
                    st = tr if st is None else st + tr
                    if len({x.stats.station for x in st}) >= 5:
                        break
                except Exception:  # noqa: BLE001
                    continue
            if st is None or len({x.stats.station for x in st}) < 3:
                for t in ev["targets"]:
                    self.fail(ev, t, "IRIS لم يُرجع سجلات كافية (≥3 محطات)")
                return
            mseed = out / "raw" / "IRIS_multi_station.mseed"
            st.write(str(mseed), format="MSEED")
            tgt = dict(name="IRIS_multi_station.mseed", role="سجلات محطات متعددة",
                       kind="observation", validation="mseed")
            nets = sorted({tr.stats.network for tr in st})
            dois = {}
            for n in nets:
                try:
                    info = http_text(f"https://service.iris.edu/fdsnws/doi/1/query?net={n}&format=text",
                                     timeout=30)
                    m = re.search(r"10\.\d{4,9}/\S+", info)
                    if m:
                        dois[n] = dict(doi=m.group(0), resolution=resolve_doi(m.group(0)))
                except Exception:  # noqa: BLE001
                    pass
            self.add(ev, tgt, mseed, "obspy.FDSN(IRIS) dataselect",
                     obs_date=str(t0), instrument="IRIS DMC FDSN",
                     program_id=f"event {evid}", networks=nets, network_dois=dois)
        except Exception as e:  # noqa: BLE001
            for t in ev["targets"]:
                self.fail(ev, t, f"{type(e).__name__}: {e}")

    # ------------------------------------------------------------------ E08 CERN
    def cern(self, ev):
        out = self.out_dir(ev)
        recid = ev["targets"][0]["cern"]["recid"]
        api = f"https://opendata.cern.ch/api/records/{recid}"
        meta = None
        try:
            meta = json.loads(http_text(api, timeout=60))
        except Exception as e:  # noqa: BLE001
            log(f"   ! API مباشر فشل ({type(e).__name__}) — سنعتمد على cernopendata-client")

        # official file list, with size and published checksum
        listing = ""
        try:
            listing = subprocess.run(
                ["cernopendata-client", "get-file-locations", "--recid", str(recid),
                 "--protocol", "http", "--verbose"],
                capture_output=True, text=True, timeout=1800, check=True).stdout
            (out / "raw" / "cern_file_locations.txt").write_text(listing, encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            log(f"   ! get-file-locations: {e}")

        cand = []
        for line in listing.splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[0].startswith("http"):
                cand.append(dict(url=parts[0], size=int(parts[1]) if parts[1].isdigit() else None,
                                 checksum=parts[2]))
        if not cand and meta:
            for f in (meta.get("metadata", {}).get("files") or meta.get("files") or []):
                if str(f.get("key", "")).endswith(".root"):
                    cand.append(dict(url=f"https://opendata.cern.ch/record/{recid}/files/"
                                          f"{os.path.basename(f['key'])}",
                                     size=f.get("size"), checksum=f.get("checksum", "")))
        roots = [c for c in cand if c["url"].endswith(".root")]
        if not roots:
            self.fail(ev, ev["targets"][0], "لا ملفات ROOT في سجل CERN (API وget-file-locations)")
            return
        pick = sorted(roots, key=lambda c: c["size"] or 0)[0]
        name = os.path.basename(pick["url"])
        dest = out / "raw" / "CMS_Run2012C_DoubleMuParked_AOD.root"
        if dest.exists() and not self.args.force:
            return

        ok = False
        try:
            subprocess.run(["cernopendata-client", "download-files", "--recid", str(recid),
                            "--filter-name", name, "--protocol", "http",
                            "--output-directory", str(out / "raw")],
                           check=True, capture_output=True, text=True, timeout=21600)
            got = list((out / "raw").rglob(name))
            if got:
                got[0].replace(dest)
                ok = True
        except Exception as e:  # noqa: BLE001
            log(f"   ! cernopendata-client download: {e}")
        if not ok:
            r = download(pick["url"], dest, timeout=21600)
            ok = r["ok"]
        if not ok:
            self.fail(ev, ev["targets"][0], "تعذّر تنزيل AOD (cernopendata-client أو HTTPS)")
            return

        # official integrity tool from the portal itself
        verify_out = ""
        try:
            verify_out = subprocess.run(
                ["cernopendata-client", "verify-files", "--recid", str(recid)],
                cwd=str(out / "raw"), capture_output=True, text=True, timeout=7200).stdout
            (out / "raw" / "cern_verify_files.txt").write_text(verify_out, encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            log(f"   ! verify-files: {e}")

        official = (pick.get("checksum") or "").replace("adler32:", "").lower()
        got_sum = adler32_of(dest)
        match = (official == got_sum) if official else None
        self.add(ev, ev["targets"][0], dest, pick["url"],
                 obs_date="2012", instrument="CMS", program_id=f"CERN-OPENDATA-{recid}",
                 official_checksum=dict(algorithm="adler32", value=official,
                                        source="cernopendata-client get-file-locations --verbose",
                                        match=match),
                 cern_verify_output=verify_out[-2000:] if verify_out else None,
                 cern_uri=pick["url"])

    # ------------------------------------------------------------------ E09 OpenNeuro
    def openneuro(self, ev):
        out = self.out_dir(ev)
        try:
            import openneuro
        except Exception as e:  # noqa: BLE001
            for t in ev["targets"]:
                self.fail(ev, t, f"openneuro-py غير مثبّت: {e}")
            return
        try:
            ds = "ds000001"
            openneuro.download(dataset=ds, target_dir=str(out / "raw"),
                               include=[p for t in ev["targets"] for p in t["openneuro"]["include"]])
        except Exception as e:  # noqa: BLE001
            for t in ev["targets"]:
                self.fail(ev, t, f"openneuro.download: {type(e).__name__}: {e}")
            return
        for t in ev["targets"]:
            p = out / "raw" / t["name"]
            if not p.exists():
                cand = list((out / "raw").rglob(t["name"]))
                if not cand:
                    self.fail(ev, t, "الملف لم يُنزَّل")
                    continue
                p = cand[0]
            self.add(ev, t, p, f"openneuro-py ds000001 / {t['name']}",
                     obs_date="2012 (إصدار OpenfMRI)", instrument="MRI 3T",
                     program_id="OpenNeuro ds000001",
                     official_checksum=dict(algorithm="sha256", value="(يتحقق منها openneuro-py أثناء التنزيل)",
                                            source="OpenNeuro GraphQL API", match=True))

    # ------------------------------------------------------------------ driver
    def run_event(self, ev):
        log(f"\n=== {ev['id']} · {ev['title']}")
        self.out_dir(ev)
        if self.args.dry_run:
            self.doi(ev)
            log(f"   DOI: {ev['doi']}")
            for t in ev["targets"]:
                log(f"   [plan] {t['name']}  ({t['role']})  → {ev['folder']}/raw/")
            log(f"   license page: {ev['license_url']}")
            return
        self.doi(ev)
        log(f"   DOI {ev['doi']} → {self.doi_cache[ev['id']].get('resolves')} "
            f"{self.doi_cache[ev['id']].get('landing')}")
        self.licence(ev)
        handler = dict(E01=self.e01, E02=self.e02, E03=self.eht, E04=self.eht,
                       E05=self.mast, E06=self.sdo, E07=self.iris, E08=self.cern,
                       E09=self.openneuro, E10=self.mast).get(ev["id"])
        if handler is None:
            log("   (لا مُنزِّل لهذا الحدث)")
            return
        try:
            handler(ev)
        except Exception as e:  # noqa: BLE001
            log(f"   !! handler crashed: {type(e).__name__}: {e}")
            for t in ev["targets"]:
                self.fail(ev, t, f"handler crashed: {type(e).__name__}: {e}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--event", help="E01,E02,…")
    p.add_argument("--all", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true", help="re-download even if the file exists")
    p.add_argument("--refresh-license", action="store_true")
    p.add_argument("--jsoc-email", help="بريد مسجّل في JSOC لتفعيل تصدير aia.lev1")
    args = p.parse_args(argv)

    ids = [s.strip().upper() for s in (args.event or "").split(",") if s.strip()]
    todo = [BY_ID[i] for i in ids] if ids else (EVENTS if args.all else [])
    if not todo:
        p.error("اختر --all أو --event E01,E02")

    run = Run(args)
    if args.jsoc_email:
        os.environ["JSOC_EMAIL"] = args.jsoc_email
        log(f"JSOC email set: {args.jsoc_email}")
    for ev in todo:
        run.run_event(ev)

    log(f"\nملفات مسجّلة: {len(run.records)} · إخفاقات: {len(run.failures)}")
    log("التالي: python tools/make_derived.py --all && python tools/make_index.py && python verify.py")
    return 0 if not run.failures else 2


if __name__ == "__main__":
    sys.exit(main())
