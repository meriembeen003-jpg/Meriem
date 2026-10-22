#!/usr/bin/env python3
"""Démo 1 — audit complet d'un article : statistiques, GRIM, transparence, biblio, rapport."""
import pathlib, sys
RACINE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
from scitk.audit import report, refs

texte = (RACINE / "data" / "article_exemple.txt").read_text(encoding="utf-8")
biblio = refs.charger_bibliographie(str(RACINE / "data" / "references_exemple.bib"))
import json
descriptifs = json.loads((RACINE / "data" / "descriptifs_exemple.json").read_text())

r = report.auditer_article(texte, references=biblio, descriptifs=descriptifs,
                           auteur="Dupont")
chemins = report.ecrire(r, str(RACINE / "demos" / "out" / "audit_article"),
                        "Audit — article de démonstration")

s = r["synthese_statistique"]
print("═" * 74)
print("AUDIT D'ARTICLE".center(74))
print("═" * 74)
print(f"Résultats extraits      : {s['resultats_extraits']}")
print(f"Significatifs (p < .05) : {s['significatifs']}")
print(f"Incohérences majeures   : {s['incoherents']}   (arrondis stricts : {s['arrondis_stricts']})")
print(f"Erreurs de décision     : {s['erreurs_de_decision']}")
print(f"Cohérence statistique   : {s['score_coherence']}/100")
print(f"Transparence            : {r['transparence']['score']}/100 "
      f"(manquants : {', '.join(r['transparence']['manquants']) or 'aucun'})")
print(f"Score global            : {r['score_global']}/100 — gravité {r['gravite'].upper()}")
print("─" * 74)
for c in r["constats"]:
    print(f"[{c['severite'].upper():8}] {c['code']:20} {c['message'][:96]}")
print("─" * 74)
for k, v in chemins.items():
    print(f"{k:9} {v}")
