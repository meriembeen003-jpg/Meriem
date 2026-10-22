# Brancher les sources scientifiques sur un agent (MCP)

Le *Model Context Protocol* permet à un agent (Claude Desktop, Cursor, VS Code +
Copilot, Continue, Cline…) d'appeler des outils externes. Les serveurs archivés
dans `vendor/mcp/` exposent les sources scientifiques comme des fonctions.

## 1. Serveurs inclus dans le miroir

| Serveur | Dossier | Ce qu'il expose |
|---|---|---|
| `paper-search-mcp` | `vendor/mcp/paper-search-mcp` | recherche multi-sources (arXiv, PubMed, bioRxiv, Semantic Scholar, IACR…) |
| `arxiv-mcp-server` | `vendor/mcp/arxiv-mcp-server` | recherche arXiv, téléchargement et lecture locale des PDF |
| `paper-search-mcp-nodejs` | non archivé | version Node, 13 sources |
| `PubMed-MCP-Server` | `vendor/mcp/PubMed-MCP-Server` | recherche PubMed, abstracts |
| `paperscraper-MCP-Server` | `vendor/mcp/paperscraper-MCP-Server` | métadonnées bioRxiv/medRxiv/chemRxiv/arXiv |
| `semantic-scholar-fastmcp-mcp-server` | `vendor/mcp/semantic-scholar-fastmcp-mcp-server` | recherche, citations, recommandations |
| `clinicaltrialsgov-mcp-server` | `vendor/mcp/clinicaltrialsgov-mcp-server` | essais cliniques |
| `biomcp` | `vendor/mcp/biomcp` | PubMed, PubTator, ClinVar, MyVariant |
| `zotero-mcp` | `vendor/mcp/zotero-mcp` | bibliothèque Zotero locale |
| `openalex-research-mcp` | `vendor/mcp/openalex-research-mcp` | 240 M+ travaux OpenAlex |
| `find-research-papers-mcp` | `vendor/mcp/find-research-papers-mcp` |arXiv, OpenAlex, Crossref, PubMed |
| `mcp-bibliotheque_nationale_de_France` | `vendor/mcp/mcp-bibliotheque_nationale_de_France` | Gallica / BnF (textes anciens) |
| `scholar-sidekick-mcp` | `vendor/mcp/scholar-sidekick-mcp` | résolution DOI/PMID/ISBN/arXiv |
| `mcp-for-research` | `vendor/mcp/mcp-for-research` | PubMed + Google Scholar |

## 2. Configuration — Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
ou `%APPDATA%\Claude\claude_desktop_config.json` (Windows) :

```json
{
  "mcpServers": {
    "arxiv": {
      "command": "uvx",
      "args": ["arxiv-mcp-server"]
    },
    "paper-search": {
      "command": "uvx",
      "args": ["paper-search-mcp"]
    },
    "pubmed": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/JackKuo666/PubMed-MCP-Server", "PubMed-MCP-Server"]
    },
    "zotero": {
      "command": "npx",
      "args": ["-y", "zotero-mcp"],
      "env": {
        "ZOTERO_API_KEY": "…",
        "ZOTERO_LIBRARY_ID": "…"
      }
    },
    "biomcp": {
      "command": "uvx",
      "args": ["biomcp"]
    }
  }
}
```

## 3. Configuration — VS Code / Cursor

`.vscode/mcp.json` :

```json
{
  "servers": {
    "arxiv": { "command": "uvx", "args": ["arxiv-mcp-server"] },
    "openalex": { "command": "uvx", "args": ["openalex-research-mcp"] },
    "clinicaltrials": { "command": "npx", "args": ["-y", "clinicaltrialsgov-mcp-server"] }
  }
}
```

## 4. Bonnes pratiques

1. **Un serveur = une source.** Empiler 10 serveurs identiques sature la fenêtre
   de contexte de l'agent et dégrade ses choix.
2. **Écrire les requêtes.** L'agent doit utiliser la syntaxe native de la source
   (champs `title.search:`, `filter=is_oa:true`, `PUB_YEAR:[2015 TO 2026]`).
3. **Exiger les identifiants.** Toute réponse doit citer un DOI/PMID/arXiv ID
   vérifiable ; sinon l'agent « hallucine » des références crédibles.
4. **Fermer la boucle par l'audit.** Un agent qui produit des références doit
   les faire vérifier : `python3 -m scitk biblio sortie.bib` et
   `scitk retractions --texte sortie.md`.
5. **Isolation.** Ces serveurs accèdent au réseau et parfois au disque
   (Zotero, PDF) : les exécuter dans un conteneur ou un utilisateur dédié.
