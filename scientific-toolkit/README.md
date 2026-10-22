# Boîte à outils — recherche & audit scientifiques

> 142 dépôts GitHub vérifiés · 74 archivés localement (34 Mo de code source) ·
> un moteur d'audit hors ligne de 35 tests · une couche de recherche multi-sources.

Ce dossier n'est pas une liste de liens. C'est un **poste de travail** :

1. un **catalogue vérifié** de 142 outils (étoiles, licence, activité, rôle en français) ;
2. un **miroir local** du code source des 74 outils les plus légers et les plus utiles —
   lisible sans réseau, installable sans dépendre de GitHub ;
3. une **bibliothèque Python `scitk`** qui recompose ces outils en un flux unique :
   recherche multi-sources → dédoublonnage → criblage PRISMA → extraction →
   **audit statistique et d'intégrité** → rapport traçable ;
4. des **démonstrations exécutables** (audit d'article, revue systématique,
   détection de doublons, catalogue).

---

## 1. Démarrage en 60 secondes

```bash
cd scientific-toolkit

# 1. aucune dépendance obligatoire pour l'audit (bibliothèque standard uniquement)
python3 -m scitk sources                       # sources de recherche disponibles
python3 -m unittest discover -s tests          # 35 tests, ~0,1 s

# 2. audit complet d'un article de démonstration
python3 -m scitk audit data/article_exemple.txt \
        --biblio data/references_exemple.bib \
        --descriptifs data/descriptifs_exemple.json \
        --out demos/out/audit_article

# 3. revue systématique PRISMA sur un corpus local
python3 -m scitk review data/corpus_exemple.csv \
        --nom "Remédiation en lecture" \
        --inclusion "lecture|reading" --exclusion "rodent|animal" \
        --sortie demos/out/revue

# 4. catalogue
python3 -m scitk catalogue --categorie audit
```

Sorties : rapports **Markdown + HTML + JSON** dans `demos/out/`.

Pour les fonctions réseau (OpenAlex, Crossref…) et les formats PDF, installer les
dépendances optionnelles :

```bash
python3 -m pip install -r requirements.txt     # voir INSTALL.md pour le détail
```

---

## 2. Ce que contient le dépôt

```
scientific-toolkit/
├── CATALOGUE.md          # 142 outils vérifiés, par catégorie, avec rôle et licence
├── README.md             # ce fichier
├── INSTALL.md            # dépendances, outils lourds (GROBID, marker, docling), MCP
├── PLAYBOOKS.md          # 6 protocoles d'audit prêts à l'emploi
├── SOURCES.md            # comparatif des sources : couverture, profondeur, quotas
├── MCP.md                # brancher PubMed/arXiv/OpenAlex/Zotero sur un agent LLM
├── LEGAL.md              # accès ouvert, Sci-Hub, licences, données personnelles
├── catalog/
│   ├── outils.json       # catalogue machine (142 entrées, métadonnées GitHub)
│   ├── outils.csv        # même catalogue en tableur
│   ├── verified.json     # réponses brutes de l'API GitHub
│   └── vendor_manifest.json / vendor_sizes.json
├── scitk/                # la bibliothèque (≈ 3 600 lignes, sans dépendance dure)
│   ├── audit/            # apa, grim, pcurve, chiffres, duplicates, refs,
│   │                     # retractions, transparency, report
│   ├── search/           # openalex, crossref, arxiv, europepmc,
│   │                     # semanticscholar, unpaywall, federated
│   ├── pipeline/         # review (PRISMA), export (CSV/RIS/BibTeX)
│   └── cli.py            # interface `python3 -m scitk`
├── data/                 # jeux de démonstration (article, biblio, corpus, rétractations)
├── demos/                # scripts exécutables + sorties générées
├── tests/                # 35 tests (statistiques, audit, clients hors ligne, PRISMA)
├── scripts/              # discovery, verification, clone, pruning, catalogue
└── vendor/               # 74 dépôts réels, classés par usage
    ├── decouverte/  fulltext/  parsing/  synthese/  revue_systematique/
    ├── audit/  mcp/  donnees/  metascience/
```

`vendor/` est un **miroir « source seule »** : code, tests, docs et configurations
sont conservés ; les binaires, modèles, images et jeux de données sont retirés
(ils représentaient 1,7 Go pour 15 500 fichiers). Les dépôts complets se
reclonent avec `python3 scripts/fetch.py --opt`.

---

## 3. La bibliothèque `scitk`

### 3.1 Audit statistique (`scitk.audit.apa`)

Inspiré de **statcheck** (Michele Nuijten) mais étendu : extraction des résultats
APA (`t`, `F`, `χ²`, `r`, `z`), recalcul de la p-value, puis comparaison à
l'intervalle compatible avec les arrondis.

Détections :

| Constat | Gravité | Signification |
|---|---|---|
| `erreur_decision` | critique | la conclusion significative/non significative change |
| `claim_contredit` | critique | le texte affirme « significatif », le recalcul dit non |
| `incoherence` | majeur/mineur | p rapportée incompatible avec la statistique |
| `incoherence_inegalite` | critique | `p < .05` alors que la p recalculée vaut .12 |
| `p_zero` | mineur | `p = .000` — impossible, écrire `p < .001` |
| `p_charniere` | info | p exactement au seuil : conclusion fragile |
| `r_invalide`, `df_suspect` | critique/majeur | valeurs mathématiquement impossibles |

Point méthodologique important : la p recalculée n'est **pas** comparée à une
valeur unique. `F(2, 45) = 3.21` désigne en réalité l'intervalle `[3.205, 3.215]` ;
la p correspondante varie de .0489 à .0507. Comparer à une valeur unique fabrique
de faux positifs — c'est la principale faiblesse des implémentations naïves.

### 3.2 GRIM, GRIMMER, SPRITE (`scitk.audit.grim`)

Si les données sont des entiers (Likert 1–5, score total), la moyenne et l'écart-type
ne peuvent pas prendre n'importe quelle valeur. Trois tests :

- **GRIM** — `M = 1.43` avec `n = 25` est impossible (la somme vaudrait 35,75) ;
- **GRIMMER** — vérifie l'existence simultanée d'une somme et d'une somme de carrés ;
- **SPRITE** — calcule les **bornes exactes** de l'écart-type pour une somme fixée :
  variance minimale (valeurs aussi égales que possible), variance maximale (valeurs
  aux bornes). `M = 4.90`, `SD = 0.05`, `n = 40`, échelle 1–5 → impossible
  (SD minimal atteignable : 0.304). Cette implémentation analytique est plus fiable
  qu'une recherche aléatoire et donne une réponse déterministe.

### 3.3 Distribution des p-values (`scitk.audit.pcurve`)

- **p-curve** — les p < .05 sont-elles concentrées près de 0 (effet réel) ou étalées
  (sélection) ? test binomial de la part sous .025 + test contre l'uniforme (KS) ;
- **excès de significativité** (Ioannidis & Trikalinos) ;
- **variance insuffisante** (style Carlisle) : `Var(p)` attendue ≈ 0.0833.

Ces tests ne valent que sur un **corpus** (revue, auteur, période), jamais sur un
article isolé. Le rapport le dit explicitement.

### 3.4 Chiffres (`scitk.audit.chiffres`)

Uniformité des décimales (χ² sur les chiffres terminaux, excès de 0/5), loi de
Benford, valeurs répétées dans un tableau, sommes de pourcentages ou d'effectifs
incohérentes.

### 3.5 Réutilisation de texte (`scitk.audit.duplicates`)

Normalisation → mots vides → shingles de 5 mots → Jaccard exact (petits corpus)
ou MinHash (gros corpus). Sert au dédoublonnage PRISMA **et** à la détection de
« paper mills » (abstracts quasi identiques).

### 3.6 Bibliographie (`scitk.audit.refs` + `retractions`)

Parseur BibTeX/RIS maison (tolérant), contrôle des DOI, années aberrantes,
doublons (DOI et titres), auto-citations, et **statut de rétractation** :
base d'exemple livrée + import de la *Retraction Watch Database* complète
(~60 000 rétractations) via `retractions.importer_base_retraction_watch()`.

### 3.7 Transparence (`scitk.audit.transparency`)

Dix indicateurs inspirés de **rtransparent** et **ODDPub** : données, code,
préenregistrement, financement, conflits d'intérêts, éthique, analyse de puissance,
protocole, limites, matériel supplémentaire. Chaque indicateur renvoie l'extrait
exact du texte — rien n'est inféré.

### 3.8 Rapports (`scitk.audit.report`)

Un rapport = synthèse + constats triés par gravité + tableau de recalcul +
transparence + distribution des p + GRIM + bibliographie + limites.
Trois formats : Markdown, HTML autonome (aucune dépendance), JSON.

**Barème du score global** (transparent, donc contestable) :
`55 % cohérence statistique + 25 % transparence + 20 % bibliographie`,
moins `2 points par constat critique` et `1 point par constat majeur`.

---

## 4. Recherche multi-sources

```python
from scitk.search.http import Client
from scitk.search import federated

res = federated.rechercher(Client(), "reading remediation randomized trial",
                           sources=["openalex", "crossref", "europepmc"],
                           limite=25, annee_min=2015)
for t in res.travaux:
    print(t.annee, t.titre[:80], t.doi, t.sources_multiples)
```

Chaque source renvoie un objet `Travail` normalisé (titre, DOI, auteurs, année,
revue, résumé, citations, accès ouvert, sujets). La fédération :

- **fusionne** les notices d'un même travail et conserve le meilleur champ de chacune ;
- **déduplique** par DOI puis par titre normalisé ;
- **mesure la couverture** : un travail vu dans une seule source est souvent un
  preprint, un chapitre ou un document peu indexé ;
- **tolère les pannes** : une source en erreur n'interrompt pas la recherche.

Côté clients, un cache disque et une temporisation par hôte évitent de marteler
les API (le « polite pool » de Crossref/OpenAlex est respecté via `mailto`).

> ⚠️ **Dans cet environnement d'exécution**, seuls GitHub, PyPI et npm sont
> joignables : les appels aux API scientifiques échouent (c'est attendu). Les
> clients sont donc testés avec des **fixtures** ; ils fonctionnent normalement
> depuis une machine connectée. La console web fournie fait ces appels **depuis
> le navigateur**, ce qui contourne la restriction du bac à sable.

---

## 5. Revue systématique (PRISMA 2020)

```python
from scitk.pipeline.review import RevueSystematique

revue = RevueSystematique(nom="Remédiation en lecture", question="…")
revue.criteres_inclusion = [r"lecture|reading"]
revue.criteres_exclusion = [r"rodent|animal"]
revue.identifies = len(travaux); revue.travaux = travaux
revue.dedupliquer().cribler().evaluer_acces()
revue.exporter("demos/out/revue")     # CSV, RIS, BibTeX, JSON, PRISMA, rapport
```

Chaque décision est journalisée (`*_journal.json`) : étape, règle appliquée,
nombre d'exclusions par motif. Le flux PRISMA est produit en texte et en Markdown,
prêt à être transposé dans un manuscrit.

---

## 6. Les 74 outils archivés — pourquoi eux

Le catalogue complet est dans **CATALOGUE.md**. Les choix d'archivage privilégient
les outils **légers, autonomes et utiles au pipeline** :

| Besoin | Outils archivés (exemples) |
|---|---|
| Interroger les index | `pyalex`, `habanero`, `arxiv.py`, `paperscraper`, `semanticscholar`, `pybliometrics`, `metapub`, `pymed`, `pubmed_parser` |
| Accès ouvert | `unpywall`, `fulltext-article-downloader`, `doi2pdf`, `PyPaperBot`, `SciDownl` ⚠️ |
| Lire un PDF | `pdfplumber`, `pdfminer.six`, `scipdf_parser`, `science-parse`, `paperetl`, `refextract` |
| Scientométrie | `pybibx`, `ScientoPy`, `litstudy`, `metaknowledge`, `novelpy`, `citationchaser`, `bibfix` |
| Revue systématique | `robotsearch`, `robotreviewer`, `trialstreamer`, `oddpub`, `rtransparent`, `PRISMA2020`, `robvis`, `paperfetcher` |
| Audit | `statcheck`, `statcheck-web`, `scrutiny`, `retractcheck`, `scipub`, `codecheck`, `gengscan`, `citeguard`, `retraction-check` |
| Agents | `paper-search-mcp`, `arxiv-mcp-server`, `PubMed-MCP-Server`, `biomcp`, `clinicaltrialsgov-mcp-server`, `zotero-mcp`, `openalex-research-mcp`, MCP Gallica (BnF) |
| Données | `dataverse-client-python`, `osfclient`, `openml-python`, `GEOparse`, `py-rcsb-api`, `pygbif`, `pdb-tools` |

Les outils lourds (GROBID, marker, MinerU, docling, paper-qa, OpenScholar, STORM,
ASReview, bibliometrix, metafor…) restent **documentés et installables** :
voir `INSTALL.md`. Ils ne sont pas clonés pour rester dans un budget de stockage
raisonnable.

---

## 7. Reproductibilité et limites

**Reproductibilité.** Audit déterministe, sans aléa (SPRITE utilise des bornes
analytiques, pas d'échantillonnage) ; 35 tests couvrent les distributions
(valeurs vérifiées par intégration numérique), l'extraction APA, GRIM/GRIMMER/SPRITE,
le parsing bibliographique, les doublons, le pipeline PRISMA et les clients HTTP.

**Limites — à lire avant toute conclusion.**

- Un constat n'est **pas** une preuve de fraude : arrondis, tests unilatéraux,
  corrections de continuité, modèles mixtes ou p-values rapportées avec une autre
  convention produisent des écarts légitimes.
- L'extraction APA par expression régulière rate les formulations non standard
  (tableaux, p-values en figures, `p = .03` sans statistique).
- GRIM/GRIMMER supposent des **données entières** : inapplicables aux mesures
  continues (temps de réaction, scores standardisés).
- Les tests de distribution exigent un corpus ; sur un article isolé, ils sont
  indicatifs.
- La base de rétractations livrée est un **échantillon pédagogique** de 8 cas
  documentés. Pour un audit réel : importer la base Retraction Watch complète.
- Les étoiles GitHub mesurent la notoriété, pas la validité scientifique.

---

## 8. Éthique et droit

- Voie privilégiée pour le texte intégral : **accès ouvert** (Unpaywall, OpenAlex,
  Europe PMC, HAL, Zenodo, dépôts institutionnels).
- Les outils de contournement (Sci-Hub, LibGen : `PyPaperBot`, `SciDownl`) sont
  archivés à titre documentaire ; leur usage peut violer le droit d'auteur et les
  conditions des éditeurs. Voir `LEGAL.md`.
- Les audits produisent des **données sur des personnes** (auteurs) : à traiter
  comme telles (RGPD), avec droit de réponse et vérification humaine avant toute
  diffusion.
