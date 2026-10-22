# Recherche & audit scientifiques — console + boîte à outils

Ce dépôt réunit deux choses complémentaires :

1. **`scientific-toolkit/`** — un poste de travail scientifique : un catalogue
   **vérifié** de 142 outils GitHub (recherche, texte intégral, extraction,
   synthèse, revue systématique, intégrité), un **miroir local** du code des
   74 outils les plus utiles (34 Mo, utilisable hors ligne), et une bibliothèque
   Python `scitk` qui les recompose en un flux unique — dont un moteur d'audit
   statistique déterministe de 35 tests ;
2. **cette application Next.js** — une console qui exécute, dans le navigateur,
   la recherche fédérée (OpenAlex, Crossref, Europe PMC) et le même audit
   statistique (recalcul APA, GRIM, bornes exactes de l'écart-type).

## Démarrer

```bash
# console web
npm install && npm run dev          # http://localhost:3000

# boîte à outils (aucune dépendance obligatoire)
cd scientific-toolkit
python3 -m unittest discover -s tests
python3 -m scitk audit data/article_exemple.txt --biblio data/references_exemple.bib \
        --descriptifs data/descriptifs_exemple.json --out demos/out/audit_article
bash demos/run_all.sh
```

## Ce que fait l'audit

| Contrôle | Méthode |
|---|---|
| Cohérence statistique | extraction APA (t, F, χ², r, z), recalcul de p, **intervalle d'arrondi** de la statistique |
| Erreurs de décision | comparaison au seuil, y compris les affirmations « significatif » du texte |
| GRIM / GRIMMER / SPRITE | granularité des moyennes et **bornes exactes** de l'écart-type pour des données entières |
| Distribution des p | p-curve, excès de significativité, variance insuffisante (Carlisle) |
| Chiffres | uniformité des décimales, Benford, sommes de pourcentages et d'effectifs |
| Réutilisation de texte | shingles de 5 mots, Jaccard / MinHash |
| Bibliographie | DOI, années, doublons, auto-citations, **rétractations** |
| Transparence | données, code, préenregistrement, financement, éthique, puissance… |

## Documents de référence

- [`scientific-toolkit/CATALOGUE.md`](scientific-toolkit/CATALOGUE.md) — les 142 outils, catégorie par catégorie, avec licence, activité et rôle.
- [`scientific-toolkit/SOURCES.md`](scientific-toolkit/SOURCES.md) — couverture et profondeur des sources (1800 → aujourd'hui, archives patrimoniales incluses).
- [`scientific-toolkit/PLAYBOOKS.md`](scientific-toolkit/PLAYBOOKS.md) — six protocoles d'audit prêts à l'emploi.
- [`scientific-toolkit/INSTALL.md`](scientific-toolkit/INSTALL.md) — dépendances, GROBID/marker/docling, serveurs MCP.
- [`scientific-toolkit/MCP.md`](scientific-toolkit/MCP.md) — brancher PubMed/arXiv/OpenAlex/Zotero sur un agent.
- [`scientific-toolkit/LEGAL.md`](scientific-toolkit/LEGAL.md) — accès ouvert, Sci-Hub, licences, RGPD.

## Limite essentielle

Un audit automatique produit des **signaux**, pas des verdicts. Chaque constat
doit être vérifié sur le manuscrit, les données et le code avant toute conclusion
ou diffusion. Voir la section « Reproductibilité et limites » du README de la
boîte à outils.
