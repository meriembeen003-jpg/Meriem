#!/usr/bin/env python3
"""Démo 2 — revue systématique PRISMA depuis un corpus multi-sources."""
import csv, pathlib, sys
RACINE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
from scitk.pipeline.review import RevueSystematique
from scitk.search.models import Travail

lignes = list(csv.DictReader(open(RACINE / "data" / "corpus_exemple.csv", encoding="utf-8")))
travaux = [Travail(titre=l["titre"], doi=l["doi"], annee=int(l["annee"]),
                   auteurs=[a.strip() for a in l["auteurs"].split(";")],
                   revue=l["revue"], resume=l["resume"], citations=int(l["citations"]),
                   source=l["source"], oa_url=l["oa_url"]) for l in lignes]

revue = RevueSystematique(
    nom="Remédiation en lecture",
    question="Quelle est l'efficacité des programmes de remédiation en lecture au primaire ?")
revue.criteres_inclusion = [r"lecture|reading"]
revue.criteres_exclusion = [r"rodent|animal"]
revue.par_source = {}
for t in travaux:
    revue.par_source[t.source] = revue.par_source.get(t.source, 0) + 1
revue.identifies = len(travaux)
revue.travaux = travaux
revue.journal.append({"etape": "import", "fichier": "data/corpus_exemple.csv", "n": len(travaux)})

revue.dedupliquer().cribler().evaluer_acces()
chemins = revue.exporter(str(RACINE / "demos" / "out" / "revue"), "lecture")

c = revue.prisma()
print("═" * 74)
print("REVUE SYSTÉMATIQUE — FLUX PRISMA 2020".center(74))
print("═" * 74)
print(f"Identifiés              : {c['identifies']}")
for s, n in c["par_source"].items():
    print(f"   · {s:16}: {n}")
print(f"Doublons supprimés      : {c['doublons']}")
print(f"Exclus (titre/résumé)   : {c['exclus_titre']}")
for m, n in c["motifs_exclusion"].items():
    print(f"   · {m:40} {n}")
print(f"Inclus                  : {c['inclus']}")
print(f"PDF en accès ouvert     : {revue.acces['avec_pdf_oa']}")
print("─" * 74)
print("Études incluses :")
for t in revue.travaux:
    print(f"  • {t.annee} — {t.titre[:72]}")
print("─" * 74)
for k, v in chemins.items():
    print(f"{k:16} {v}")
