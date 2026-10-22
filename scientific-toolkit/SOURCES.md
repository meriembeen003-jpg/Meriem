# Sources scientifiques : couverture, profondeur historique, quotas

Aucun index ne couvre tout. La stratégie de ce kit est de **croiser** les sources,
parce que les lacunes de l'une sont l'information de l'autre : un article absent
d'OpenAlex mais présent dans Europe PMC et Crossref révèle un problème d'indexation
(ou une référence douteuse).

## 1. Index bibliographiques généraux

| Source | Volume (ordre de grandeur) | Profondeur | Clé API | Quota indicatif | Client ici |
|---|---|---|---|---|---|
| **OpenAlex** | ≈ 260 M travaux | 1800 → aujourd'hui | non | ~100 k/j, 10 req/s (polite pool avec `mailto`) | `pyalex`, `scitk.search.openalex` |
| **Crossref** | ≈ 160 M DOI | XIXᵉ → aujourd'hui (dépôts historiques) | non | 50 req/s (polite pool) | `habanero`, `scitk.search.crossref` |
| **Semantic Scholar** | ≈ 220 M papiers | XXᵉ → aujourd'hui | recommandée (gratuite) | 1 req/s sans clé, 10 avec | `semanticscholar`, `scitk.search.semanticscholar` |
| **Europe PMC** | ≈ 43 M abstracts, ≈ 10 M textes intégraux | 1900 → aujourd'hui | non | généreux, ~10 req/s | `scitk.search.europepmc` |
| **PubMed / NCBI** | ≈ 37 M références | 1950 → aujourd'hui (indexation rétrospective) | non (clé conseillée) | 3 req/s sans clé, 10 avec | `metapub`, `pymed`, `Bio.Entrez` |
| **arXiv** | ≈ 2,5 M préprints | 1991 → aujourd'hui | non | 1 req / 3 s | `arxiv.py` |
| **dblp** | ≈ 7 M notices | 1936 → aujourd'hui | non | ~1 req/s | API directe |
| **Scopus** | ≈ 90 M notices | 1788 → aujourd'hui | oui (Elsevier) | selon contrat | `pybliometrics` |
| **Web of Science** | ≈ 90 M notices | 1900 → aujourd'hui | oui (Clarivate) | selon contrat | export fichier |

**À retenir** : OpenAlex est la seule source *gratuite, sans clé* qui combine
couverture tous domaines, métadonnées riches (institutions, financements, concepts)
et profondeur jusqu'au XIXᵉ. Crossref est la source de vérité du DOI — un DOI
introuvable dans Crossref est un signal fort.

## 2. Texte intégral et accès ouvert

| Source | Volume | Usage | Client |
|---|---|---|---|
| **Unpaywall** | ≈ 50 M localisations OA | DOI → PDF légal, statut gold/green/hybrid/bronze | `unpywall`, `scitk.search.unpaywall` |
| **Europe PMC** | ≈ 10 M full texts | XML JATS téléchargeable | `scitk.search.europepmc.texte_integral` |
| **CORE** | ≈ 300 M documents agrégés | agrégateur de dépôts (littérature grise incluse) | `core_api_pylib` |
| **HAL** | ≈ 3 M documents | archive ouverte française, toutes disciplines | API REST |
| **PMC / PubMed Central** | ≈ 5 M | texte intégral biomédical | `metapub`, Europe PMC |
| **DOAJ** | ≈ 20 k revues | vérifier qu'une revue est en accès ouvert | API |
| **Zenodo / OSF / Dryad / Figshare / Dataverse** | millions de jeux de données | données et code associés aux articles | `osfclient`, `dataverse-client-python` |

## 3. « Les plus anciennes » : archives patrimoniales

C'est ici que se joue la couverture réelle de la littérature ancienne. Ces
collections sont numérisées, interrogeables et souvent téléchargeables.

| Source | Contenu | Période | Accès |
|---|---|---|---|
| **Gallica (BnF)** | presse, revues savantes, monographies françaises | XVᵉ → XXᵉ | API IIIF + SRU, MCP `mcp-bibliotheque_nationale_de_France` |
| **HathiTrust** | ≈ 18 M volumes numérisés | XVᵉ → XXIᵉ | API bibliographique, plein texte selon statut |
| **Internet Archive** (dont *Scholar*) | livres, revues, microfilms ; ≈ dizaines de millions d'articles | XVIIᵉ → XXIᵉ | API, `fatcat` |
| **Biodiversity Heritage Library** | littérature naturaliste | XVᵉ → XXIᵉ | API, `bhl-us` |
| **Open Library** | métadonnées de livres | tous siècles | API, `openlibrary` |
| **Europeana** | patrimoine culturel et scientifique européen | tous siècles | API (clé) |
| **Persée / Numdam / JSTOR** | revues savantes rétronumérisées | XIXᵉ–XXᵉ | Persée et Numdam ouverts ; JSTOR payant |
| **Google Books API** | ouvrages numérisés | tous siècles | API (quota) |
| **Wikidata / Scholia** | profils d'auteurs, institutions, revues | tous siècles | SPARQL |

**Stratégie recommandée pour une revue exhaustive « de toutes époques » :**

1. **Récent (1990 →)** : OpenAlex + Crossref + Europe PMC + arXiv + Semantic Scholar.
2. **XXᵉ siècle** : Crossref (dépôts rétrospectifs), PubMed (indexation ancienne),
   Scopus/WoS si disponibles, HathiTrust et Internet Archive pour les revues non indexées.
3. **Avant 1900** : Gallica, HathiTrust, BHL, Open Library, Europeana, Google Books.
4. **Littérature grise** : CORE, HAL, OSF Preprints, thèses (`theses.fr`, EThOS, OATD).
5. **Chaînage bibliographique** : citations avant/arrière (OpenCitations, Semantic
   Scholar, `citationchaser`) — souvent le seul moyen d'atteindre les travaux
   anciens mal indexés.

## 4. Citations, rétractations, intégrité

| Source | Contenu | Client |
|---|---|---|
| **OpenCitations** | ≈ 2 milliards de liens de citation, CC0 | `oc_meta` |
| **Crossref Event Data** | traces d'usage (blogs, Wikipedia, politique) | `event-data-percolator` |
| **Retraction Watch Database** | ≈ 60 000 rétractations (via Crossref, sur demande) | `retractions.importer_base_retraction_watch()` |
| **Crossref `update-to`** | rétractations, corrections, expressions de préoccupation | `scitk.search.crossref.statut_publication` |
| **PubPeer** | commentaires post-publication | API non officielle |
| **CODECHECK** | certificats de reproduction indépendante | `codecheckers/codecheck` |

## 5. Données disciplinaires

| Domaine | Source | Volume | Client |
|---|---|---|---|
| Biomédical | PubChem | ≈ 120 M composés | `PubChemPy` |
| Bioactivité | ChEMBL | ≈ 2,4 M composés | `chembl_webresource_client` |
| Structures | PDB | ≈ 220 k structures | `py-rcsb-api` |
| Génomique | Ensembl, GEO | génomes, transcriptomes | `ensembl-rest`, `GEOparse` |
| Protéines | UniProt | ≈ 250 M entrées | `bioservices` |
| Biodiversité | GBIF | ≈ 3 milliards d'occurrences | `pygbif` |
| Essais cliniques | ClinicalTrials.gov | ≈ 500 k essais | MCP dédié |
| ML reproductible | OpenML | millions de jeux de données et runs | `openml-python` |

## 6. Quotas : bonnes pratiques

- **Identifiez-vous** : `mailto` (OpenAlex, Crossref, Unpaywall) et `User-Agent`
  explicite placent votre trafic dans le « polite pool ».
- **Mettez en cache** : `scitk` écrit chaque réponse sur disque (TTL 24 h) ;
  une revue systématique se rejoue sans re-solliciter les API.
- **Paginatez proprement** : `per-page` max 200 (OpenAlex), `rows` max 1000 (Crossref).
- **Préférez les snapshots** pour les analyses massives : OpenAlex publie des
  snapshots S3 ; les dumps Crossref sont téléchargeables (analyse hors ligne,
  reproductible).
- **Respectez les licences** : OpenAlex CC0, Crossref métadonnées libres mais
  abstracts soumis au droit des éditeurs, Europe PMC selon statut de l'article.
