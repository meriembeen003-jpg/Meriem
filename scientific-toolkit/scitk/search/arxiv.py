# -*- coding: utf-8 -*-
"""arXiv — préprints 1991 → aujourd'hui, physique, maths, informatique, biologie.

API Atom ; pas de clé ; 1 requête / 3 s recommandé.
"""
from __future__ import annotations
import xml.etree.ElementTree as ET

from .models import Travail
from .http import Client

BASE = "http://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _texte(node, chemin, defaut=""):
    el = node.find(chemin, NS)
    return (el.text or defaut).strip() if el is not None and el.text else defaut


def vers_travail(entry) -> Travail:
    id_url = _texte(entry, "a:id")
    arxiv_id = id_url.split("/abs/")[-1] if "/abs/" in id_url else id_url
    doi = _texte(entry, "arxiv:doi")
    cats = [c.get("term") for c in entry.findall("a:category", NS)]
    return Travail(
        titre=" ".join(_texte(entry, "a:title").split()),
        doi=doi,
        annee=int(_texte(entry, "a:published")[:4]) if _texte(entry, "a:published") else None,
        auteurs=[_texte(a, "a:name") for a in entry.findall("a:author", NS)],
        revue=_texte(entry, "arxiv:journal_ref") or "arXiv",
        resume=" ".join(_texte(entry, "a:summary").split()),
        type="preprint",
        arxiv_id=arxiv_id.split("v")[0],
        url=id_url,
        source="arxiv",
        id_source=arxiv_id,
        sujets=cats[:6],
    )


def rechercher(client: Client, requete: str, limite: int = 25,
               tri: str = "relevance", categorie: str = "") -> list[Travail]:
    q = requete
    if categorie:
        q = f"cat:{categorie} AND ({requete})"
    params = {
        "search_query": f"all:{q}" if ":" not in q else q,
        "start": 0,
        "max_results": min(limite, 100),
        "sortBy": "relevance" if tri == "relevance" else "submittedDate",
        "sortOrder": "descending",
    }
    xml = client.get_texte(BASE, params)
    racine = ET.fromstring(xml)
    return [vers_travail(e) for e in racine.findall("a:entry", NS)]


def par_id(client: Client, arxiv_id: str) -> Travail | None:
    xml = client.get_texte(BASE, {"id_list": arxiv_id})
    racine = ET.fromstring(xml)
    entries = racine.findall("a:entry", NS)
    return vers_travail(entries[0]) if entries else None
