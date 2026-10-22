# -*- coding: utf-8 -*-
"""Exports bibliographiques : CSV, RIS, BibTeX, JSON, flux PRISMA (Markdown)."""
from __future__ import annotations
import csv
import json
import pathlib
import re

from ..search.models import Travail


def _slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s.lower()).strip("_")
    return s[:40] or "ref"


def cle_bibtex(t: Travail, idx: int = 0) -> str:
    nom = _slug(t.auteurs[0].split()[-1]) if t.auteurs else "anonyme"
    mot = _slug((t.titre or "sans_titre").split()[0]) if t.titre else "sans_titre"
    return f"{nom}{t.annee or 'sansannee'}{mot}{idx if idx else ''}"


def vers_bibtex(travaux: list[Travail]) -> str:
    out, vues = [], set()
    for i, t in enumerate(travaux):
        cle = cle_bibtex(t, 0)
        base, n = cle, 1
        while cle in vues:
            n += 1
            cle = f"{base}{chr(96 + n)}"
        vues.add(cle)
        champs = [
            ("title", t.titre),
            ("author", " and ".join(t.auteurs)),
            ("journal", t.revue),
            ("year", str(t.annee) if t.annee else ""),
            ("doi", t.doi),
            ("volume", ""),
            ("pages", ""),
            ("publisher", t.editeur),
            ("url", t.url or t.oa_url),
            ("abstract", (t.resume or "")[:1200]),
            ("keywords", ", ".join(t.sujets)),
        ]
        corps = ",\n".join(f"  {k} = {{{v}}}" for k, v in champs if v)
        out.append(f"@article{{{cle},\n{corps}\n}}")
    return "\n\n".join(out) + "\n"


def vers_ris(travaux: list[Travail]) -> str:
    out = []
    for t in travaux:
        L = ["TY  - JOUR" if t.type not in ("preprint",) else "TY  - UNPB"]
        if t.titre:
            L.append(f"TI  - {t.titre}")
        for a in t.auteurs:
            L.append(f"AU  - {a}")
        if t.annee:
            L.append(f"PY  - {t.annee}")
        if t.revue:
            L.append(f"JO  - {t.revue}")
        if t.doi:
            L.append(f"DO  - {t.doi}")
        if t.resume:
            L.append("AB  - " + " ".join(t.resume.split())[:2000])
        if t.url or t.oa_url:
            L.append(f"UR  - {t.url or t.oa_url}")
        L.append("ER  - ")
        out.append("\n".join(L))
    return "\n\n".join(out) + "\n"


COLONNES = ["titre", "doi", "annee", "auteurs", "revue", "citations", "est_oa",
            "oa_url", "type", "langue", "source", "sources_multiples", "resume"]


def vers_csv(travaux: list[Travail], chemin: str) -> str:
    p = pathlib.Path(chemin)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES, extrasaction="ignore")
        w.writeheader()
        for t in travaux:
            d = t.dict()
            d["auteurs"] = "; ".join(t.auteurs)
            d["sources_multiples"] = "; ".join(t.sources_multiples)
            w.writerow({k: d.get(k, "") for k in COLONNES})
    return str(p)


def vers_json(travaux: list[Travail], chemin: str) -> str:
    p = pathlib.Path(chemin)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps([t.dict() for t in travaux], indent=2, ensure_ascii=False), encoding="utf-8")
    return str(p)


def exporter_tout(travaux: list[Travail], dossier: str, prefixe: str = "corpus") -> dict:
    d = pathlib.Path(dossier)
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{prefixe}.bib").write_text(vers_bibtex(travaux), encoding="utf-8")
    (d / f"{prefixe}.ris").write_text(vers_ris(travaux), encoding="utf-8")
    return {
        "csv": vers_csv(travaux, str(d / f"{prefixe}.csv")),
        "json": vers_json(travaux, str(d / f"{prefixe}.json")),
        "bibtex": str(d / f"{prefixe}.bib"),
        "ris": str(d / f"{prefixe}.ris"),
    }


def flux_prisma(compteurs: dict) -> str:
    """Diagramme de flux PRISMA 2020 en texte (à coller dans un manuscrit)."""
    c = compteurs
    lignes = [
        "Identification",
        f"  Enregistrements identifiés par source : {c.get('identifies', 0)}",
    ]
    for s, n in (c.get("par_source") or {}).items():
        lignes.append(f"    · {s} : {n}")
    lignes += [
        f"  Doublons supprimés : {c.get('doublons', 0)}",
        "",
        "Sélection",
        f"  Enregistrements criblés (titre/résumé) : {c.get('cribles', 0)}",
        f"  Exclus sur titre/résumé : {c.get('exclus_titre', 0)}",
    ]
    for motif, n in (c.get("motifs_exclusion") or {}).items():
        lignes.append(f"    · {motif} : {n}")
    lignes += [
        f"  Textes intégraux recherchés : {c.get('textes_recherches', 0)}",
        f"  Textes intégraux non disponibles : {c.get('non_disponibles', 0)}",
        "",
        "Inclusion",
        f"  Études incluses dans la synthèse : {c.get('inclus', 0)}",
        f"  Études incluses dans la méta-analyse : {c.get('inclus_meta', 0)}",
    ]
    return "\n".join(lignes)
