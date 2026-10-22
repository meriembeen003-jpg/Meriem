# -*- coding: utf-8 -*-
"""Indicateurs de transparence d'un article (approche rtransparent / ODDPub).

Détecte la présence — et la qualité — des déclarations de politique de
recherche : données, code, préenregistrement, financement, conflits d'intérêts,
éthique, taille d'échantillon, protocole, enregistrement d'essai.

Aucune inférence : uniquement ce que le texte déclare, avec l'extrait exact
pour permettre la vérification humaine.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field, asdict

MOTIFS = {
    "donnees": {
        "libelle": "Disponibilité des données",
        "fort": [r"data\s+(?:are|is)\s+(?:publicly\s+)?available", r"donn[ée]es\s+(?:sont\s+)?(?:disponibles|accessibles|d[ée]pos[ée]es)",
                 r"data\s+availability\s+statement", r"d[ée]claration\s+de\s+disponibilit[ée]\s+des\s+donn[ée]es",
                 r"deposited\s+in\s+(?:the\s+)?(?:zenodo|dryad|osf|figshare|dataverse|github)",
                 r"d[ée]pos[ée]es?\s+(?:sur|dans)\s+(?:zenodo|dryad|osf|figshare|dataverse|github|hal)"],
        "faible": [r"(?:data|donn[ée]es).{0,40}(?:available|disponibles).{0,30}(?:up)?on\s+request",
                   r"sur\s+demande\s+aupr[èe]s"],
    },
    "code": {
        "libelle": "Disponibilité du code / des analyses",
        "fort": [r"code\s+(?:is\s+)?(?:publicly\s+)?available", r"source\s+code",
                 r"analys[ey]s?\s+(?:code|scripts?).{0,30}(?:available|deposited)",
                 r"(?:github\.com|gitlab\.com|zenodo\.org|figshare\.com)/\S+",
                 r"code\s+(?:de\s+)?(?:l['’]analyse|analyse).{0,30}(?:disponible|d[ée]pos[ée])"],
        "faible": [r"code.{0,30}(?:available|disponible).{0,30}on\s+request"],
    },
    "preregistration": {
        "libelle": "Préenregistrement / rapport enregistré",
        "fort": [r"pre[-\s]?regist(?:ered|ration)", r"pr[ée]?enregistr",
                 r"registered\s+report", r"osf\.io/[a-z0-9]{5}", r"aspredicted",
                 r"clinicaltrials\.gov|isrctn|euctr|chictr|anzctr",
                 r"enregistr[ée]?\s+(?:avant|aupr[èe]s|sur\s+osf)",
                 r"registered\s+(?:prospectively\s+)?(?:before|prior\s+to)"],
        "faible": [],
    },
    "financement": {
        "libelle": "Financement déclaré",
        "fort": [r"fund(?:ed|ing)\s+by", r"grant\s+(?:no|number|agreement)",
                 r"financ[ée]?\s+par", r"bourse\s+n[°o]?", r"this\s+work\s+was\s+supported\s+by"],
        "faible": [r"no\s+(?:specific\s+)?funding", r"aucun\s+financement"],
    },
    "conflits": {
        "libelle": "Conflits d'intérêts",
        "fort": [r"conflicts?\s+of\s+interest", r"competing\s+interests",
                 r"conflits?\s+d['’]int[ée]r[êe]ts?", r"declaration\s+of\s+interest",
                 r"the\s+authors\s+declare"],
        "faible": [],
    },
    "ethique": {
        "libelle": "Approbation éthique / consentement",
        "fort": [r"ethic(?:s|al)\s+(?:approval|committee|review\s+board)",
                 r"institutional\s+review\s+board|\bIRB\b",
                 r"comit[ée]\s+d['’][ée]thique", r"informed\s+consent",
                 r"consentement\s+[ée]clair[ée]"],
        "faible": [],
    },
    "puissance": {
        "libelle": "Justification de la taille d'échantillon",
        "fort": [r"power\s+analysis", r"sample\s+size\s+(?:calculation|justification|estimation)",
                 r"analyse\s+de\s+puissance", r"calcul\s+de\s+la\s+taille\s+d['’][ée]chantillon",
                 r"a\s+priori\s+(?:sample|power)"],
        "faible": [],
    },
    "protocole": {
        "libelle": "Protocole disponible",
        "fort": [r"study\s+protocol", r"protocole\s+(?:de\s+l['’][ée]tude|d['’][ée]tude|a\s+[ée]t[ée]|fut)",
                 r"protocol\s+(?:is\s+)?(?:available|published)"],
        "faible": [],
    },
    "limites": {
        "libelle": "Limites discutées",
        "fort": [r"\blimitations?\b", r"\blimites?\b"],
        "faible": [],
    },
    "materiel": {
        "libelle": "Matériel supplémentaire",
        "fort": [r"supplementary\s+(?:material|information|data)",
                 r"mat[ée]riel\s+suppl[ée]mentaire", r"supporting\s+information"],
        "faible": [],
    },
}

POIDS = {"donnees": 18, "code": 15, "preregistration": 15, "financement": 8,
         "conflits": 10, "ethique": 8, "puissance": 10, "protocole": 6,
         "limites": 5, "materiel": 5}


@dataclass
class Indicateur:
    cle: str
    libelle: str
    present: bool
    qualite: str            # 'fort', 'faible', 'absent'
    extrait: str = ""
    note: str = ""

    def dict(self):
        return asdict(self)


@dataclass
class AuditTransparence:
    indicateurs: list[Indicateur] = field(default_factory=list)
    score: int = 0
    manquants: list[str] = field(default_factory=list)

    def dict(self):
        return {"score": self.score, "manquants": self.manquants,
                "indicateurs": [i.dict() for i in self.indicateurs]}


def _extrait(texte: str, m: re.Match, marge: int = 90) -> str:
    return re.sub(r"\s+", " ", texte[max(0, m.start() - marge): m.end() + marge]).strip()


def auditer(texte: str) -> AuditTransparence:
    """Analyse les déclarations de transparence d'un article."""
    audit = AuditTransparence()
    total = 0
    for cle, spec in MOTIFS.items():
        trouve, qualite, ext = None, "absent", ""
        for motif in spec["fort"]:
            m = re.search(motif, texte, re.I)
            if m:
                trouve, qualite, ext = m, "fort", _extrait(texte, m)
                break
        if not trouve:
            for motif in spec["faible"]:
                m = re.search(motif, texte, re.I)
                if m:
                    trouve, qualite, ext = m, "faible", _extrait(texte, m)
                    break
        note = ""
        if cle == "donnees" and qualite == "faible":
            note = "Données « sur demande » : pratique faiblement vérifiable."
        if cle == "preregistration" and trouve:
            note = "Vérifier que le préenregistrement précède la collecte et couvre l'analyse rapportée."
        audit.indicateurs.append(Indicateur(cle, spec["libelle"], bool(trouve), qualite, ext, note))
        if trouve:
            total += POIDS[cle] * (1.0 if qualite == "fort" else 0.5)
        else:
            audit.manquants.append(spec["libelle"])
    audit.score = max(0, min(100, round(total)))
    return audit


def comparer(articles: dict[str, str]) -> dict:
    """Taux de présence de chaque indicateur sur un corpus d'articles."""
    audits = {k: auditer(v) for k, v in articles.items()}
    n = len(audits) or 1
    taux = {}
    for cle in MOTIFS:
        present = sum(1 for a in audits.values()
                      if any(i.cle == cle and i.present for i in a.indicateurs))
        taux[cle] = round(present / n, 3)
    return {"articles": len(audits), "taux_presence": taux,
            "score_moyen": round(sum(a.score for a in audits.values()) / n, 1)}
