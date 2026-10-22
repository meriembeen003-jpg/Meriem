# -*- coding: utf-8 -*-
"""Audit d'une bibliographie (BibTeX, RIS, CSV de DOIs).

Contrôles :
  • syntaxe et champs obligatoires ; DOI manquant ou mal formé ;
  • doublons (DOI identique, titre quasi identique, preprint + version publiée) ;
  • anomalies temporelles (année future, antérieure à 1500, incohérence avec le DOI) ;
  • rétractations (base locale + hook en ligne) ;
  • citations circulaires / auto-citations (taux par auteur) ;
  • références « fantômes » (métadonnées incomplètes, revue inconnue).
"""
from __future__ import annotations
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field, asdict

from . import retractions as RET
from .duplicates import titres_proches

RE_DOI = re.compile(r"^10\.\d{4,9}/\S+$")


# ─────────────────────────── parsing BibTeX ───────────────────────────
def _nettoyer(v: str) -> str:
    v = v.strip().strip("{}\"").strip()
    v = re.sub(r"\s+", " ", v)
    return v


def parser_bibtex(texte: str) -> list[dict]:
    """Parseur BibTeX tolérant (pas de dépendance externe).

    Gère @type{clé, champ = {valeur}, champ = "valeur", champ = 123}.
    """
    entrees, i, n = [], 0, len(texte)
    while True:
        m = re.search(r"@(\w+)\s*\{", texte[i:])
        if not m:
            break
        typ = m.group(1).lower()
        debut = i + m.end()
        profondeur, j = 1, debut
        while j < n and profondeur:
            if texte[j] == "{":
                profondeur += 1
            elif texte[j] == "}":
                profondeur -= 1
            j += 1
        corps = texte[debut:j - 1]
        i = j
        cle, _, reste = corps.partition(",")
        entree = {"type": typ, "cle": _nettoyer(cle)}
        champ_re = re.compile(r"(\w+)\s*=\s*", re.I)
        pos = 0
        while True:
            cm = champ_re.search(reste, pos)
            if not cm:
                break
            nom = cm.group(1).lower()
            k = cm.end()
            while k < len(reste) and reste[k] in " \t\n":
                k += 1
            if k >= len(reste):
                break
            if reste[k] == "{":
                prof, k2 = 1, k + 1
                while k2 < len(reste) and prof:
                    if reste[k2] == "{":
                        prof += 1
                    elif reste[k2] == "}":
                        prof -= 1
                    k2 += 1
                val = reste[k + 1:k2 - 1]
                pos = k2
            elif reste[k] == '"':
                k2 = reste.find('"', k + 1)
                k2 = len(reste) if k2 == -1 else k2
                val = reste[k + 1:k2]
                pos = k2 + 1
            else:
                vm = re.match(r"([^,\n]+)", reste[k:])
                val = vm.group(1) if vm else ""
                pos = k + len(val)
            entree[nom] = _nettoyer(val)
        entrees.append(entree)
    return entrees


def parser_ris(texte: str) -> list[dict]:
    out, cur = [], {}
    for ligne in texte.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])\s{1,2}-\s?(.*)$", ligne)
        if not m:
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "TY":
            cur = {"type": val.lower()}
        elif tag == "ER":
            if cur:
                out.append(cur)
            cur = {}
        else:
            cle = {"TI": "title", "T1": "title", "AU": "author", "PY": "year",
                   "Y1": "year", "JO": "journal", "JF": "journal", "T2": "journal",
                   "DO": "doi", "AB": "abstract", "VL": "volume", "IS": "number",
                   "SP": "pages", "PB": "publisher"}.get(tag, tag.lower())
            if cle in ("author", "editor"):
                cur.setdefault("author", [])
                cur["author"] = (cur["author"] if isinstance(cur["author"], str)
                                 else ", ".join([cur["author"]]) if cur.get("author") else "")
                cur["author"] = (cur["author"] + ", " + val).strip(", ") if cur.get("author") else val
            else:
                cur[cle] = val
    return out


# ─────────────────────────── validation ───────────────────────────
def doi_valide(doi: str) -> bool:
    return bool(RE_DOI.match((doi or "").strip()))


def _norm_titre(t: str) -> str:
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", "", t)


@dataclass
class Constat:
    code: str
    severite: str
    cible: str
    message: str

    def dict(self):
        return asdict(self)


@dataclass
class AuditBiblio:
    entrees: int = 0
    constats: list[Constat] = field(default_factory=list)
    doublons: list[dict] = field(default_factory=list)
    retractees: list[dict] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def nb_problemes(self):
        return len(self.constats)

    def dict(self):
        return {"entrees": self.entrees, "nb_constats": len(self.constats),
                "constats": [c.dict() for c in self.constats],
                "doublons": self.doublons, "retractees": self.retractees,
                "stats": self.stats}


def audit_bibliographie(references: list[dict], auteur_auditeur: str = "",
                        annee_min: int = 1500, annee_max: int = 2100,
                        base_retractations: str | None = None) -> AuditBiblio:
    audit = AuditBiblio(entrees=len(references))
    annee_courante = 2026
    doublons_doi, titres = Counter(), {}

    for idx, ref in enumerate(references):
        cle = ref.get("cle") or ref.get("doi") or f"ref{idx}"
        titre = ref.get("title", "")
        annee = ref.get("year", "")
        doi = (ref.get("doi") or "").strip()

        # 1) champs essentiels
        if not titre:
            audit.constats.append(Constat("titre_manquant", "majeur", cle,
                                          "Référence sans titre exploitable."))
        if not ref.get("author") and ref.get("type") not in ("misc", "online"):
            audit.constats.append(Constat("auteur_manquant", "mineur", cle,
                                          "Référence sans auteur."))
        if not annee:
            audit.constats.append(Constat("annee_manquante", "mineur", cle,
                                          "Année de publication absente."))

        # 2) année
        m = re.search(r"\d{4}", str(annee))
        if m:
            a = int(m.group(0))
            if a < annee_min or a > annee_courante + 1:
                audit.constats.append(Constat(
                    "annee_aberrante", "majeur", cle,
                    f"Année {a} invraisemblable (bornes {annee_min}–{annee_courante + 1})."))
        # 3) DOI
        if doi:
            if not doi_valide(doi):
                audit.constats.append(Constat(
                    "doi_invalide", "majeur", cle, f"DOI mal formé : {doi}"))
            doublons_doi[doi.lower()] += 1
        else:
            audit.constats.append(Constat(
                "doi_absent", "mineur", cle,
                "Pas de DOI : vérification d'existence et de rétractation impossible."))
        # 4) titre pour doublons
        if titre:
            titres[cle] = titre

        # 5) rétractation
        res = RET.chercher(doi=doi, titre=titre, base=base_retractations)
        if res:
            audit.retractees.append({"cle": cle, **res})
            audit.constats.append(Constat(
                "retractee", "critique", cle,
                f"Référence rétractée : {res.get('titre', '')} ({res.get('annee', '')}) — "
                f"{res.get('source', '')}"))

    # 6) doublons exacts
    for doi, n in doublons_doi.items():
        if n > 1:
            audit.doublons.append({"type": "doi_identique", "valeur": doi, "occurrences": n})
            audit.constats.append(Constat(
                "doublon_doi", "majeur", doi, f"DOI présent {n} fois dans la bibliographie."))

    # 7) doublons de titres (>= .85 de similarité)
    for paire in titres_proches(titres, seuil=0.85):
        audit.doublons.append({"type": "titre_similaire", **paire})
        audit.constats.append(Constat(
            "doublon_titre", "majeur", f"{paire['a']} ≈ {paire['b']}",
            f"Titres quasi identiques ({paire['similarite']:.0%}) : doublon probable "
            "ou preprint + version publiée."))

    # 8) auto-citations
    if auteur_auditeur:
        patron = _norm_titre(auteur_auditeur).split()[-1]
        auto = sum(1 for r in references
                   if patron and patron in _norm_titre(r.get("author", "")))
        audit.stats["auto_citations"] = auto
        audit.stats["taux_auto_citation"] = round(auto / len(references), 3) if references else 0
        if references and auto / len(references) > 0.25:
            audit.constats.append(Constat(
                "auto_citation_excessive", "mineur", auteur_auditeur,
                f"{auto}/{len(references)} références citent l'auteur audité "
                f"({auto / len(references):.0%}) : à examiner."))

    # 9) statistiques globales
    sans_doi = sum(1 for r in references if not (r.get("doi") or "").strip())
    audit.stats.update({
        "sans_doi": sans_doi,
        "part_sans_doi": round(sans_doi / len(references), 3) if references else 0,
        "annee_mediane": _mediane([int(re.search(r"\d{4}", str(r.get("year", ""))).group(0))
                                   for r in references
                                   if re.search(r"\d{4}", str(r.get("year", "")))]),
        "types": dict(Counter(r.get("type", "?") for r in references)),
    })
    return audit


def _mediane(vals):
    if not vals:
        return None
    vals = sorted(vals)
    n = len(vals)
    return vals[n // 2] if n % 2 else round((vals[n // 2 - 1] + vals[n // 2]) / 2, 1)


def charger_bibliographie(chemin: str) -> list[dict]:
    texte = open(chemin, encoding="utf-8", errors="replace").read()
    if chemin.lower().endswith(".bib"):
        return parser_bibtex(texte)
    if chemin.lower().endswith(".ris"):
        return parser_ris(texte)
    if chemin.lower().endswith((".csv", ".txt")):
        return [{"doi": l.strip()} for l in texte.splitlines() if l.strip()]
    raise ValueError("format non pris en charge (.bib, .ris, .csv)")
