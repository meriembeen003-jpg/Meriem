#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vérification de l'existence et de la santé de chaque dépôt via l'API GitHub.
Résultat -> catalog/verified.json  (source de vérité : étoiles, licence, activité)"""
import json, subprocess, sys, pathlib, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from candidates import CANDIDATES

seen, rows = set(), []
for repo, cat, note, clone in CANDIDATES:
    if repo in seen:
        continue
    seen.add(repo)
    r = subprocess.run(["gh", "api", f"repos/{repo}"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"✗ INTROUVABLE {repo}  {r.stderr[:80].strip()}")
        continue
    d = json.loads(r.stdout)
    rows.append({
        "repo": repo,
        "categorie": cat,
        "note": note,
        "a_cloner": clone,
        "etoiles": d["stargazers_count"],
        "licence": (d.get("license") or {}).get("spdx_id"),
        "langage": d.get("language"),
        "dernier_push": d["pushed_at"],
        "archive": d["archived"],
        "sujets": (d.get("topics") or [])[:8],
        "description_officielle": (d.get("description") or "")[:300],
        "url": d["html_url"],
    })
    print(f"✓ {d['stargazers_count']:>7}★ {repo:<48} {(d.get('license') or {}).get('spdx_id')}")

rows.sort(key=lambda x: (-x["etoiles"]))
pathlib.Path("catalog/verified.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
print(f"\n{len(rows)} dépôts vérifiés -> catalog/verified.json")
