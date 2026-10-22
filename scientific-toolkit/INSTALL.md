# Installation

## 0. Rien à installer pour l'audit

Le moteur d'audit (`scitk.audit`) et le pipeline PRISMA n'utilisent que la
**bibliothèque standard** de Python 3.10+.

```bash
python3 --version && python3 -m unittest discover -s tests
```

## 1. Dépendances recommandées (recherche, PDF, formats)

```bash
python3 -m pip install -r requirements.txt
```

| Paquet | Usage |
|---|---|
| `requests`, `httpx` | clients HTTP alternatifs |
| `pyalex` | client OpenAlex officiel |
| `habanero` | client Crossref |
| `arxiv` | client arXiv |
| `semanticscholar` | client Semantic Scholar |
| `pybliometrics` | client Scopus (clé Elsevier requise) |
| `unpywall` | Unpaywall |
| `pyzotero` | API Zotero |
| `bibtexparser` | BibTeX (alternative à notre parseur maison) |
| `pymupdf` | lecture PDF rapide |
| `pdfplumber` | tableaux et coordonnées |
| `camelot-py` | tableaux PDF (nécessite Ghostscript) |
| `tiktoken` | découpage pour les LLM |
| `pytest` | exécution des tests au format pytest |

## 2. Outils lourds, à installer à la demande

### GROBID — PDF scientifique → XML structuré (référence du domaine)

```bash
docker pull lfoppiano/grobid:0.8.1
docker run -t --rm -p 8070:8070 lfoppiano/grobid:0.8.1
# puis : curl -F input=@article.pdf http://localhost:8070/api/processFulltextDocument
```

### marker — PDF → Markdown/JSON (rapide, tables et équations)

```bash
pip install marker-pdf
marker_single article.pdf --output_dir sortie/
```

### docling — conversion universelle (IBM)

```bash
pip install docling
docling article.pdf --output sortie/
```

### MinerU / Nougat / Surya — alternatives d'extraction

```bash
pip install -U "mineru[core]"          # PDF scientifiques complexes
pip install nougat-ocr                  # équations LaTeX
pip install surya-ocr                   # OCR + layout multilingue
```

### PaperQA2 — agent de lecture de corpus

```bash
pip install paper-qa
pqa --paper_directory corpus/ "Quels effets sont rapportés ?"
```

### ASReview — screening par apprentissage actif

```bash
pip install asreview
asreview lab
```

### R — méta-analyse et scientométrie

```r
install.packages(c("metafor", "meta", "dmetar", "robvis", "bibliometrix",
                   "scrutiny", "revtools", "statcheck", "rcrossref"))
```

## 3. Serveurs MCP (agents LLM)

```bash
# Python (uv recommandé)
pip install uv
uvx paper-search-mcp
uvx arxiv-mcp-server
uvx biomcp

# Node
npx -y paper-search-mcp-nodejs
npx -y clinicaltrialsgov-mcp-server
```

Configuration détaillée dans `MCP.md`.

## 4. Reconstituer le miroir de code

```bash
python3 scripts/discover.py        # exploration par mots-clés (API GitHub)
python3 scripts/verify.py          # étoiles, licences, activité
python3 scripts/fetch.py           # clone des 74 dépôts retenus
python3 scripts/fetch.py --opt     # + les outils lourds (plusieurs centaines de Mo)
python3 scripts/prune.py           # miroir « source seule »
python3 scripts/build_catalog.py   # régénère CATALOGUE.md et catalog/*.json
```

`gh` (GitHub CLI) doit être authentifié pour `verify.py` :

```bash
gh auth login          # ou exporter GH_TOKEN
```

## 5. Installation complète en une commande

```bash
bash scripts/install.sh
```

Le script vérifie Python, lance les tests, installe les dépendances optionnelles
(échec non bloquant) et affiche le catalogue.
