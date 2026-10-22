# -*- coding: utf-8 -*-
"""Recherche fédérée : interroge plusieurs sources, fusionne et déduplique.

L'intérêt d'interroger plusieurs index : aucun ne couvre tout. Un article absent
d'OpenAlex mais présent dans Europe PMC et Crossref, ou inversement, révèle des
lacunes d'indexation (et parfois des références fantômes).
"""
from __future__ import annotations
from dataclasses import dataclass, field

from .http import Client, ErreurReseau
from .models import Travail, dedupliquer
from . import openalex, crossref, arxiv, europepmc, semanticscholar

SOURCES = {
    "openalex": "OpenAlex (260M+, tous domaines, 1800→)",
    "crossref": "Crossref (160M+ DOI, source de vérité des DOI)",
    "europepmc": "Europe PMC (40M+, biomédical + brevets + preprints)",
    "semanticscholar": "Semantic Scholar (220M+, citations et recommandations)",
    "arxiv": "arXiv (préprints 1991→, STIM)",
}


@dataclass
class ResultatFedere:
    travaux: list[Travail] = field(default_factory=list)
    erreurs: dict[str, str] = field(default_factory=dict)
    par_source: dict[str, int] = field(default_factory=dict)
    total_brut: int = 0
    doublons: int = 0

    def dict(self):
        return {"travaux": [t.dict() for t in self.travaux], "erreurs": self.erreurs,
                "par_source": self.par_source, "total_brut": self.total_brut,
                "doublons": self.doublons}


def rechercher(client: Client, requete: str, sources: list[str] | None = None,
               limite: int = 25, annee_min: int | None = None,
               annee_max: int | None = None, oa_seulement: bool = False,
               email: str = "", cle_s2: str = "") -> ResultatFedere:
    """Interroge les sources demandées ; une source en échec n'interrompt rien."""
    sources = sources or ["openalex", "crossref", "europepmc", "semanticscholar"]
    res = ResultatFedere()
    tout: list[Travail] = []
    for s in sources:
        try:
            if s == "openalex":
                lot = openalex.rechercher(client, requete, limite, annee_min, annee_max,
                                          oa_seulement, mailto=email)
            elif s == "crossref":
                lot = crossref.rechercher(client, requete, limite, annee_min, annee_max)
            elif s == "europepmc":
                lot = europepmc.rechercher(client, requete, limite, annee_min, oa_seulement)
            elif s == "semanticscholar":
                lot = semanticscholar.rechercher(client, requete, limite, annee_min, annee_max,
                                                 cle_api=cle_s2)
            elif s == "arxiv":
                lot = arxiv.rechercher(client, requete, limite)
            else:
                res.erreurs[s] = "source inconnue"
                continue
        except (ErreurReseau, ValueError, KeyError) as e:
            res.erreurs[s] = str(e)[:200]
            res.par_source[s] = 0
            continue
        res.par_source[s] = len(lot)
        tout.extend(lot)
    res.total_brut = len(tout)
    uniques, supprimes = dedupliquer(tout)
    res.doublons = supprimes
    for t in uniques:
        t.sources_multiples = sorted(set(t.sources_multiples) | {t.source})
    res.travaux = sorted(uniques, key=lambda t: (-len(t.sources_multiples), -(t.citations or 0)))
    return res


def couverture(res: ResultatFedere) -> dict:
    """Quelle part des travaux est indexée par plusieurs sources ?"""
    n = len(res.travaux) or 1
    multi = sum(1 for t in res.travaux if len(t.sources_multiples) > 1)
    return {
        "travaux_uniques": len(res.travaux),
        "vus_dans_plusieurs_sources": multi,
        "part_multi_sources": round(multi / n, 3),
        "par_source": res.par_source,
        "erreurs": res.erreurs,
        "note": "un travail vu dans une seule source est souvent un preprint, "
                "un chapitre ou un document peu indexé",
    }
