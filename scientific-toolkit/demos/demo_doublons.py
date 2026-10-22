#!/usr/bin/env python3
"""Démo 3 — réutilisation de texte : détection de « paper mill » et doublons."""
import json, pathlib, sys
RACINE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
from scitk.audit import duplicates

docs = json.loads((RACINE / "data" / "corpus_textes.json").read_text())
res = duplicates.doublons_corpus(docs, seuil=0.35)
print("═" * 74)
print("RÉUTILISATION DE TEXTE".center(74))
print("═" * 74)
print(f"{res['documents']} documents · shingles de {res['k_shingles']} mots · seuil {res['seuil']}")
for p in res["paires_suspectes"]:
    print(f"  {p['a']} ↔ {p['b']} : {p['similarite']:.0%}  ({p['methode']})")
print("─" * 74)
print("Fragments partagés entre article_A et article_C :")
for f in duplicates.phrases_identiques(docs["article_A"], docs["article_C"], 6)[:5]:
    print("   «", f[:90], "»")
print("─" * 74)
print(res["interpretation"])
