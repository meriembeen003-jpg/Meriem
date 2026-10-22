# -*- coding: utf-8 -*-
"""Modèle normalisé d'un travail scientifique, quelle que soit la source."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict


@dataclass
class Travail:
    titre: str
    doi: str = ""
    annee: int | None = None
    auteurs: list[str] = field(default_factory=list)
    revue: str = ""
    resume: str = ""
    citations: int | None = None
    oa_url: str = ""
    est_oa: bool | None = None
    type: str = ""
    langue: str = ""
    editeur: str = ""
    issn: str = ""
    pmid: str = ""
    arxiv_id: str = ""
    url: str = ""
    source: str = ""
    id_source: str = ""
    sujets: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    sources_multiples: list[str] = field(default_factory=list)

    def dict(self):
        return asdict(self)

    @property
    def cle_dedup(self) -> str:
        if self.doi:
            return "doi:" + self.doi.lower().strip()
        titre = " ".join((self.titre or "").lower().split())[:120]
        return f"titre:{titre}|{self.annee or ''}"


def fusionner(a: Travail, b: Travail) -> Travail:
    """Fusionne deux notices du même travail en conservant le plus d'information."""
    base, autre = (a, b) if (a.resume and not b.resume) else (b, a)
    out = Travail(**{k: v for k, v in base.dict().items()})
    for champ in ("doi", "annee", "revue", "resume", "oa_url", "pmid", "arxiv_id", "url",
                  "editeur", "issn", "langue", "type"):
        if not getattr(out, champ) and getattr(autre, champ):
            setattr(out, champ, getattr(autre, champ))
    if not out.auteurs and autre.auteurs:
        out.auteurs = autre.auteurs
    if (out.citations or 0) < (autre.citations or 0):
        out.citations = autre.citations
    if out.est_oa is None:
        out.est_oa = autre.est_oa
    out.sujets = sorted(set(out.sujets) | set(autre.sujets))
    out.references = sorted(set(out.references) | set(autre.references))
    out.sources_multiples = sorted(set(out.sources_multiples) | {a.source, b.source})
    return out


def dedupliquer(travaux: list[Travail]) -> tuple[list[Travail], int]:
    """Déduplication par DOI puis par titre normalisé. -> (uniques, nb_supprimés)."""
    vus: dict[str, Travail] = {}
    orphelins: list[Travail] = []
    for t in travaux:
        cle = t.cle_dedup
        if cle in vus:
            vus[cle] = fusionner(vus[cle], t)
        else:
            vus[cle] = t
    # seconde passe : titres très proches sans DOI
    uniques = list(vus.values())
    titres = {}
    for t in uniques:
        if t.doi or not t.titre:
            continue
        k = " ".join(t.titre.lower().split())
        if k in titres:
            i = uniques.index(titres[k])
            uniques[i] = fusionner(uniques[i], t)
            orphelins.append(t)
        else:
            titres[k] = t
    supprimes = len(travaux) - len(uniques) + len(orphelins)
    return [t for t in uniques if t not in orphelins], supprimes
