#!/usr/bin/env python3
"""Upload the archive to Google Drive (browser-side, no shell egress needed).

The page reads ../archive/tasks.json, then for each task
  1. POSTs the file to /api/upload  (same origin; the Next.js route proxies it to Drive)
  2. POSTs the caption as a Drive comment
Progress is kept in localStorage and the task id is appended to the URL hash, so the
run can be resumed after a reload.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import catalog  # noqa: E402
from texts import TEXTS  # noqa: E402

OUT = os.path.join(HERE, "tasks.json")

ORDER = ["deep", "galaxies", "clusters", "nebulae", "stars", "snr", "bh",
         "exo", "fits", "sun"]

PREFIX = {"deep": "07", "galaxies": "01", "clusters": "06", "nebulae": "04",
          "stars": "03", "snr": "08", "bh": "02", "exo": "05", "fits": "09",
          "sun": "10"}


def slug(e):
    s = e["key"].replace("_", "-")
    return s


def caption(e):
    return (
        f"**{e['name']}**\n\n"
        f"التفسير العلمي: {e['science']}\n\n"
        f"الخصائص المرصودة: {e['props']}\n\n"
        f"الطول الموجي / النطاق: {e['wl']}\n\n"
        f"المصدر: {e['src']} — {e['telescope']} ({e['instrument']}) — تاريخ الرصد: {e['date']}\n\n"
        f"حقوق النسب: {e['credit']} — الرخصة: {e['license']}\n\n"
        f"حجم الصورة الأصلي: {e.get('pixels', '—')} — SHA1: {e['sha1'][:16]}"
    )


def main():
    ents = catalog.build()
    tasks = []
    for e in ents:
        ext = os.path.splitext(e["file"])[1].lower()
        name = f"{PREFIX[e['folder']]}_{slug(e)}{ext}"
        staged = os.path.join(HERE, "upload", name)
        tasks.append(dict(id=e["key"], folder=e["folder"], name=name,
                          path=os.path.relpath(staged, os.path.dirname(HERE)), _src=e["file"],
                          bytes=e["bytes"], caption=caption(e), science=e["science"]))
    # calibrated products rendered in this workspace (kept where the source FITS is public)
    renders = [
        ("meerkat", "09_NGC1044_MeerKAT_Lband_radio.png", "glx_meerkat.png", "01"),
        ("chandra", "10_HCG62_Chandra_ACIS_xray.png", "clu_hcg62.png", "06"),
        ("soho", "11_SOHO_EIT_195A_corona.png", "sun_soho.png", "10"),
        ("aia", "12_SDO_AIA_171A_corona.png", "sun_aia.png", "10"),
        ("herschel", "13_Herschel_SPIRE_350um_submm.png", "sub_herschel.png", "03"),
        ("fermi", "15_FermiLAT_gamma_ray_sky_map.png", "gam_fermi.png", "06"),
    ]
    for key, fname, out, pref in renders:
        for e in catalog.FITS_RENDERED:
            if e["key"] != key:
                continue
            src_rel = "final/" + fname
            staged = os.path.join(HERE, "upload", f"{pref}_{out}")
            tasks.append(dict(id="render_" + key, folder=e["folder"], name=f"{pref}_{out}",
                              path=os.path.relpath(staged, os.path.dirname(HERE)),
                              _src=src_rel, bytes=os.path.getsize(os.path.join(HERE, src_rel)),
                              caption=(f"**{e['name']}**\n\nالتفسير العلمي: {TEXTS[e['key']][0]}\n\n"
                                       f"الخصائص المرصودة: {TEXTS[e['key']][1]}\n\n"
                                       f"الطول الموجي / النطاق: {e['wl']}\n\n"
                                       f"المصدر: {e['src']} — {e['telescope']} ({e['instrument']})، "
                                       f"{e['date']}\n\nحقوق النسب: {e['credit']} — {e['license']}\n\n"
                                       f"الصورة مبنية من منتج FITS عام: {e['src']} (سلم ألوان كاذب موضّح في التعليق)."),
                              science=TEXTS[e["key"]][0]))

    # FITS originals
    for i, (src, name, note) in enumerate(catalog.FITS_FILES):
        p = os.path.join(HERE, src)
        staged = os.path.join(HERE, "upload", name)
        tasks.append(dict(id="fits_" + str(i), folder="fits", name=name,
                          path=os.path.relpath(staged, os.path.dirname(HERE)), _src=src,
                          bytes=os.path.getsize(p),
                          caption=(f"**{name}**\n\nالتفسير العلمي: {note}\n\n"
                                   f"الخصائص: منتج علمي معاير من الأرشيف العام، بوحدات وWCS كاملة في الترويسة.\n\n"
                                   f"المصدر: {src}\n\nحقوق النسب: بيانات عامة من الأرشيفات الفلكية "
                                   f"(NASA/ESA/ESO/SARAO) — تُستخدم للأغراض العلمية مع ذكر المصدر."),
                          science=note))
    folders = []
    names = {
        "galaxies": "01 — المجرات (Galaxies)",
        "bh": "02 — الثقوب السوداء والنوى المجرية النشطة (Black Holes & AGN)",
        "stars": "03 — النجوم والعناقيد النجمية (Stars & Clusters)",
        "nebulae": "04 — السدم (Nebulae)",
        "exo": "05 — الكواكب الخارجية (Exoplanets)",
        "clusters": "06 — العناقيد المجرية والبنية الكونية (Clusters & Cosmic Web)",
        "deep": "07 — حقول الرصد العميق (Deep Fields)",
        "snr": "08 — البقايا النجمية (Supernova Remnants)",
        "fits": "09 — الرصد متعدد الأطوال الموجية بأدوات موثقة (Multi-wavelength FITS)",
        "sun": "10 — الشمس والغلاف الشمسي (Sun & Heliosphere)",
    }
    for k in ORDER:
        folders.append(dict(id=k, name=names[k], drive_id=catalog.FOLDERS[k]))
    out = dict(root="1JTJwVP-dhjA1_pAb2k1psJPCNrUiqt-i", folders=folders, tasks=tasks)
    for t in out["tasks"]:
        stem = os.path.splitext(t["name"])[0]
        thumb = os.path.join(HERE, "thumbs", stem + ".jpg")
        t["thumb"] = ("thumbs/" + stem + ".jpg") if os.path.exists(thumb) else None
    clean = dict(out)
    clean["tasks"] = [{k: v for k, v in t.items() if not k.startswith("_")} for t in out["tasks"]]
    json.dump(clean, open(OUT, "w"), ensure_ascii=False)
    # stage every file under its final Drive name so the browser page can fetch it
    up = os.path.join(HERE, "upload")
    os.makedirs(up, exist_ok=True)
    for t in tasks:
        src = os.path.join(HERE, t["_src"])
        dst = os.path.join(os.path.dirname(HERE), t["path"])
        if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
            if os.path.lexists(dst):
                os.remove(dst)
            os.link(src, dst)
    print(f"{len(tasks)} tasks, {sum(t['bytes'] for t in tasks)/1e6:.0f} MB")


if __name__ == "__main__":
    main()
