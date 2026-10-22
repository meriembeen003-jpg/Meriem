# -*- coding: utf-8 -*-
"""Crossref — 160M+ DOI : métadonnées de référence, financements, rétractations.

Particularité : Crossref est la source de vérité du DOI. Un DOI absent de
Crossref est suspect ; un `update-to`/`relation` indique souvent une
rétractation ou une correction.
"""
from __future__ import annotations
from .models import Travail
from .http import Client

BASE = "https://api.crossref.org"


def _annee(it: dict) -> int | None:
    for champ in ("published-print", "published-online", "issued", "created"):
        parties = (it.get(champ) or {}).get("date-parts")
        if parties and parties[0] and parties[0][0]:
            return int(parties[0][0])
    return None


def _auteurs(it: dict) -> list[str]:
    out = []
    for a in it.get("author", []) or []:
        nom = " ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name", "")
        if nom:
            out.append(nom)
    return out


def vers_travail(it: dict) -> Travail:
    titre = (it.get("title") or [""])[0]
    return Travail(
        titre=titre.strip(),
        doi=(it.get("DOI") or "").lower(),
        annee=_annee(it),
        auteurs=_auteurs(it),
        revue=((it.get("container-title") or [""])[0] or "").strip(),
        resume=_nettoyer_jats(it.get("abstract", "")),
        citations=it.get("is-referenced-by-count"),
        est_oa=(it.get("license") is not None),
        type=it.get("type", ""),
        langue=it.get("language", ""),
        editeur=it.get("publisher", ""),
        issn=((it.get("ISSN") or [""])[0] or ""),
        url=it.get("URL", ""),
        source="crossref",
        id_source=it.get("DOI", ""),
        sujets=(it.get("subject") or [])[:6],
        references=[r.get("DOI") for r in (it.get("reference") or []) if r.get("DOI")][:200],
    )


def _nettoyer_jats(xml: str) -> str:
    import re
    return re.sub(r"<[^>]+>", " ", xml or "").replace("  ", " ").strip()


def rechercher(client: Client, requete: str, limite: int = 25,
               annee_min: int | None = None, annee_max: int | None = None,
               type_filtre: str = "") -> list[Travail]:
    params = {"query.bibliographic": requete, "rows": min(limite, 100),
              "select": "DOI,title,author,container-title,abstract,is-referenced-by-count,"
                        "issued,published-print,published-online,type,publisher,ISSN,URL,"
                        "license,subject,reference,language"}
    filtres = []
    if annee_min or annee_max:
        filtres.append(f"from-pub-date:{annee_min or 1500}-01-01,until-pub-date:{annee_max or 2030}-12-31")
    if type_filtre:
        filtres.append(f"type:{type_filtre}")
    if filtres:
        params["filter"] = ",".join(filtres)
    data = client.get_json(f"{BASE}/works", params)
    return [vers_travail(it) for it in (data.get("message") or {}).get("items", [])]


def par_doi(client: Client, doi: str) -> Travail | None:
    doi = doi.replace("https://doi.org/", "").strip()
    try:
        data = client.get_json(f"{BASE}/works/{doi}")
    except Exception:
        return None
    msg = data.get("message") or {}
    return vers_travail(msg) if msg else None


def statut_publication(client: Client, doi: str) -> dict:
    """Vérifie l'existence du DOI et repère les relations de mise à jour
    (rétractation, correction, republication)."""
    data = client.get_json(f"{BASE}/works/{doi}")
    msg = data.get("message") or {}
    if not msg:
        return {"doi": doi, "existe": False}
    rel = msg.get("relation") or {}
    mises_a_jour = msg.get("update-to") or []
    return {
        "doi": doi,
        "existe": True,
        "titre": (msg.get("title") or [""])[0],
        "revue": (msg.get("container-title") or [""])[0],
        "editeur": msg.get("publisher"),
        "type": msg.get("type"),
        "relations": list(rel.keys()) if rel else [],
        "mises_a_jour": [{"type": u.get("type"), "doi": u.get("DOI")} for u in mises_a_jour],
        "retracte_probable": bool(mises_a_jour) or "is-retracted-by" in rel,
        "date": _annee(msg),
    }
