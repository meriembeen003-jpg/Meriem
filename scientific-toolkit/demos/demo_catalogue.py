#!/usr/bin/env python3
"""Démo 4 — exploration du catalogue vérifié (142 outils)."""
import collections, json, pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent
outils = json.loads((RACINE / "catalog" / "outils.json").read_text(encoding="utf-8"))
print("═" * 74)
print("CATALOGUE — 142 OUTILS DE RECHERCHE ET D'AUDIT".center(74))
print("═" * 74)
etoiles = sum(o["etoiles"] or 0 for o in outils)
print(f"{len(outils)} dépôts · {etoiles:,} étoiles cumulées · "
      f"{sum(1 for o in outils if o['archive_localement'])} archivés localement".replace(",", " "))
licences = collections.Counter(o["licence"] or "non précisée" for o in outils)
print("Licences :", " · ".join(f"{k} {v}" for k, v in licences.most_common(6)))
print("─" * 74)
par_cat = collections.defaultdict(list)
for o in outils:
    par_cat[o["categorie"]].append(o)
for cat, lot in sorted(par_cat.items(), key=lambda x: -len(x[1])):
    top = sorted(lot, key=lambda o: -(o["etoiles"] or 0))[:3]
    print(f"{cat:20} {len(lot):>2} outils | " + ", ".join(
        f"{o['repo'].split('/')[-1]} ({o['etoiles']})" for o in top))
print("─" * 74)
print("Les 10 plus étoilés :")
for o in sorted(outils, key=lambda o: -(o["etoiles"] or 0))[:10]:
    print(f"  {str(o['etoiles']):>6}★ {o['repo']:<44} {o['note'][:70]}")
