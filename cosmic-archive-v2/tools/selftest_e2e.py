#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""selftest_e2e.py — prove the whole chain works without touching any archive.

It builds tiny synthetic files, serves them over a local HTTP server (so the
real download code path, retries and sidecar-checksum probing are exercised),
then runs: download → checksum (incl. a published .sha256 sidecar) → structural
validation → record → MANIFEST → verify.

Output goes to _selftest/e2e/.  Everything here is labelled
«مصدر أولي: لا · رصد/نموذج/اختبار: اختبار» and never enters the real MANIFEST.
"""

from __future__ import annotations

import csv
import hashlib
import http.server
import json
import os
import socketserver
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

OUT = ROOT / "_selftest" / "e2e"
FIX = OUT / "served"


def build_fixtures():
    import numpy as np
    FIX.mkdir(parents=True, exist_ok=True)
    from astropy.io import fits
    hdu = fits.PrimaryHDU(np.zeros((16, 16), dtype="f4"))
    hdu.header.update({"NSIDE": 32, "ORDERING": "RING", "COORDSYS": "G"})
    hdu.writeto(FIX / "map.fits", overwrite=True)

    with open(FIX / "spectrum.txt", "w") as f:
        f.write("# L TT\n")
        for i in range(2, 600):
            f.write(f"{i} {1e4 / i:.6e}\n")

    import h5py
    with h5py.File(FIX / "strain.hdf5", "w") as f:
        d = f.create_dataset("strain/Strain", data=np.random.randn(300000).astype("f8"))
        d.attrs["Xspacing"] = 1 / 16384
        d.attrs["Xstart"] = 0
        f.create_dataset("meta/Detector", data=np.bytes_("H1"))
        f.create_dataset("meta/UTCstart", data=np.bytes_("TEST"))

    from obspy import Stream, Trace, UTCDateTime
    st = Stream([Trace(data=np.random.randn(4000).astype("f4"),
                       header=dict(station=f"S{i}", network="XX", channel="BHZ",
                                   sampling_rate=40.0, starttime=UTCDateTime(2020, 1, 1)))
                 for i in range(5)])
    st.write(str(FIX / "multi.mseed"), format="MSEED")

    import nibabel as nib
    nib.save(nib.Nifti1Image(np.random.rand(12, 12, 12).astype("f4"), np.eye(4)), str(FIX / "t1.nii.gz"))

    (FIX / "usgs.json").write_text(json.dumps({"features": [{"id": "test", "properties": {"mag": 7.9}}]}))

    # a published checksum sidecar, to exercise official-checksum comparison
    h = hashlib.sha256((FIX / "spectrum.txt").read_bytes()).hexdigest()
    (FIX / "spectrum.txt.sha256").write_text(h + "  spectrum.txt\n")
    return dict(map="map.fits", spectrum="spectrum.txt", strain="strain.hdf5",
                mseed="multi.mseed", nifti="t1.nii.gz", usgs="usgs.json")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(FIX), **kw)

    def log_message(self, *a):
        pass


def main():
    if not (ROOT / "_fetch_records.json").exists():
        ROOT.joinpath("_fetch_records.json").write_text("[]")
    OUT.mkdir(parents=True, exist_ok=True)
    names = build_fixtures()

    srv = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"

    import fetch_primary as fp

    # isolate the self-test records from the real ones
    fp.RECORDS = OUT / "_fetch_records.json"
    fp.FAILURES = OUT / "_fetch_failures.json"
    fp.RECORDS.write_text("[]")
    fp.FAILURES.write_text("[]")

    args = fp.argparse.Namespace(dry_run=False, force=True, refresh_license=False)
    run = fp.Run(args)
    ev = dict(id="SELFTEST", title="اختبار ذاتي شامل (ليس دليلاً)", folder="_selftest/e2e/event",
              doi="10.0000/selftest", license_text="fixture", license_url=base,
              instrument="FIXTURE")
    run.doi_cache[ev["id"]] = dict(doi=ev["doi"], resolves=None, note="selftest")

    specs = [("map", "fits_planck_map"), ("spectrum", "planck_spectrum"),
             ("strain", "gwosc_hdf5"), ("mseed", "mseed"),
             ("nifti", "nifti"), ("usgs", "usgs_event")]
    for key, validator in specs:
        url = f"{base}/{names[key]}"
        dest = ROOT / ev["folder"] / "raw" / names[key]
        r = fp.download(url, dest, timeout=30)
        assert r["ok"], (key, r)
        target = dict(name=names[key], role="selftest", kind="test", validation=validator)
        run.add(ev, target, dest, url)
    srv.shutdown()

    # manifest from the self-test records only
    env_backup = os.environ.get("CA_MANIFEST_SCOPE")
    os.environ["CA_MANIFEST_SCOPE"] = "e2e"
    import make_index
    make_index.ROOT = ROOT
    rows = []
    for r in json.loads((OUT / "_fetch_records.json").read_text()):
        p = ROOT / r["file"]
        oc = r.get("official_checksum") or {}
        rows.append(dict(event="SELFTEST", event_title="اختبار ذاتي شامل", record_type="test",
                         record_type_ar="اختبار", primary_source="لا", primary_source_ar="لا",
                         file=r["file"], bytes=p.stat().st_size, sha256=fp.sha256_file(p),
                         official_checksum=(f"{oc.get('algorithm')}:{oc.get('value')}" if oc.get("value") else "غير منشور"),
                         checksum_match="نعم" if oc.get("match") else "لا ينطبق",
                         archive="fixtures", archive_product=r["product"], doi="", doi_resolves="لا ينطبق",
                         doi_landing="", license_declared="fixture", license_url=base, instrument="FIXTURE",
                         program_id="SELFTEST", obs_date="", processing="none",
                         colour="لا شيء", audio="لا", validator=r["validator"],
                         validation=json.dumps(r["validation"], ensure_ascii=False), notes="selftest"))
    mf = OUT / "MANIFEST_E2E.csv"
    with open(mf, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        [w.writerow(r) for r in rows]

    import verify
    rows2, problems, per_event, checked = verify.verify_manifest(mf)
    print(f"\nE2E: {checked} files, {len(problems)} problems")
    for p in problems:
        print("  ", p)
    checksum_row = [r for r in rows if "spectrum" in r["file"]][0]
    print("official sidecar checksum comparison:", checksum_row["official_checksum"][:20],
          "→ match:", checksum_row["checksum_match"])
    summary = dict(files=checked, problems=problems,
                   validators={r["validator"]: json.loads(r["validation"]).get("details", "")[:90]
                               for r in rows})
    (OUT / "selftest_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
