# -*- coding: utf-8 -*-
"""scitk — boîte à outils de recherche et d'audit scientifiques.

Modules
  scitk.audit    : cohérence statistique (APA), GRIM/GRIMMER/SPRITE, p-curve,
                   décimales, Benford, doublons de texte, transparence,
                   rétractations, bibliographies, rapports.
  scitk.search   : clients OpenAlex, Crossref, arXiv, Europe PMC, Semantic Scholar,
                   Unpaywall + recherche fédérée avec déduplication.
  scitk.pipeline : revue systématique PRISMA, exports CSV/RIS/BibTeX.
"""
__version__ = "1.0.0"
__all__ = ["audit", "search", "pipeline", "cli"]
