#!/usr/bin/env python3
"""Découverte : interroge l'API GitHub (via gh) pour lister les dépôts
les plus populaires par thématique. Résultat -> catalog/discovery.json"""
import json, subprocess, urllib.parse, pathlib

QUERIES = [
    ("discovery",   "literature search papers api"),
    ("discovery",   "academic paper retrieval api"),
    ("systematic",  "systematic review automation"),
    ("integrity",   "scientific integrity reproducibility"),
    ("integrity",   "statistical error detection"),
    ("scientometry","scientometrics bibliometrics"),
    ("pdf",         "scientific pdf parsing"),
    ("synth",       "scientific literature rag llm"),
    ("meta",        "meta-analysis"),
    ("fulltext",    "open access fulltext download"),
    ("mcp",         "mcp server pubmed arxiv"),
    ("retraction",  "retraction citation check"),
]

def gh(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode != 0:
        print("ERR", path, r.stderr[:200])
        return []
    d = json.loads(r.stdout)
    return d.get("items", []) if isinstance(d, dict) else d

out = {}
for tag, q in QUERIES:
    url = ("search/repositories?q=" + urllib.parse.quote(q)
           + "&sort=stars&order=desc&per_page=20")
    items = gh(url)
    print(f"\n### {tag} :: {q}")
    for it in items[:12]:
        print(f"{it['stargazers_count']:>7} {it['full_name']:<45} {str(it['description'])[:68]}")
    out.setdefault(tag, []).extend(
        {k: it[k] for k in ("full_name", "stargazers_count", "description",
                            "archived", "pushed_at", "topics", "language")}
        | {"license": (it.get("license") or {}).get("spdx_id")}
        for it in items)

pathlib.Path("catalog/discovery.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("\n-> catalog/discovery.json")
