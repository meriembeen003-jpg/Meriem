#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit le catalogue final : JSON, CSV et CATALOGUE.md.

Fusionne : le catalogue curaté (notes françaises), la vérification API GitHub
(étoiles, licence, activité) et l'état local du miroir (vendor/).
"""
import csv
import json
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from candidates import CANDIDATES  # noqa: E402

CATEGORIES = {
    "decouverte": ("Découverte & métadonnées", "Interroger les index, résoudre les DOI, "
                   "explorer toutes les époques (archives historiques incluses)"),
    "fulltext": ("Texte intégral", "Récupérer les PDF : accès ouvert d'abord, autres voies ensuite"),
    "parsing": ("Extraction & structuration", "Transformer un PDF en données exploitables"),
    "synthese": ("Synthèse & RAG scientifique", "Lire, résumer, comparer, générer des revues"),
    "revue_systematique": ("Revue systématique", "PRISMA, screening, risque de biais, méta-analyse"),
    "audit": ("Audit & intégrité", "Vérifier les chiffres, les références, les rétractations"),
    "mcp": ("MCP & agents", "Exposer ces sources à un agent LLM"),
    "donnees": ("Données & dépôts", "Accéder aux jeux de données et aux dépôts"),
    "metascience": ("Corpus massifs & méta-science", "Analyser la science à l'échelle du corpus"),
}


def charger(chemin):
    p = RACINE / chemin
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def main():
    verifies = {d["repo"]: d for d in charger("catalog/verified.json")}
    tailles = {d["repo"].split("/")[-1]: d for d in charger("catalog/vendor_sizes.json")}
    manifeste = {d["repo"]: d for d in charger("catalog/vendor_manifest.json")}

    outils, manquants = [], []
    for repo, cat, note, vendored in CANDIDATES:
        v = verifies.get(repo, {})
        local = tailles.get(repo.split("/")[-1], {})
        entre = {
            "repo": repo,
            "categorie": cat,
            "note": note,
            "url": v.get("url", f"https://github.com/{repo}"),
            "etoiles": v.get("etoiles"),
            "licence": v.get("licence"),
            "langage": v.get("langage"),
            "dernier_push": v.get("dernier_push"),
            "archive": v.get("archive"),
            "sujets": v.get("sujets", []),
            "description_officielle": v.get("description_officielle", ""),
            "verifie": bool(v),
            "archive_localement": repo in manifeste and manifeste[repo].get("statut") == "ok",
            "chemin_local": manifeste.get(repo, {}).get("chemin", ""),
            "taille_locale_mo": local.get("Mo"),
            "fichiers_locaux": local.get("fichiers"),
        }
        if not v:
            manquants.append(repo)
        outils.append(entre)

    outils.sort(key=lambda o: (o["categorie"], -(o["etoiles"] or 0)))
    (RACINE / "catalog" / "outils.json").write_text(
        json.dumps(outils, indent=1, ensure_ascii=False), encoding="utf-8")

    with open(RACINE / "catalog" / "outils.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["repo", "categorie", "etoiles", "licence", "langage", "dernier_push",
                "archive", "archive_localement", "chemin_local", "taille_locale_mo", "note", "url"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(outils)

    # ── statistiques
    total_etoiles = sum(o["etoiles"] or 0 for o in outils)
    licences = {}
    for o in outils:
        licences[o["licence"] or "non précisée"] = licences.get(o["licence"] or "non précisée", 0) + 1
    archives = sum(1 for o in outils if o["archive"])
    archives_locaux = sum(1 for o in outils if o["archive_localement"])
    taille = sum(o["taille_locale_mo"] or 0 for o in outils)

    # ── CATALOGUE.md
    L = ["# Catalogue vérifié — recherche & audit scientifiques sur GitHub", "",
         f"**{len(outils)} dépôts** · {total_etoiles:,} étoiles cumulées · "
         f"{archives_locaux} archivés localement ({taille:.1f} Mo) · "
         f"{len(manquants)} non vérifiables".replace(",", " "), "",
         "Chaque entrée a été contrôlée via l'API GitHub (existence, étoiles, licence, "
         "dernière activité, archivage). Les notes en français expliquent *à quoi sert* "
         "l'outil et *pourquoi* il compte pour la recherche ou l'audit.", "",
         "> ⚠️ Les outils de téléchargement de PDF hors accès ouvert (Sci-Hub, LibGen) sont "
         "signalés dans la catégorie « Texte intégral ». Leur usage peut violer les "
         "conditions des éditeurs : ce kit privilégie systématiquement les voies légales "
         "(Unpaywall, OpenAlex, Europe PMC, dépôts institutionnels). Voir `LEGAL.md`.", "",
         "## Sommaire", ""]
    for cle, (nom, _) in CATEGORIES.items():
        n = sum(1 for o in outils if o["categorie"] == cle)
        L.append(f"- [{nom}](#{nom.lower().replace(' ', '-').replace('&', '')}) — {n} outils")
    L += ["", "## Vue d'ensemble", "", "| Catégorie | Outils | Étoiles cumulées | Archivés |",
          "|---|---|---|---|"]
    for cle, (nom, _) in CATEGORIES.items():
        lot = [o for o in outils if o["categorie"] == cle]
        L.append(f"| {nom} | {len(lot)} | {sum(o['etoiles'] or 0 for o in lot):,} | "
                 f"{sum(1 for o in lot if o['archive_localement'])} |".replace(",", " "))
    L.append("")

    for cle, (nom, sous_titre) in CATEGORIES.items():
        lot = [o for o in outils if o["categorie"] == cle]
        if not lot:
            continue
        L += [f"## {nom}", "", f"*{sous_titre}*", "",
              "| Étoiles | Dépôt | Licence | Dernier push | Rôle | Local |",
              "|---:|---|---|---|---|---|"]
        for o in sorted(lot, key=lambda x: -(x["etoiles"] or 0)):
            actif = "🗄️" if o["archive_localement"] else ("⚠️ archivé" if o["archive"] else "")
            note = o["note"].replace("|", "/")
            licence = o["licence"] or "—"
            date = (o["dernier_push"] or "—")[:10]
            etoiles = f"{o['etoiles']:,}".replace(",", " ") if o["etoiles"] is not None else "?"
            L.append(f"| {etoiles} | [{o['repo']}]({o['url']}) | {licence} | {date} | {note} | {actif} |")
        L.append("")

    if manquants:
        L += ["## Dépôts non vérifiés", "",
              "Ces entrées n'ont pas pu être confirmées par l'API (renommage, dépôt privé "
              "ou supprimé). Elles sont conservées à titre indicatif :", ""]
        L += [f"- `{r}`" for r in manquants] + [""]

    L += ["---", "",
          "## Méthode de constitution", "",
          "1. `scripts/candidates.py` — catalogue curaté à la main (rôle, catégorie, intérêt).",
          "2. `scripts/verify.py` — vérification de chaque dépôt via l'API GitHub "
          "(étoiles, licence SPDX, dernier push, archivage).",
          "3. `scripts/fetch.py` — clone superficiel des dépôts retenus dans `vendor/`.",
          "4. `scripts/prune.py` — réduction à un miroir « source seule » (code + docs, "
          "sans binaires ni modèles) pour rester dans un budget de stockage raisonnable.",
          "5. `scripts/build_catalog.py` — fusion et génération de ce catalogue.",
          "",
          "Les étoiles sont un indicateur de notoriété, **pas de qualité scientifique** : "
          "un outil à 30 étoiles peut être la référence d'un domaine étroit (ex. "
          "`quest-bih/rtransparent`, `codecheckers/codecheck`)."]
    (RACINE / "CATALOGUE.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"{len(outils)} outils · {archives_locaux} archivés · {taille:.1f} Mo · "
          f"{total_etoiles} étoiles")
    print("-> catalog/outils.json, catalog/outils.csv, CATALOGUE.md")
    if manquants:
        print("non vérifiés :", ", ".join(manquants))


if __name__ == "__main__":
    main()
