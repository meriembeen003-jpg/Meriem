#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Archive les dépôts du catalogue dans vendor/ (clone superficiel, .git retiré).

  python3 scripts/fetch.py              # uniquement les dépôts "vendored"
  python3 scripts/fetch.py --opt        # + les outils lourds (à la demande)
  python3 scripts/fetch.py --only owner/repo
  python3 scripts/fetch.py --list
"""
import argparse, json, pathlib, shutil, subprocess, sys, concurrent.futures as cf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from candidates import CANDIDATES

ROOT = pathlib.Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor"
MANIFEST = ROOT / "catalog" / "vendor_manifest.json"


def clone(row):
    repo, cat, note, vendored = row
    dest = VENDOR / cat / repo.split("/")[1]
    if (dest / ".git").exists() or (dest.exists() and any(dest.iterdir())):
        return {"repo": repo, "statut": "déjà présent", "chemin": str(dest.relative_to(ROOT))}
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone", "--depth", "1", "--single-branch", "--quiet",
           "--config", "advice.detachedHead=false", f"https://github.com/{repo}.git", str(dest)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        return {"repo": repo, "statut": "échec", "erreur": r.stderr.strip()[:200]}
    shutil.rmtree(dest / ".git", ignore_errors=True)
    size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
    return {"repo": repo, "statut": "ok", "chemin": str(dest.relative_to(ROOT)),
            "octets": size, "fichiers": sum(1 for f in dest.rglob("*") if f.is_file())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opt", action="store_true", help="inclure les outils lourds")
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    rows = [r for r in CANDIDATES if r[3]] if not a.opt else list(CANDIDATES)
    if a.only:
        rows = [r for r in CANDIDATES if r[0] in a.only]
    if a.list:
        for r in rows:
            print(f"{'★' if r[3] else ' '} {r[0]:<50} {r[1]}")
        return

    VENDOR.mkdir(exist_ok=True)
    results = []
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(clone, rows):
            if res["statut"] == "ok":
                print(f"✓ {res['repo']:<50} {res.get('octets',0)/1e6:6.1f} Mo  {res.get('fichiers',0):>5} fichiers")
            else:
                print(f"✗ {res['repo']:<50} {res['statut']} {res.get('erreur','')[:80]}")
            results.append(res)

    old = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
    index = {r["repo"]: r for r in old}
    index.update({r["repo"]: r for r in results})
    MANIFEST.write_text(json.dumps(sorted(index.values(), key=lambda x: x["repo"]), indent=1, ensure_ascii=False))
    total = sum(r.get("octets", 0) for r in index.values() if r["statut"] == "ok")
    ok = sum(1 for r in index.values() if r["statut"] == "ok")
    print(f"\n{ok} dépôts archivés · {total/1e6:.1f} Mo · manifeste → catalog/vendor_manifest.json")


if __name__ == "__main__":
    main()
