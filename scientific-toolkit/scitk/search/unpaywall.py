# -*- coding: utf-8 -*-
"""Unpaywall — résolution du PDF légal en accès ouvert pour un DOI.

50M+ articles OA. Gratuit avec un email de contact obligatoire.
C'est la voie *légale* privilegiée par ce kit pour récupérer un texte intégral
(avant tout autre outil de téléchargement).
"""
from __future__ import annotations
from .http import Client

BASE = "https://api.unpaywall.org/v2"


def resoudre(client: Client, doi: str, email: str) -> dict:
    doi = doi.replace("https://doi.org/", "").strip()
    if not email or "@" not in email:
        raise ValueError("Unpaywall exige une adresse email de contact (paramètre email).")
    data = client.get_json(f"{BASE}/{doi}", {"email": email})
    meilleur = data.get("best_oa_location") or {}
    return {
        "doi": data.get("doi"),
        "est_oa": data.get("is_oa"),
        "statut": data.get("oa_status"),        # gold, green, hybrid, bronze, closed
        "pdf": meilleur.get("url_for_pdf"),
        "landing": meilleur.get("url"),
        "editeur": data.get("publisher"),
        "revue": data.get("journal_name"),
        "annee": data.get("year"),
        "titre": data.get("title"),
        "licence": meilleur.get("license"),
        "emplacements": [
            {"url_pdf": l.get("url_for_pdf"), "url": l.get("url"),
             "hebergement": l.get("host_type"), "version": l.get("version"),
             "licence": l.get("license")}
            for l in (data.get("oa_locations") or [])
        ],
    }


def resoudre_lot(client: Client, dois: list[str], email: str) -> list[dict]:
    out = []
    for d in dois:
        try:
            out.append(resoudre(client, d, email))
        except Exception as e:
            out.append({"doi": d, "erreur": str(e)})
    return out
