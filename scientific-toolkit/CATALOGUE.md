# Catalogue vérifié — recherche & audit scientifiques sur GitHub

**142 dépôts** · 798 219 étoiles cumulées · 74 archivés localement (34.4 Mo) · 1 non vérifiables

Chaque entrée a été contrôlée via l'API GitHub (existence, étoiles, licence, dernière activité, archivage). Les notes en français expliquent *à quoi sert* l'outil et *pourquoi* il compte pour la recherche ou l'audit.

> ⚠️ Les outils de téléchargement de PDF hors accès ouvert (Sci-Hub, LibGen) sont signalés dans la catégorie « Texte intégral ». Leur usage peut violer les conditions des éditeurs : ce kit privilégie systématiquement les voies légales (Unpaywall, OpenAlex, Europe PMC, dépôts institutionnels). Voir `LEGAL.md`.

## Sommaire

- [Découverte & métadonnées](#découverte--métadonnées) — 36 outils
- [Texte intégral](#texte-intégral) — 6 outils
- [Extraction & structuration](#extraction--structuration) — 21 outils
- [Synthèse & RAG scientifique](#synthèse--rag-scientifique) — 20 outils
- [Revue systématique](#revue-systématique) — 17 outils
- [Audit & intégrité](#audit--intégrité) — 11 outils
- [MCP & agents](#mcp--agents) — 13 outils
- [Données & dépôts](#données--dépôts) — 15 outils
- [Corpus massifs & méta-science](#corpus-massifs--méta-science) — 3 outils

## Vue d'ensemble

| Catégorie | Outils | Étoiles cumulées | Archivés |
|---|---|---|---|
| Découverte & métadonnées | 36 | 26 479 | 24 |
| Texte intégral | 6 | 1 563 | 5 |
| Extraction & structuration | 21 | 464 944 | 6 |
| Synthèse & RAG scientifique | 20 | 256 762 | 5 |
| Revue systématique | 17 | 2 459 | 9 |
| Audit & intégrité | 11 | 430 | 9 |
| MCP & agents | 13 | 12 984 | 9 |
| Données & dépôts | 15 | 31 160 | 7 |
| Corpus massifs & méta-science | 3 | 1 438 | 0 |

## Découverte & métadonnées

*Interroger les index, résoudre les DOI, explorer toutes les époques (archives historiques incluses)*

| Étoiles | Dépôt | Licence | Dernier push | Rôle | Local |
|---:|---|---|---|---|---|
| 6 773 | [internetarchive/openlibrary](https://github.com/internetarchive/openlibrary) | AGPL-3.0 | 2026-10-22 | Open Library : métadonnées de livres et fonds anciens ; API + édition. |  |
| 5 242 | [biopython/biopython](https://github.com/biopython/biopython) | NOASSERTION | 2026-10-22 | Entrez/PubMed/GenBank/UniProt/PDB : la voie NCBI historique et complète. |  |
| 1 882 | [scholarly-python-package/scholarly](https://github.com/scholarly-python-package/scholarly) | Unlicense | 2026-03-24 | Google Scholar : profils, publications, citations — indexe l'ancien comme le récent. | 🗄️ |
| 1 721 | [zotero/translators](https://github.com/zotero/translators) | — | 2026-10-19 | Traducteurs Zotero : extraction de métadonnées depuis des milliers de sites éditeurs. |  |
| 1 552 | [lukasschwab/arxiv.py](https://github.com/lukasschwab/arxiv.py) | MIT | 2026-10-05 | Client arXiv : préprints 1991→aujourd'hui, tous champs, pagination robuste. | 🗄️ |
| 1 433 | [urschrei/pyzotero](https://github.com/urschrei/pyzotero) | NOASSERTION | 2026-10-20 | API Zotero : bibliothèques, collections, annotations, export BibTeX. | 🗄️ |
| 1 063 | [J535D165/recordlinkage](https://github.com/J535D165/recordlinkage) | BSD-3-Clause | 2024-02-21 | Record linkage / dédoublonnage : éliminer les doublons d'une revue systématique. | 🗄️ |
| 738 | [titipata/pubmed_parser](https://github.com/titipata/pubmed_parser) | MIT | 2025-07-31 | Parsing d'articles PubMed Central structurés (sections, figures, tables). | 🗄️ |
| 673 | [massimoaria/bibliometrix](https://github.com/massimoaria/bibliometrix) | NOASSERTION | 2026-10-19 | Suite R de référence en scientométrie : cartes thématiques, co-citation, réseaux. |  |
| 574 | [sciunto-org/python-bibtexparser](https://github.com/sciunto-org/python-bibtexparser) | MIT | 2026-10-05 | Parsing/écriture BibTeX robuste pour l'audit de bibliographies. | 🗄️ |
| 544 | [jannisborn/paperscraper](https://github.com/jannisborn/paperscraper) | MIT | 2026-10-14 | Recherche multi-sources : PubMed, arXiv, bioRxiv, medRxiv, chemRxiv, OpenAlex ; export JSON/CSV. | 🗄️ |
| 503 | [pybliometrics-dev/pybliometrics](https://github.com/pybliometrics-dev/pybliometrics) | NOASSERTION | 2026-09-27 | Client Scopus complet (clé Elsevier) : 90M+ notices depuis 1970, affiliations, financements. | 🗄️ |
| 484 | [danielnsilva/semanticscholar](https://github.com/danielnsilva/semanticscholar) | MIT | 2026-08-01 | Client Semantic Scholar (220M+ papiers) : abstracts, citations, TLDR, recommandations, S2ORC. | 🗄️ |
| 440 | [naivenaive/EasyPubMed](https://github.com/naivenaive/EasyPubMed) | MIT | 2026-07-19 | Extraction massive de PubMed en un appel, export CSV/Excel. |  |
| 427 | [J535D165/pyalex](https://github.com/J535D165/pyalex) | MIT | 2026-10-05 | Client Python OpenAlex : 260M+ travaux, 1800→aujourd'hui, citations, auteurs, institutions. Sans clé API. | 🗄️ |
| 256 | [WDscholia/scholia](https://github.com/WDscholia/scholia) | GPL-3.0 | 2026-07-12 | Profils scientifiques sur Wikidata : auteurs→travaux→institutions via SPARQL massif. |  |
| 252 | [sckott/habanero](https://github.com/sckott/habanero) | MIT | 2026-10-16 | Client Crossref : 160M+ DOI, références, rétractations, financements, peer-review. Couverture rétrospective très profonde. | 🗄️ |
| 229 | [NLeSC/litstudy](https://github.com/NLeSC/litstudy) | Apache-2.0 | 2025-05-27 | LitStudy : pipelines bibliographiques (Scopus, WoS, PubMed, arXiv) + cartes de science. | 🗄️ |
| 223 | [Valdecy/pybibx](https://github.com/Valdecy/pybibx) | NOASSERTION | 2026-06-21 | Scientométrie en Python : performance, réseaux, clustering, cartes. | 🗄️ |
| 214 | [gijswobben/pymed](https://github.com/gijswobben/pymed) | MIT | 2021-12-07 | PubMed/NCBI E-utilities minimal et fiable (XML → DataFrame). | 🗄️ |
| 183 | [UWNETLAB/metaknowledge](https://github.com/UWNETLAB/metaknowledge) | GPL-2.0 | 2022-06-09 | Manipulation de corpus hétérogènes (WoS, Scopus, PubMed, ProQuest) et réseaux. | 🗄️ |
| 166 | [dissemin/dissemin](https://github.com/dissemin/dissemin) | AGPL-3.0 | 2021-02-27 | Disponibilité OA d'un article + dépôt institutionnel (agrège HAL, Zenodo, arXiv). | ⚠️ archivé |
| 162 | [nealhaddaway/citationchaser](https://github.com/nealhaddaway/citationchaser) | — | 2025-03-21 | Citation chasing avant/arrière pour revues systématiques (Lens.org / OpenAlex). | 🗄️ |
| 160 | [metapub/metapub](https://github.com/metapub/metapub) | Apache-2.0 | 2026-09-28 | Toolkit NCBI : résolution PMID/DOI, métadonnées PubMed, téléchargement full-text PMC. | 🗄️ |
| 150 | [ourresearch/openalex-api-tutorials](https://github.com/ourresearch/openalex-api-tutorials) | MIT | 2024-04-25 | Notebooks officiels OpenAlex : requêtes complexes, snapshots, analyses de masse. | 🗄️ |
| 121 | [internetarchive/fatcat](https://github.com/internetarchive/fatcat) | NOASSERTION | 2024-07-31 | Internet Archive Scholar : dizaines de millions d'articles ; couverture historique unique (revues anciennes, OA, preprints). |  |
| 94 | [jpruiz84/ScientoPy](https://github.com/jpruiz84/ScientoPy) | MIT | 2026-09-28 | Scientométrie clé en main (publications, citations, co-occurrence, progression temporelle). | 🗄️ |
| 67 | [ropensci/roadoi](https://github.com/ropensci/roadoi) | NOASSERTION | 2024-09-26 | Client R Unpaywall (variante R). |  |
| 37 | [Kwirtz/novelpy](https://github.com/Kwirtz/novelpy) | MIT | 2024-06-13 | Indicateurs de nouveauté (CD index, atypicality) : détecter les ruptures scientifiques. | 🗄️ |
| 36 | [unpywall/unpywall](https://github.com/unpywall/unpywall) | MIT | 2024-02-19 | Unpaywall : localise le PDF légal en accès ouvert pour un DOI (50M+ OA). | 🗄️ |
| 28 | [nealhaddaway/bibfix](https://github.com/nealhaddaway/bibfix) | NOASSERTION | 2026-02-02 | Réparation/normalisation de données bibliographiques (DOI, années, revues). | 🗄️ |
| 25 | [gbhl/bhl-us](https://github.com/gbhl/bhl-us) | NOASSERTION | 2026-10-08 | Biodiversity Heritage Library : littérature naturaliste historique numérisée (XVIIIe→XXe). |  |
| 12 | [Kryzo/mcp-bibliotheque_nationale_de_France](https://github.com/Kryzo/mcp-bibliotheque_nationale_de_France) | — | 2025-03-21 | MCP Gallica (BnF) : accès aux collections numérisées françaises, y compris textes anciens. | 🗄️ |
| 9 | [opencitations/oc_meta](https://github.com/opencitations/oc_meta) | ISC | 2026-10-12 | OpenCitations Meta : 2 milliards+ de liens de citation en accès ouvert, CC0. |  |
| 4 | [Open-Models/core_api_pylib](https://github.com/Open-Models/core_api_pylib) | AGPL-3.0 | 2022-12-30 | Client CORE : 300M+ documents OA agrégés (dont littérature grise et archives). | 🗄️ |
| 2 | [crossref/event-data-percolator](https://github.com/CrossRef/event-data-percolator) | MIT | 2018-09-20 | Crossref Event Data : traces d'usage (blogs, Wikipedia) pour audit d'impact. | ⚠️ archivé |

## Texte intégral

*Récupérer les PDF : accès ouvert d'abord, autres voies ensuite*

| Étoiles | Dépôt | Licence | Dernier push | Rôle | Local |
|---:|---|---|---|---|---|
| 659 | [ferru97/PyPaperBot](https://github.com/ferru97/PyPaperBot) | MIT | 2024-12-08 | Téléchargement massif de PDF par mots-clés/DOI (arXiv, Sci-Hub), dédoublonnage. | 🗄️ |
| 529 | [Impactstory/unpaywall](https://github.com/ourresearch/unpaywall-extension) | MIT | 2025-01-02 | Code et données du service Unpaywall (source de vérité OA). |  |
| 329 | [Tishacy/SciDownl](https://github.com/Tishacy/SciDownl) | MIT | 2024-02-11 | Téléchargeur Sci-Hub par DOI/PMID/URL avec résolution automatique. | 🗄️ |
| 27 | [computron/fulltext-article-downloader](https://github.com/computron/fulltext-article-downloader) | BSD-3-Clause | 2026-09-29 | Téléchargement automatisé de full-texts depuis une liste d'identifiants. | 🗄️ |
| 17 | [byigitt/doi2pdf](https://github.com/byigitt/doi2pdf) | — | 2025-05-15 | DOI → PDF en accès ouvert, cascade de résolveurs, CLI simple. | 🗄️ |
| 2 | [heidihelena/fullvahti](https://github.com/heidihelena/fullvahti) | Apache-2.0 | 2026-07-30 | Extension Zotero : récupère les PDF OA (Unpaywall, PMC) pour toute une bibliothèque. | 🗄️ |

## Extraction & structuration

*Transformer un PDF en données exploitables*

| Étoiles | Dépôt | Licence | Dernier push | Rôle | Local |
|---:|---|---|---|---|---|
| 91 527 | [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | Apache-2.0 | 2026-09-16 | OCR industriel (80+ langues) pour littérature scannée. |  |
| 82 305 | [opendatalab/MinerU](https://github.com/opendatalab/MinerU) | NOASSERTION | 2026-10-19 | Extraction de PDF scientifiques à grande échelle (formules LaTeX, tableaux). |  |
| 77 114 | [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) | Apache-2.0 | 2026-10-22 | OCR de référence (100+ langues) : indispensable pour les archives numérisées. |  |
| 69 372 | [docling-project/docling](https://github.com/docling-project/docling) | MIT | 2026-10-22 | Docling (IBM) : PDF/DOCX/PPTX → JSON structuré, layout + tableaux. |  |
| 40 590 | [datalab-to/marker](https://github.com/datalab-to/marker) | Apache-2.0 | 2026-10-22 | PDF → Markdown/JSON rapide (SOTA open source) : tableaux, équations, ordre de lecture. |  |
| 21 519 | [VikParuchuri/surya](https://github.com/datalab-to/surya) | Apache-2.0 | 2026-10-22 | OCR multilingue + layout + ordre de lecture, précis sur scans anciens. |  |
| 15 590 | [unstructured-io/unstructured](https://github.com/Unstructured-IO/unstructured) | Apache-2.0 | 2026-10-22 | Découpage sémantique de documents (titres, listes, tableaux) pour RAG. |  |
| 10 967 | [pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF) | AGPL-3.0 | 2026-10-22 | Extraction/rendu PDF très rapide (texte, images, annotations, tableaux). |  |
| 10 839 | [jsvine/pdfplumber](https://github.com/jsvine/pdfplumber) | MIT | 2026-10-15 | Extraction de tableaux et texte avec coordonnées (audit des chiffres publiés). | 🗄️ |
| 10 088 | [facebookresearch/nougat](https://github.com/facebookresearch/nougat) | MIT | 2025-02-21 | OCR scientifique NeurIPS : équations et structure → Markdown. |  |
| 10 052 | [opendatalab/PDF-Extract-Kit](https://github.com/opendatalab/PDF-Extract-Kit) | AGPL-3.0 | 2025-01-03 | Boîte à outils layout/OCR/formule/tableau pour PDF académiques. |  |
| 7 044 | [pdfminer/pdfminer.six](https://github.com/pdfminer/pdfminer.six) | MIT | 2026-03-13 | Extraction fine de texte et positions pour l'analyse de mise en page. | 🗄️ |
| 5 190 | [kermitt2/grobid](https://github.com/grobidOrg/grobid) | Apache-2.0 | 2026-10-22 | Référence absolue : PDF scientifique → XML structuré (références, affiliations, sections, tableaux). |  |
| 4 102 | [apache/tika](https://github.com/apache/tika) | Apache-2.0 | 2026-10-22 | Extraction texte/métadonnées pour 1500+ formats. |  |
| 3 842 | [camelot-dev/camelot](https://github.com/camelot-dev/camelot) | MIT | 2026-10-14 | Extraction de tableaux PDF (stream/lattice) pour récupérer les données publiées. |  |
| 2 319 | [chezou/tabula-py](https://github.com/chezou/tabula-py) | MIT | 2024-12-05 | Wrapper Tabula : tableaux PDF → DataFrame. |  |
| 707 | [allenai/science-parse](https://github.com/allenai/science-parse) | Apache-2.0 | 2024-05-26 | Parseur sémantique de papiers (métadonnées, sections, références) — historique AllenAI. | 🗄️ |
| 700 | [neuml/paperetl](https://github.com/neuml/paperetl) | Apache-2.0 | 2025-12-07 | ETL de papiers (PDF, XML, CSV, JSON) vers SQLite pour recherche plein texte. | 🗄️ |
| 478 | [allenai/s2orc-doc2json](https://github.com/allenai/s2orc-doc2json) | Apache-2.0 | 2024-04-11 | PDF → S2ORC JSON (sections, références liées, figures) : standard de fouille de corpus. |  |
| 456 | [titipata/scipdf_parser](https://github.com/titipata/scipdf_parser) | MIT | 2024-03-21 | PDF scientifique → texte + figures + sections. | 🗄️ |
| 143 | [inspirehep/refextract](https://github.com/inspirehep/refextract) | GPL-2.0 | 2026-10-02 | Extraction de références bibliographiques depuis du texte brut (CERN). | 🗄️ |

## Synthèse & RAG scientifique

*Lire, résumer, comparer, générer des revues*

| Étoiles | Dépôt | Licence | Dernier push | Rôle | Local |
|---:|---|---|---|---|---|
| 52 618 | [run-llama/llama_index](https://github.com/run-llama/llama_index) | MIT | 2026-10-21 | Orchestration de données pour LLM : connecteurs, index, agents documentaires. |  |
| 40 269 | [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) | MIT | 2026-10-22 | RAG par graphe rapide et économique, adapté aux gros corpus. |  |
| 36 411 | [microsoft/graphrag](https://github.com/microsoft/graphrag) | MIT | 2026-10-20 | GraphRAG : indexation en graphe pour questions globales sur un corpus. |  |
| 31 681 | [stanford-oval/storm](https://github.com/stanford-oval/storm) | MIT | 2025-09-30 | STORM : rédaction d'articles encyclopédiques avec recherche multi-perspective et citations. |  |
| 30 246 | [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | Apache-2.0 | 2026-10-10 | Agent de recherche autonome multi-sources (rapports cités). |  |
| 26 811 | [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | Apache-2.0 | 2026-10-22 | Pipelines RAG/QA en production (retrieval, rerank, génération). |  |
| 13 027 | [neuml/txtai](https://github.com/neuml/txtai) | Apache-2.0 | 2026-10-21 | Recherche sémantique + pipelines RAG, indexation de millions d'abstracts en local. |  |
| 9 452 | [Future-House/paper-qa](https://github.com/Future-House/paper-qa) | Apache-2.0 | 2026-10-20 | PaperQA2 : agent qui lit des milliers de PDF, répond avec citations et détecte les contradictions. |  |
| 9 386 | [LearningCircuit/local-deep-research](https://github.com/LearningCircuit/local-deep-research) | MIT | 2026-10-22 | Deep research 100% local (Ollama) : aucune donnée ne sort de la machine. |  |
| 1 718 | [allenai/scibert](https://github.com/allenai/scibert) | Apache-2.0 | 2022-02-22 | SciBERT : embeddings spécialisés science (base de tout classifieur scientifique). | 🗄️ |
| 1 673 | [AkariAsai/OpenScholar](https://github.com/AkariAsai/OpenScholar) | Apache-2.0 | 2025-08-13 | RAG scientifique open source (8B) surpassant GPT-4o sur les revues de littérature. |  |
| 1 211 | [facebookresearch/BLINK](https://github.com/facebookresearch/BLINK) | MIT | 2023-09-21 | Entity linking (gènes, maladies, produits) : brique clé de l'extraction de connaissances. | 🗄️ |
| 637 | [lamm-mit/SciAgentsDiscovery](https://github.com/lamm-mit/SciAgentsDiscovery) | Apache-2.0 | 2025-05-10 | SciAgents : graphes de connaissances + agents pour générer des hypothèses interdisciplinaires. |  |
| 476 | [manubot/manubot](https://github.com/manubot/manubot) | NOASSERTION | 2026-08-02 | Écriture scientifique ouverte et automatisée (citations, reproductibilité). |  |
| 284 | [Future-House/aviary](https://github.com/Future-House/aviary) | Apache-2.0 | 2026-10-20 | Aviary : environnements d'agents pour tâches scientifiques réelles. |  |
| 279 | [allenai/scifact](https://github.com/allenai/scifact) | NOASSERTION | 2023-10-15 | SciFact : vérification de claims scientifiques contre la littérature. | 🗄️ |
| 213 | [citation-js/citation-js](https://github.com/citation-js/citation-js) | MIT | 2026-10-22 | Citation.js : conversion BibTeX/RIS/Wikidata → CSL, formatage de références. |  |
| 145 | [allenai/specter2](https://github.com/allenai/SPECTER2) | Apache-2.0 | 2026-02-24 | SPECTER2 : embeddings d'articles (citation-informed) pour cartographier la littérature. | 🗄️ |
| 134 | [Future-House/lab-bench](https://github.com/Future-House/LAB-Bench) | CC-BY-SA-4.0 | 2026-10-13 | LAB-Bench : référence d'évaluation des LLM sur la recherche biologique. |  |
| 91 | [allenai/scirepeval](https://github.com/allenai/scirepeval) | Apache-2.0 | 2026-05-05 | Benchmark d'extraction d'information scientifique. | 🗄️ |

## Revue systématique

*PRISMA, screening, risque de biais, méta-analyse*

| Étoiles | Dépôt | Licence | Dernier push | Rôle | Local |
|---:|---|---|---|---|---|
| 1 049 | [ASReview/asreview](https://github.com/asreview/asreview) | Apache-2.0 | 2026-10-20 | ASReview LAB : screening par active learning, standard académique (PRISMA). |  |
| 316 | [wviechtb/metafor](https://github.com/wviechtb/metafor) | — | 2026-10-16 | metafor (R) : référence mondiale des méta-analyses (effets mixtes, hétérogénéité, biais de publication). |  |
| 299 | [prisma-flowdiagram/PRISMA2020](https://github.com/prisma-flowdiagram/PRISMA2020) | NOASSERTION | 2026-09-05 | Diagrammes de flux PRISMA 2020 conformes (R/Shiny). | 🗄️ |
| 179 | [ijmarshall/robotreviewer](https://github.com/ijmarshall/robotreviewer) | GPL-3.0 | 2022-07-18 | RobotReviewer : évaluation automatique du risque de biais (RoB 2). | 🗄️ |
| 148 | [htlin222/meta-pipe](https://github.com/htlin222/meta-pipe) | NOASSERTION | 2026-09-23 | Pipeline méta-analyse de bout en bout assisté par LLM (PRISMA + calculs). |  |
| 105 | [guido-s/meta](https://github.com/guido-s/meta) | GPL-2.0 | 2026-10-16 | meta (R) : méta-analyses + graphiques forest/funnel conformes Cochrane. |  |
| 80 | [mcguinlu/robvis](https://github.com/mcguinlu/robvis) | NOASSERTION | 2026-09-02 | robvis : visualisations Risk-of-Bias (RoB2, ROBINS-I) prêtes à publier. | 🗄️ |
| 59 | [mjwestgate/revtools](https://github.com/mjwestgate/revtools) | — | 2026-07-07 | revtools (R) : dédoublonnage et screening de bibliographies. |  |
| 46 | [MathiasHarrer/dmetar](https://github.com/MathiasHarrer/dmetar) | NOASSERTION | 2025-05-30 | dmetar : companion du guide 'Doing Meta-Analysis in R'. |  |
| 45 | [quest-bih/oddpub](https://github.com/quest-bih/oddpub) | AGPL-3.0 | 2026-08-31 | ODDPub : détection automatique des déclarations de données/code ouverts. | 🗄️ |
| 44 | [bwallace/abstrackr-web](https://github.com/bwallace/abstrackr-web) | — | 2021-04-22 | Abstrackr : screening semi-automatique par apprentissage actif. |  |
| 24 | [ijmarshall/robotsearch](https://github.com/ijmarshall/robotsearch) | GPL-3.0 | 2023-03-25 | RobotSearch : filtre les RCT dans les résultats (économise ~90% du screening). | 🗄️ |
| 23 | [ijmarshall/trialstreamer](https://github.com/ijmarshall/trialstreamer) | — | 2022-06-24 | Trialstreamer : méta-analyses vivantes, PICO extraits automatiquement des RCT. | 🗄️ |
| 21 | [paperfetcher/paperfetcher](https://github.com/paperfetcher/paperfetcher) | MIT | 2024-07-13 | Paperfetcher : handsearching et citation chasing automatisés. | 🗄️ |
| 17 | [ijmarshall/cochrane-nlp](https://github.com/ijmarshall/cochrane-nlp) | GPL-3.0 | 2016-05-17 | Outils NLP Cochrane (PICO, similarité, ranking). |  |
| 4 | [SisonkeBiotik-Africa/Systematic-Review-Automation](https://github.com/SisonkeBiotik-Africa/Systematic-Review-Automation) | GPL-2.0 | 2021-10-29 | Automatisation des tâches de revue systématique. | 🗄️ |
| 0 | [quest-bih/rtransparent](https://github.com/quest-bih/rtransparent) | GPL-3.0 | 2025-10-06 | rtransparent : 6 indicateurs de transparence (données, code, COI, financement, registre). | 🗄️ |

## Audit & intégrité

*Vérifier les chiffres, les références, les rétractations*

| Étoiles | Dépôt | Licence | Dernier push | Rôle | Local |
|---:|---|---|---|---|---|
| 196 | [MicheleNuijten/statcheck](https://github.com/MicheleNuijten/statcheck) | — | 2026-10-22 | statcheck : recalcule les p-values publiées (APA) → incohérences, erreurs de décimale. | 🗄️ |
| 180 | [ropensci/rcrossref](https://github.com/ropensci/rcrossref) | NOASSERTION | 2025-08-22 | rcrossref (R) : Crossref + statut de rétractation dans un pipeline R. |  |
| 23 | [libscie/retractcheck](https://github.com/libscie/retractcheck) | NOASSERTION | 2020-11-04 | retractcheck : vérifie un DOI/texte contre la Retraction Watch Database. | 🗄️ |
| 12 | [codecheckers/codecheck](https://github.com/codecheckers/codecheck) | NOASSERTION | 2026-10-20 | CODECHECK : procédure d'audit reproductible (exécution indépendante du code). | 🗄️ |
| 11 | [lhdjung/scrutiny](https://github.com/lhdjung/scrutiny) | NOASSERTION | 2026-10-19 | scrutiny (R) : GRIM, GRIMMER, SPRITE, décimales — implémentation de référence. | 🗄️ |
| 3 | [dpagliaccio/scipub](https://github.com/dpagliaccio/scipub) | GPL-3.0 | 2024-03-08 | scipub (R) : erreurs de reporting statistique et données manquantes. | 🗄️ |
| 2 | [MicheleNuijten/statcheck-web](https://github.com/MicheleNuijten/statcheck-web) | MIT | 2026-10-22 | Interface web statcheck pour vérifier un PDF publié. | 🗄️ |
| 2 | [xntj-ai/gengscan](https://github.com/xntj-ai/gengscan) | MIT | 2026-06-16 | Gengscan : détection d'empreintes d'intégrité / paper mills par LLM. | 🗄️ |
| 1 | [wedo911/citeguard](https://github.com/wedo911/citeguard) | MIT | 2026-08-26 | Contrôle des rétractations, corrections et expressions de préoccupation. | 🗄️ |
| 0 | [JesseRWeigel/retraction-check](https://github.com/JesseRWeigel/retraction-check) | MIT | 2026-07-27 | Vérification de citations contre les données de rétractation Crossref. | 🗄️ |
| ? | [CenterForOpenScience/TOP_Factor](https://github.com/CenterForOpenScience/TOP_Factor) | — | — | TOP Factor : notation des politiques de transparence des revues. |  |

## MCP & agents

*Exposer ces sources à un agent LLM*

| Étoiles | Dépôt | Licence | Dernier push | Rôle | Local |
|---:|---|---|---|---|---|
| 5 527 | [54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp) | MIT | 2026-10-16 | MCP Zotero : la bibliothèque personnelle devient une base interrogeable. |  |
| 3 229 | [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) | Apache-2.0 | 2026-10-08 | MCP arXiv : recherche, téléchargement, lecture locale des PDF. | 🗄️ |
| 2 890 | [openags/paper-search-mcp](https://github.com/openags/paper-search-mcp) | MIT | 2026-10-02 | MCP multi-sources (arXiv, PubMed, bioRxiv, Semantic Scholar...) : tout un moteur scientifique exposé à l'agent. | 🗄️ |
| 663 | [genomoncology/biomcp](https://github.com/genomoncology/biomcp) | MIT | 2026-10-22 | BioMCP : PubMed/PubTator/ClinVar/MyVariant — biomédical unifié. |  |
| 188 | [Dianel555/paper-search-mcp-nodejs](https://github.com/Dianel555/paper-search-mcp-nodejs) | MIT | 2026-09-20 | Port Node.js du MCP paper-search (13 sources). |  |
| 165 | [zongmin-yu/semantic-scholar-fastmcp-mcp-server](https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server) | MIT | 2026-03-20 | MCP Semantic Scholar : recherche, citations, recommandations. | 🗄️ |
| 132 | [JackKuo666/PubMed-MCP-Server](https://github.com/JackKuo666/PubMed-MCP-Server) | MIT | 2025-05-08 | MCP PubMed : recherche et abstracts/full-text. | 🗄️ |
| 99 | [cyanheads/clinicaltrialsgov-mcp-server](https://github.com/cyanheads/clinicaltrialsgov-mcp-server) | Apache-2.0 | 2026-10-17 | MCP ClinicalTrials.gov : essais, critères d'éligibilité, résultats. |  |
| 57 | [oksure/openalex-research-mcp](https://github.com/oksure/openalex-research-mcp) | MIT | 2026-10-01 | MCP OpenAlex : recherche et analyse de 240M+ travaux. | 🗄️ |
| 16 | [aringadre76/mcp-for-research](https://github.com/aringadre76/mcp-for-research) | MIT | 2026-05-12 | MCP consolidant PubMed, Google Scholar et autres sources. | 🗄️ |
| 11 | [mlava/scholar-sidekick-mcp](https://github.com/mlava/scholar-sidekick-mcp) | MIT | 2026-10-15 | Résolution d'identifiants savants (DOI/PMID/ISBN/arXiv) + métadonnées. | 🗄️ |
| 6 | [surendranb/find-research-papers-mcp](https://github.com/surendranb/find-research-papers-mcp) | MIT | 2026-10-03 | MCP multi-sources (arXiv, OpenAlex, Crossref, PubMed). | 🗄️ |
| 1 | [JackKuo666/paperscraper-MCP-Server](https://github.com/JackKuo666/paperscraper-MCP-Server) | — | 2025-03-19 | MCP paperscraper : métadonnées bioRxiv/medRxiv/chemRxiv/arXiv. | 🗄️ |

## Données & dépôts

*Accéder aux jeux de données et aux dépôts*

| Étoiles | Dépôt | Licence | Dernier push | Rôle | Local |
|---:|---|---|---|---|---|
| 22 078 | [huggingface/datasets](https://github.com/huggingface/datasets) | Apache-2.0 | 2026-10-22 | Accès unifié aux corpus (S2ORC, peS2o, arXiv, PubMed) via une API. |  |
| 5 142 | [ckan/ckan](https://github.com/ckan/ckan) | NOASSERTION | 2026-10-21 | CKAN : moteur de portails open data (milliers de portails publics). |  |
| 1 048 | [zenodo/zenodo](https://github.com/zenodo/zenodo) | GPL-2.0 | 2026-03-13 | Zenodo (CERN) : dépôt universel, DOI pour données et logiciels. |  |
| 517 | [mcs07/PubChemPy](https://github.com/mcs07/PubChemPy) | MIT | 2025-09-08 | PubChem : 110M+ composés, propriétés, bibliographie associée. |  |
| 461 | [haddocking/pdb-tools](https://github.com/haddocking/pdb-tools) | NOASSERTION | 2026-06-10 | pdb-tools : manipulation de fichiers PDB pour audit structural. | 🗄️ |
| 452 | [chembl/chembl_webresource_client](https://github.com/chembl/chembl_webresource_client) | NOASSERTION | 2026-03-24 | ChEMBL : bioactivités, molécules, cibles (20M+ composés). |  |
| 370 | [openml/openml-python](https://github.com/openml/openml-python) | NOASSERTION | 2026-10-21 | OpenML : millions de jeux de données et résultats de modèles (reproductibilité ML). | 🗄️ |
| 347 | [cokelaer/bioservices](https://github.com/cokelaer/bioservices) | NOASSERTION | 2026-06-12 | Passerelle unifiée vers 40+ services bio (UniProt, KEGG, ChEMBL, Reactome…). |  |
| 164 | [guma44/GEOparse](https://github.com/guma44/GEOparse) | BSD-3-Clause | 2024-07-27 | GEO : jeux de données transcriptomiques (Gene Expression Omnibus). | 🗄️ |
| 158 | [gbif/pygbif](https://github.com/gbif/pygbif) | MIT | 2026-10-13 | GBIF : 2 milliards+ occurrences de biodiversité. | 🗄️ |
| 149 | [Ensembl/ensembl-rest](https://github.com/Ensembl/ensembl-rest) | Apache-2.0 | 2026-06-16 | Ensembl REST : génomes, variants, orthologues. | ⚠️ archivé |
| 145 | [osfclient/osfclient](https://github.com/osfclient/osfclient) | BSD-3-Clause | 2023-10-17 | OSF : projets, prépublications et données de recherche. | 🗄️ |
| 67 | [rcsb/py-rcsb-api](https://github.com/rcsb/py-rcsb-api) | MIT | 2026-09-21 | RCSB PDB : structures 3D de protéines et données d'expérience. | 🗄️ |
| 33 | [IQSS/dataverse-client-python](https://github.com/IQSS/dataverse-client-python) | Apache-2.0 | 2021-11-23 | Dataverse : jeux de données des dépôts universitaires (Harvard…). | 🗄️ |
| 29 | [datadryad/dryad-app](https://github.com/datadryad/dryad-app) | MIT | 2026-10-22 | Dryad : dépôt de données d'articles ; API article↔données. |  |

## Corpus massifs & méta-science

*Analyser la science à l'échelle du corpus*

| Étoiles | Dépôt | Licence | Dernier push | Rôle | Local |
|---:|---|---|---|---|---|
| 1 090 | [allenai/s2orc](https://github.com/allenai/s2orc) | — | 2024-04-26 | S2ORC : 80M+ articles en texte structuré (plus grand corpus scientifique ouvert). |  |
| 191 | [allenai/peS2o](https://github.com/allenai/peS2o) | Apache-2.0 | 2024-10-23 | peS2o : 40M articles prêts pour l'entraînement de LLM (open). |  |
| 157 | [ourresearch/openalex-guts](https://github.com/ourresearch/openalex-guts) | MIT | 2026-03-06 | Code d'ingestion OpenAlex : comprendre les snapshots et leurs limites. |  |

## Dépôts non vérifiés

Ces entrées n'ont pas pu être confirmées par l'API (renommage, dépôt privé ou supprimé). Elles sont conservées à titre indicatif :

- `CenterForOpenScience/TOP_Factor`

---

## Méthode de constitution

1. `scripts/candidates.py` — catalogue curaté à la main (rôle, catégorie, intérêt).
2. `scripts/verify.py` — vérification de chaque dépôt via l'API GitHub (étoiles, licence SPDX, dernier push, archivage).
3. `scripts/fetch.py` — clone superficiel des dépôts retenus dans `vendor/`.
4. `scripts/prune.py` — réduction à un miroir « source seule » (code + docs, sans binaires ni modèles) pour rester dans un budget de stockage raisonnable.
5. `scripts/build_catalog.py` — fusion et génération de ce catalogue.

Les étoiles sont un indicateur de notoriété, **pas de qualité scientifique** : un outil à 30 étoiles peut être la référence d'un domaine étroit (ex. `quest-bih/rtransparent`, `codecheckers/codecheck`).
