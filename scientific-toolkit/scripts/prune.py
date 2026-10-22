#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Réduit vendor/ à un miroir « source seule » : code, docs, configurations.

Supprime : binaires, modèles, images, archives, PDF, jeux de données, dépendances
(node_modules, vendor d'un vendor), builds. Objectif : rester sous le budget de
persistance du dépôt tout en gardant l'intégralité du code lisible.
"""
import pathlib, sys, shutil, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor"

CODE_EXT = {
    ".py", ".pyx", ".pxd", ".ipynb", ".r", ".rmd", ".jl", ".m", ".c", ".h", ".cc",
    ".cpp", ".hpp", ".java", ".scala", ".go", ".rs", ".js", ".jsx", ".ts", ".tsx",
    ".vue", ".svelte", ".sh", ".bash", ".ps1", ".bat", ".sql", ".html", ".css",
    ".scss", ".less", ".xml", ".xsl", ".json", ".jsonl", ".yaml", ".yml", ".toml",
    ".ini", ".cfg", ".conf", ".txt", ".md", ".rst", ".tex", ".bib", ".csl", ".cls",
    ".sty", ".bst", ".csv", ".tsv", ".mod", ".lua", ".pl", ".rb", ".php", ".ex",
    ".exs", ".clj", ".lisp", ".f", ".f90", ".for", ".sas", ".do", ".dockerfile",
    ".lock", ".env.example", ".gitignore", ".gitattributes", ".editorconfig",
}
KEEP_NAMES = {"LICENSE", "LICENCE", "COPYING", "NOTICE", "Dockerfile", "Makefile",
              "README", "CITATION", "CITATION.cff", "AUTHORS", "CONTRIBUTING.md",
              "requirements.txt", "setup.py", "pyproject.toml", "DESCRIPTION", "NAMESPACE"}
DROP_DIRS = {"node_modules", ".git", ".github", "dist", "build", "__pycache__", ".pytest_cache",
             "site-packages", ".venv", "venv", "target", ".mypy_cache", ".ruff_cache",
             "models", "weights", "checkpoints", "images", "img", "figures", "figs",
             "screenshots", "assets", "media", "videos", "data", "datasets", "corpus",
             "test_files", "test-data", "fixtures", "docs/_build", "_build", "coverage",
             "sdlc", "testdata", "golden", "replay", "snapshots", "archive", "site",
             "public", "preview", "vendor_bundle", "third_party"}
MAX_BYTES = 150_000          # aucun fichier > 400 Ko conservé
TOTAL_BUDGET = 62_000_000     # ~62 Mo
FILE_BUDGET = 7_000


def keep(p: pathlib.Path) -> bool:
    if p.is_dir():
        return p.name.lower() not in DROP_DIRS
    if p.name in KEEP_NAMES or p.name.split(".")[0].upper() in {"LICENSE", "COPYING"}:
        return True
    ext = p.suffix.lower()
    if ext not in CODE_EXT:
        return False
    try:
        if p.stat().st_size > MAX_BYTES:
            return False
    except OSError:
        return False
    return True


def prune_repo(d: pathlib.Path):
    removed = 0
    for child in sorted(d.rglob("*"), key=lambda x: -len(x.parts)):
        if not child.exists():
            continue
        if child.is_dir():
            if child.name.lower() in DROP_DIRS:
                shutil.rmtree(child, ignore_errors=True)
                removed += 1
        elif not keep(child):
            child.unlink(missing_ok=True)
            removed += 1
    return removed


def main():
    if not VENDOR.exists():
        sys.exit("vendor/ absent — lancer scripts/fetch.py")
    total_removed = 0
    report = []
    for cat in sorted(VENDOR.iterdir()):
        if not cat.is_dir():
            continue
        for repo in sorted(cat.iterdir()):
            if not repo.is_dir():
                continue
            n = prune_repo(repo)
            size = sum(f.stat().st_size for f in repo.rglob("*") if f.is_file())
            files = sum(1 for f in repo.rglob("*") if f.is_file())
            total_removed += n
            report.append({"repo": f"{cat.name}/{repo.name}", "Mo": round(size / 1e6, 2), "fichiers": files})
            if size == 0:
                shutil.rmtree(repo, ignore_errors=True)
                report[-1]["Mo"] = 0
    report.sort(key=lambda x: -x["Mo"])
    (ROOT / "catalog" / "vendor_sizes.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    tot = sum(r["Mo"] for r in report)
    nf = sum(r["fichiers"] for r in report)
    print(f"supprimés : {total_removed} éléments")
    print(f"reste : {len(report)} dépôts · {tot:.1f} Mo · {nf} fichiers")
    for r in report[:12]:
        print(f"  {r['Mo']:7.1f} Mo  {r['fichiers']:>5} f  {r['repo']}")


if __name__ == "__main__":
    main()
