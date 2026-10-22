# -*- coding: utf-8 -*-
"""Pipeline de revue systématique, conforme à la logique PRISMA 2020.

Étapes : identification multi-sources → dédoublonnage → criblage (critères
d'inclusion/exclusion par expressions régulières sur titre et résumé) →
évaluation de la disponibilité des textes → export → rapport traçable.

Tout est déterministe et journalisé : chaque décision est reproductible.
"""
from __future__ import annotations
import json
import pathlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..search.models import Travail, dedupliquer
from ..search.federated import rechercher, ResultatFedere
from ..search.http import Client
from . import export


@dataclass
class Decision:
    travail: Travail
    motif: str
    regle: str = ""

    def dict(self):
        return {"titre": self.travail.titre, "doi": self.travail.doi,
                "annee": self.travail.annee, "motif": self.motif, "regle": self.regle}


@dataclass
class RevueSystematique:
    nom: str = "Revue systématique"
    question: str = ""
    criteres_inclusion: list[str] = field(default_factory=list)
    criteres_exclusion: list[str] = field(default_factory=list)
    champs_criblage: tuple[str, ...] = ("titre", "resume")
    annee_min: int | None = None
    exiger_resume: bool = False
    langues: list[str] = field(default_factory=list)

    travaux: list[Travail] = field(default_factory=list)
    exclus: list[Decision] = field(default_factory=list)
    journal: list[dict] = field(default_factory=list)
    compteurs: dict = field(default_factory=dict)
    par_source: dict = field(default_factory=dict)
    doublons: int = 0
    identifies: int = 0

    # ─────────────────────────── étapes ───────────────────────────
    def identifier(self, source: str, travaux: list[Travail]) -> "RevueSystematique":
        for t in travaux:
            t.sources_multiples = sorted(set(t.sources_multiples) | {source})
        self.travaux.extend(travaux)
        self.identifies += len(travaux)
        self.par_source[source] = self.par_source.get(source, 0) + len(travaux)
        self.journal.append({"etape": "identification", "source": source,
                             "n": len(travaux)})
        return self

    def identifier_en_ligne(self, requete: str, sources: list[str] | None = None,
                            limite: int = 50, email: str = "", client: Client | None = None) -> dict:
        res = rechercher(client or Client(), requete, sources, limite,
                         annee_min=self.annee_min, email=email)
        for s, n in res.par_source.items():
            self.par_source[s] = self.par_source.get(s, 0) + n
        self.identifies += res.total_brut
        self.travaux.extend(res.travaux)
        self.doublons += res.doublons
        self.journal.append({"etape": "identification_en_ligne", "requete": requete,
                             "erreurs": res.erreurs, "n_brut": res.total_brut})
        return {"total_brut": res.total_brut, "erreurs": res.erreurs}

    def dedupliquer(self) -> "RevueSystematique":
        avant = len(self.travaux)
        uniques, supprimes = dedupliquer(self.travaux)
        self.travaux = uniques
        self.doublons = max(self.doublons, supprimes)
        self.journal.append({"etape": "deduplication", "avant": avant,
                             "apres": len(uniques), "supprimes": supprimes})
        return self

    def _texte(self, t: Travail) -> str:
        morceaux = []
        for c in self.champs_criblage:
            v = getattr(t, c, "") or ""
            morceaux.append(v)
        return " ".join(morceaux).lower()

    def cribler(self) -> "RevueSystematique":
        gardes = []
        motifs: dict[str, int] = {}
        for t in self.travaux:
            texte = self._texte(t)
            # 1) exclusion explicite
            exclu = False
            for regle in self.criteres_exclusion:
                if re.search(regle, texte, re.I):
                    self.exclus.append(Decision(t, f"critère d'exclusion : {regle}", regle))
                    motifs[f"exclusion : {regle}"] = motifs.get(f"exclusion : {regle}", 0) + 1
                    exclu = True
                    break
            if exclu:
                continue
            # 2) année
            if self.annee_min and t.annee and t.annee < self.annee_min:
                self.exclus.append(Decision(t, f"antérieur à {self.annee_min}", "annee_min"))
                motifs["antérieur à l'année plancher"] = motifs.get("antérieur à l'année plancher", 0) + 1
                continue
            # 3) langue
            if self.langues and t.langue and t.langue.lower() not in [l.lower() for l in self.langues]:
                self.exclus.append(Decision(t, f"langue {t.langue}", "langue"))
                motifs["langue non éligible"] = motifs.get("langue non éligible", 0) + 1
                continue
            # 4) résumé exigé
            if self.exiger_resume and not (t.resume or "").strip():
                self.exclus.append(Decision(t, "résumé absent", "resume"))
                motifs["résumé absent"] = motifs.get("résumé absent", 0) + 1
                continue
            # 5) inclusion : au moins un critère doit apparaître (si fournis)
            if self.criteres_inclusion and not any(re.search(r, texte, re.I)
                                                   for r in self.criteres_inclusion):
                self.exclus.append(Decision(t, "aucun critère d'inclusion", "inclusion"))
                motifs["aucun critère d'inclusion"] = motifs.get("aucun critère d'inclusion", 0) + 1
                continue
            gardes.append(t)
        cribles = len(self.travaux)
        self.travaux = gardes
        self.motifs_exclusion = motifs
        self.journal.append({"etape": "criblage", "cribles": cribles,
                             "inclus": len(gardes), "exclus": len(self.exclus)})
        return self

    def evaluer_acces(self) -> "RevueSystematique":
        dispo = sum(1 for t in self.travaux if t.oa_url)
        self.journal.append({"etape": "acces", "avec_pdf_oa": dispo,
                             "sans_pdf_oa": len(self.travaux) - dispo})
        self.acces = {"avec_pdf_oa": dispo, "sans_pdf_oa": len(self.travaux) - dispo}
        return self

    # ─────────────────────────── sorties ───────────────────────────
    def prisma(self) -> dict:
        return {
            "question": self.question,
            "identifies": self.identifies,
            "par_source": self.par_source,
            "doublons": self.doublons,
            "cribles": self.identifies - self.doublons,
            "exclus_titre": len(self.exclus),
            "motifs_exclusion": getattr(self, "motifs_exclusion", {}),
            "textes_recherches": len(self.travaux),
            "non_disponibles": getattr(self, "acces", {}).get("sans_pdf_oa", 0),
            "inclus": len(self.travaux),
            "inclus_meta": getattr(self, "inclus_meta", 0),
        }

    def exporter(self, dossier: str, prefixe: str = "revue") -> dict:
        d = pathlib.Path(dossier)
        d.mkdir(parents=True, exist_ok=True)
        chemins = export.exporter_tout(self.travaux, dossier, prefixe)
        (d / f"{prefixe}_prisma.json").write_text(
            json.dumps(self.prisma(), indent=2, ensure_ascii=False), encoding="utf-8")
        (d / f"{prefixe}_journal.json").write_text(
            json.dumps({"nom": self.nom, "question": self.question,
                        "horodatage": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "criteres_inclusion": self.criteres_inclusion,
                        "criteres_exclusion": self.criteres_exclusion,
                        "journal": self.journal,
                        "exclus": [e.dict() for e in self.exclus]},
                       indent=2, ensure_ascii=False), encoding="utf-8")
        (d / f"{prefixe}_prisma.txt").write_text(export.flux_prisma(self.prisma()), encoding="utf-8")
        (d / f"{prefixe}_rapport.md").write_text(self.rapport(), encoding="utf-8")
        chemins.update({"prisma_json": str(d / f"{prefixe}_prisma.json"),
                        "journal_json": str(d / f"{prefixe}_journal.json"),
                        "rapport": str(d / f"{prefixe}_rapport.md"),
                        "flux_prisma": str(d / f"{prefixe}_prisma.txt")})
        return chemins

    def rapport(self) -> str:
        c = self.prisma()
        L = [f"# {self.nom}", "",
             f"**Question :** {self.question or '—'}", "",
             f"*Généré le {datetime.now(timezone.utc).isoformat(timespec='seconds')}*", "",
             "## Flux PRISMA 2020", "",
             "| Étape | Nombre |", "|---|---|",
             f"| Enregistrements identifiés | {c['identifies']} |",
             f"| Doublons supprimés | {c['doublons']} |",
             f"| Criblés (titre/résumé) | {c['cribles']} |",
             f"| Exclus | {c['exclus_titre']} |",
             f"| Textes intégraux évalués | {c['textes_recherches']} |",
             f"| **Inclus** | **{c['inclus']}** |", "",
             "### Identification par source", ""]
        for s, n in c["par_source"].items():
            L.append(f"- {s} : {n}")
        if c["motifs_exclusion"]:
            L += ["", "### Motifs d'exclusion", ""]
            for m, n in sorted(c["motifs_exclusion"].items(), key=lambda x: -x[1]):
                L.append(f"- {m} : {n}")
        L += ["", "### Critères appliqués", ""]
        L += [f"- Inclusion : `{r}`" for r in self.criteres_inclusion] or ["- Inclusion : aucun"]
        L += [f"- Exclusion : `{r}`" for r in self.criteres_exclusion] or ["- Exclusion : aucun"]
        L += ["", "### Études incluses", ""]
        for t in sorted(self.travaux, key=lambda x: (x.annee or 0), reverse=True):
            aut = ", ".join(t.auteurs[:3]) + (" et al." if len(t.auteurs) > 3 else "")
            L.append(f"- **{t.titre}** — {aut} ({t.annee or 's.d.'}). *{t.revue}*. "
                     + (f"DOI : {t.doi}" if t.doi else "sans DOI"))
        return "\n".join(L) + "\n"

    def __str__(self):
        c = self.prisma()
        return (f"<Revue {self.nom!r} : {c['identifies']} identifiés, {c['doublons']} doublons, "
                f"{c['exclus_titre']} exclus, {c['inclus']} inclus>")
