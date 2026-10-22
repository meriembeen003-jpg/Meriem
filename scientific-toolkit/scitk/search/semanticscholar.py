# -*- coding: utf-8 -*-
"""Semantic Scholar — 220M+ papiers, abstracts, citations, TLDR, recommandations.

Sans clé : ~1 req/s. Avec clé gratuite : 10 req/s (en-tête x-api-key).
"""
from __future__ import annotations
from .models import Travail
from .http import Client

BASE = "https://api.semanticscholar.org/graph/v1"
CHAMPS = ("title,abstract,year,authors,venue,journal,externalIds,citationCount,"
          "openAccessPdf,url,fieldsOfStudy,publicationTypes,referenceCount,tldr")


def vers_travail(p: dict) -> Travail:
    ext = p.get("externalIds") or {}
    oa = p.get("openAccessPdf") or {}
    tldr = (p.get("tldr") or {}).get("text", "")
    resume = p.get("abstract") or tldr or ""
    return Travail(
        titre=(p.get("title") or "").strip(),
        doi=(ext.get("DOI") or "").lower(),
        annee=p.get("year"),
        auteurs=[a.get("name") for a in (p.get("authors") or []) if a.get("name")],
        revue=(p.get("venue") or (p.get("journal") or {}).get("name") or ""),
        resume=resume,
        citations=p.get("citationCount"),
        oa_url=oa.get("url", ""),
        est_oa=bool(oa.get("url")),
        type=", ".join(p.get("publicationTypes") or []) or "article",
        pmid=str(ext.get("PubMed", "") or ""),
        arxiv_id=str(ext.get("ArXiv", "") or ""),
        url=p.get("url", ""),
        source="semanticscholar",
        id_source=p.get("paperId", ""),
        sujets=(p.get("fieldsOfStudy") or [])[:6],
    )


def rechercher(client: Client, requete: str, limite: int = 25,
               annee_min: int | None = None, annee_max: int | None = None,
               cle_api: str = "") -> list[Travail]:
    params = {"query": requete, "limit": min(limite, 100), "fields": CHAMPS}
    if annee_min or annee_max:
        params["year"] = f"{annee_min or ''}-{annee_max or ''}"
    headers = {"x-api-key": cle_api} if cle_api else None
    data = client.get_json(f"{BASE}/paper/search", params, headers=headers)
    return [vers_travail(p) for p in data.get("data", [])]


def par_doi(client: Client, doi: str, cle_api: str = "") -> Travail | None:
    headers = {"x-api-key": cle_api} if cle_api else None
    try:
        p = client.get_json(f"{BASE}/paper/DOI:{doi}", {"fields": CHAMPS}, headers=headers)
    except Exception:
        return None
    return vers_travail(p) if p.get("paperId") else None


def citations(client: Client, paper_id: str, limite: int = 100) -> list[Travail]:
    data = client.get_json(f"{BASE}/paper/{paper_id}/citations",
                           {"fields": CHAMPS, "limit": min(limite, 1000)})
    return [vers_travail(x["citingPaper"]) for x in data.get("data", [])]


def references(client: Client, paper_id: str, limite: int = 100) -> list[Travail]:
    data = client.get_json(f"{BASE}/paper/{paper_id}/references",
                           {"fields": CHAMPS, "limit": min(limite, 1000)})
    return [vers_travail(x["citedPaper"]) for x in data.get("data", [])]


def recommandations(client: Client, paper_id: str, limite: int = 50) -> list[Travail]:
    data = client.get_json(f"{BASE}/recommendations/v1/papers/forpaper/{paper_id}",
                           {"fields": CHAMPS, "limit": min(limite, 100)})
    return [vers_travail(p) for p in data.get("recommendedPapers", [])]
