#!/usr/bin/env python3
"""Démo 5 — recherche fédérée en ligne (OpenAlex, Crossref, Europe PMC, arXiv).

Nécessite un accès réseau vers les API scientifiques. Dans un environnement
restreint, la démo explique l'échec et montre le mode hors ligne équivalent.
"""
import pathlib, sys
RACINE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
from scitk.search.http import Client, ErreurReseau
from scitk.search import federated

requete = "reading remediation randomized controlled trial"
print("═" * 74)
print("RECHERCHE FÉDÉRÉE".center(74))
print("═" * 74)
print("Requête :", requete)
try:
    res = federated.rechercher(Client(cache=True), requete,
                               ["openalex", "crossref", "europepmc", "arxiv"], limite=10)
except ErreurReseau as e:
    print(f"\nRéseau indisponible : {e}")
    print("→ Cet environnement n'autorise pas les appels aux API scientifiques.")
    print("→ Sur une machine connectée, la même commande fonctionne :")
    print('   python3 -m scitk search "reading remediation" --sources openalex,crossref')
    print("→ Équivalent hors ligne : python3 demos/demo_revue.py (corpus local)")
    sys.exit(0)

if res.erreurs:
    print("Sources en échec :", ", ".join(f"{k}" for k in res.erreurs))
if not res.travaux:
    print("\nAucune source joignable depuis cet environnement (attendu : seuls GitHub, "
          "PyPI et npm sont autorisés).\n"
          "→ Sur une machine connectée :\n"
          '   python3 -m scitk search "reading remediation" --sources openalex,crossref\n'
          "→ Équivalent hors ligne : python3 demos/demo_revue.py")
    sys.exit(0)
print(f"{res.total_brut} résultats bruts → {len(res.travaux)} uniques "
      f"({res.doublons} doublons fusionnés)")
for t in res.travaux:
    print(f"\n• {t.titre[:88]}")
    print(f"  {', '.join(t.auteurs[:3])}{' et al.' if len(t.auteurs) > 3 else ''} "
          f"({t.annee}) — {t.revue[:60]}")
    print(f"  DOI {t.doi or '—'} · {t.citations if t.citations is not None else '?'} citations "
          f"· sources {','.join(t.sources_multiples)}")
print("\nCouverture :", federated.couverture(res))
