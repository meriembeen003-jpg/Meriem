# -*- coding: utf-8 -*-
"""OpenAlex — 260M+ travaux, couverture 1800 → aujourd'hui, sans clé API.

Documentation : https://docs.openalex.org
Quota conseillé : ~10 req/s ; ajouter `mailto` pour le « polite pool ».
"""
from __future__ import annotations
import urllib.parse

from .models import Travail
from .http import Client, ErreurReseau

BASE = "https://api.openalex.org"


def _reconstruire_resume(inv: dict | None) -> str:
    """OpenAlex stocke les résumés sous forme d'index inversé."""
    if not inv:
        return ""
    positions = []
    for mot, idxs in inv.items():
        for i in idxs:
            positions.append((i, mot))
    return " ".join(m for _, m in sorted(positions))


def _auteurs(w: dict) -> list[str]:
    out = []
    for a in w.get("authorships", []) or []:
        nom = (a.get("author") or {}).get("display_name")
        if nom:
            out.append(nom)
    return out


def vers_travail(w: dict) -> Travail:
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    oa = w.get("open_access") or {}
    return Travail(
        titre=(w.get("title") or w.get("display_name") or "").strip(),
        doi=(w.get("doi") or "").replace("https://doi.org/", ""),
        annee=w.get("publication_year"),
        auteurs=_auteurs(w),
        revue=src.get("display_name") or "",
        resume=_reconstruire_resume(w.get("abstract_inverted_index")),
        citations=w.get("cited_by_count"),
        oa_url=oa.get("oa_url") or "",
        est_oa=oa.get("is_oa"),
        type=w.get("type") or "",
        langue=w.get("language") or "",
        editeur=(src.get("host_organization_name") or ""),
        issn=(src.get("issn_l") or ""),
        pmid=(w.get("ids") or {}).get("pmid", "").replace("https://pubmed.ncbi.nlm.nih.gov/", ""),
        url=w.get("id", ""),
        source="openalex",
        id_source=(w.get("id") or "").split("/")[-1],
        sujets=[c.get("display_name") for c in (w.get("concepts") or [])[:6] if c.get("display_name")],
        references=[r.split("/")[-1] for r in (w.get("referenced_works") or [])][:200],
    )


def rechercher(client: Client, requete: str, limite: int = 25, annee_min: int | None = None,
               annee_max: int | None = None, oa_seulement: bool = False,
               tri: str = "relevance_score:desc", mailto: str = "") -> list[Travail]:
    params = {"search": requete, "per-page": min(limite, 200)}
    filtres = []
    if annee_min:
        filtres.append(f"from_publication_date:{annee_min}-01-01")
    if annee_max:
        filtres.append(f"to_publication_date:{annee_max}-12-31")
    if oa_seulement:
        filtres.append("is_oa:true")
    if filtres:
        params["filter"] = ",".join(filtres)
    if mailto:
        params["mailto"] = mailto
    data = client.get_json(f"{BASE}/works", params)
    return [vers_travail(w) for w in data.get("results", [])]


def par_doi(client: Client, doi: str) -> Travail | None:
    doi = doi.replace("https://doi.org/", "").strip()
    try:
        data = client.get_json(f"{BASE}/works/https://doi.org/{doi}")
    except ErreurReseau:
        return None
    return vers_travail(data) if data.get("id") else None


def citations_de(client: Client, id_openalex: str, limite: int = 50) -> list[Travail]:
    """Travaux citant un article donné (citation chasing avant)."""
    params = {"filter": f"cites:{id_openalex}", "per-page": min(limite, 200)}
    data = client.get_json(f"{BASE}/works", params)
    return [vers_travail(w) for w in data.get("results", [])]


def references_de(client: Client, id_openalex: str) -> list[Travail]:
    w = client.get_json(f"{BASE}/works/{id_openalex}")
    refs = [r.split("/")[-1] for r in (w.get("referenced_works") or [])]
    out = []
    for lot in range(0, len(refs), 50):
        ids = "|".join(refs[lot:lot + 50])
        data = client.get_json(f"{BASE}/works", {"filter": f"openalex_id:{ids}", "per-page": 50})
        out += [vers_travail(x) for x in data.get("results", [])]
    return out


def recherche_avancee(client: Client, expression: str, limite: int = 25) -> list[Travail]:
    """Recherche experte : 'title.search:climate AND abstract.search:policy'."""
    data = client.get_json(f"{BASE}/works", {"filter": expression, "per-page": min(limite, 200)})
    return [vers_travail(w) for w in data.get("results", [])]


def statistiques_par_annee(client: Client, requete: str) -> dict[int, int]:
    data = client.get_json(f"{BASE}/works", {"search": requete, "group_by": "publication_year"})
    return {int(g["key"]): g["count"] for g in data.get("group_by", []) if str(g["key"]).isdigit()}
