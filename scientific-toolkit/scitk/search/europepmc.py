# -*- coding: utf-8 -*-
"""Europe PMC — 40M+ abstracts, 10M+ textes intégraux, brevets, financements.

Excellente couverture biomédicale ET historique (PubMed + PMC + preprints +
brevets + littérature grise). API REST sans clé, quotas généreux.
"""
from __future__ import annotations
from .models import Travail
from .http import Client

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"


def vers_travail(r: dict) -> Travail:
    return Travail(
        titre=(r.get("title") or "").strip(),
        doi=(r.get("doi") or "").lower(),
        annee=int(r["pubYear"]) if str(r.get("pubYear", "")).isdigit() else None,
        auteurs=[a.strip() for a in (r.get("authorString") or "").rstrip(".").split(",") if a.strip()],
        revue=r.get("journalTitle") or r.get("bookOrReportDetails", {}).get("publisher", ""),
        resume=(r.get("abstractText") or "").strip(),
        citations=(r.get("citedByCount") if isinstance(r.get("citedByCount"), int) else None),
        est_oa=(r.get("isOpenAccess") == "Y"),
        type=r.get("pubType", ""),
        langue=r.get("language", ""),
        pmid=str(r.get("pmid", "") or ""),
        url=f"https://europepmc.org/article/{r.get('source', 'MED')}/{r.get('id', '')}",
        source="europepmc",
        id_source=str(r.get("id", "")),
        sujets=[k.strip() for k in (r.get("keywordList", {}) or {}).get("keyword", [])][:6],
        arxiv_id=(r.get("fullTextIdList", {}) or {}).get("fullTextId", [""])[0] if r.get("fullTextIdList") else "",
    )


def rechercher(client: Client, requete: str, limite: int = 25,
               annee_min: int | None = None, oa_seulement: bool = False,
               source: str = "") -> list[Travail]:
    q = requete
    if annee_min:
        q += f" AND (PUB_YEAR:[{annee_min} TO 2030])"
    if oa_seulement:
        q += " AND (OPEN_ACCESS:y)"
    if source:
        q += f" AND (SRC:{source})"
    params = {"query": q, "format": "json", "resultType": "core",
              "pageSize": min(limite, 100), "sort": "CITED desc"}
    data = client.get_json(f"{BASE}/search", params)
    return [vers_travail(r) for r in (data.get("resultList") or {}).get("result", [])]


def texte_integral(client: Client, pmcid: str) -> str:
    """Récupère le texte intégral XML d'un article PMC (accès ouvert)."""
    pmcid = pmcid if pmcid.upper().startswith("PMC") else f"PMC{pmcid}"
    return client.get_texte(f"{BASE}/{pmcid}/fullTextXML")


def par_doi(client: Client, doi: str) -> Travail | None:
    data = client.get_json(f"{BASE}/search", {"query": f'DOI:"{doi}"', "format": "json",
                                              "resultType": "core", "pageSize": 1})
    res = (data.get("resultList") or {}).get("result", [])
    return vers_travail(res[0]) if res else None
