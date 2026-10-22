# -*- coding: utf-8 -*-
"""Contrôle de rétractations — base locale + import de la Retraction Watch DB.

Deux usages :
  • `chercher(doi=..., titre=...)` sur la base d'exemple fournie ;
  • `importer_base_retraction_watch(csv)` pour charger l'export officiel
    « Retraction Watch Database » (demande gratuite à Crossref/RW) et obtenir
    une couverture de ~60 000 rétractations, y compris historiques.

La base livrée (data/retractions.csv) est un *échantillon pédagogique* de cas
documentés, pas une base exhaustive : pour un audit réel, importer la RW DB.
"""
from __future__ import annotations
import csv
import io
import os
import pathlib
import re
import unicodedata

DATA = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "retractions.csv"


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", t).strip()


def _norm_doi(d: str) -> str:
    d = (d or "").strip().lower()
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", d)
    return d


_cache: dict[str, list[dict]] = {}


def charger(base: str | None = None) -> list[dict]:
    """Charge une base CSV (chemin) ou la base d'exemple livrée."""
    chemin = pathlib.Path(base) if base else DATA
    cle = str(chemin)
    if cle in _cache:
        return _cache[cle]
    if not chemin.exists():
        _cache[cle] = []
        return []
    texte = chemin.read_text(encoding="utf-8", errors="replace")
    # détection de l'export officiel Retraction Watch
    entete = texte.splitlines()[0].lower() if texte else ""
    rows: list[dict] = []
    try:
        if "record id" in entete or "originalpaperdoi" in entete.replace(" ", ""):
            rows = _importer_rw(texte)
        else:
            for r in csv.DictReader(io.StringIO(texte)):
                rows.append({
                    "doi": _norm_doi(r.get("doi", "")),
                    "titre": r.get("titre", "") or r.get("title", ""),
                    "annee": (r.get("annee") or "")[:4],
                    "revue": r.get("revue", "") or r.get("journal", ""),
                    "motif": r.get("motif", "") or r.get("reason", ""),
                    "date": r.get("date_retractation", ""),
                    "source": r.get("source", ""),
                })
    except Exception:
        rows = []
    _cache[cle] = rows
    return rows


def _importer_rw(texte: str) -> list[dict]:
    rows = []
    for r in csv.DictReader(io.StringIO(texte)):
        rows.append({
            "doi": _norm_doi(r.get("OriginalPaperDOI", "")),
            "pmid": r.get("OriginalPaperPubMedID", ""),
            "titre": r.get("Title", ""),
            "annee": (r.get("RetractionDate", "") or "")[-4:],
            "revue": r.get("Journal", ""),
            "motif": (r.get("Reason", "") or "")[:400],
            "date": r.get("RetractionDate", ""),
            "nature": r.get("RetractionNature", ""),
            "source": "Retraction Watch Database",
        })
    return [r for r in rows if r["doi"] or r["titre"]]


def importer_base_retraction_watch(chemin_csv: str) -> dict:
    rows = charger(chemin_csv)
    return {"entrees": len(rows), "fichier": chemin_csv,
            "avec_doi": sum(1 for r in rows if r["doi"])}


def chercher(doi: str = "", titre: str = "", base: str | None = None,
             seuil_titre: float = 0.92) -> dict | None:
    """Retourne l'enregistrement de rétractation correspondant, ou None."""
    rows = charger(base)
    d = _norm_doi(doi)
    if d:
        for r in rows:
            if r["doi"] and (r["doi"] == d or r["doi"].split("/")[-1] == d.split("/")[-1]):
                return r
    if titre:
        t = _norm(titre)
        if len(t) < 15:
            return None
        for r in rows:
            tr = _norm(r.get("titre", ""))
            if not tr:
                continue
            if tr == t:
                return r
            # inclusion mutuelle (titres tronqués dans les exports)
            if len(t) > 25 and (t in tr or tr in t):
                return r
            mots_t, mots_r = set(t.split()), set(tr.split())
            if mots_t and len(mots_t & mots_r) / len(mots_t | mots_r) >= seuil_titre:
                return r
    return None


def verifier_texte(texte: str, base: str | None = None) -> list[dict]:
    """Repère les DOI cités dans un texte et vérifie leur statut de rétractation."""
    dois = re.findall(r"10\.\d{4,9}/[^\s\"'<>,;)\]]+", texte)
    out = []
    for d in dict.fromkeys(dois):
        r = chercher(doi=d, base=base)
        if r:
            out.append({"doi": d, **r})
    return out


def statistiques(base: str | None = None) -> dict:
    rows = charger(base)
    motifs: dict[str, int] = {}
    for r in rows:
        for m in re.split(r"[;,]", r.get("motif", "")):
            m = m.strip()
            if m:
                motifs[m] = motifs.get(m, 0) + 1
    return {"entrees": len(rows),
            "avec_doi": sum(1 for r in rows if r["doi"]),
            "motifs_principaux": sorted(motifs.items(), key=lambda x: -x[1])[:10],
            "note": "échantillon pédagogique" if not base else "base importée"}
