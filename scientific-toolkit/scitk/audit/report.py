# -*- coding: utf-8 -*-
"""Génération de rapports d'audit (Markdown, HTML, JSON).

Le rapport agrège : cohérence statistique (APA), tests GRIM/GRIMMER/SPRITE,
indicateurs de transparence, statut des références et rétractations, tests de
distribution (p-curve, décimales, Benford, doublons de texte).
"""
from __future__ import annotations
import html
import json
import pathlib
from datetime import datetime, timezone

from . import apa, grim, pcurve, chiffres, refs, retractions, transparency, duplicates

NIVEAU_ORDRE = {"critique": 0, "majeur": 1, "mineur": 2, "info": 3}
BADGES = {"critique": "🔴 CRITIQUE", "majeur": "🟠 MAJEUR", "mineur": "🟡 MINEUR", "info": "🔵 INFO"}


def _tri_constats(constats: list[dict]) -> list[dict]:
    return sorted(constats, key=lambda c: (NIVEAU_ORDRE.get(c.get("severite", "info"), 9),
                                           c.get("code", "")))


def auditer_article(texte: str, references: list[dict] | None = None,
                    descriptifs: list[dict] | None = None,
                    auteur: str = "", base_retractations: str | None = None) -> dict:
    """Audit complet d'un article : renvoie une structure sérialisable."""
    a = apa.audit_texte(texte)
    resultat = {
        "horodatage": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "statistiques": a.dict(),
        "synthese_statistique": {
            "resultats_extraits": a.nb_resultats,
            "significatifs": a.nb_significatifs,
            "incoherents": a.nb_incoherents,
            "arrondis_stricts": a.nb_arrondis,
            "erreurs_de_decision": a.nb_erreurs_decision,
            "score_coherence": a.score,
            "taux_incoherence": round(apa.taux_incoherence(a), 4),
        },
        "transparence": transparency.auditer(texte).dict(),
    }
    pvals = [r.p_rapportee for r in a.resultats if r.p_rapportee and 0 < r.p_rapportee <= 1]
    resultat["distribution_p"] = {
        "pcurve": pcurve.pcurve(pvals),
        "exces": pcurve.exces_significativite(pvals),
        "variance": pcurve.variance_insuffisante(pvals),
    }
    if descriptifs:
        resultat["grim"] = grim.audit_descriptifs(descriptifs)
    if references:
        b = refs.audit_bibliographie(references, auteur_auditeur=auteur,
                                     base_retractations=base_retractations)
        resultat["bibliographie"] = b.dict()
    resultat["constats"] = _tri_constats(_tous_constats(resultat))
    resultat["gravite"] = _gravite(resultat["constats"])
    resultat["score_global"] = _score_global(resultat)
    return resultat


def _tous_constats(r: dict) -> list[dict]:
    out = []
    for res in r["statistiques"]["resultats"]:
        for c in res["constats"]:
            out.append({**c, "source": f"{res['type']} — {res['df_texte']}",
                        "valeur": f"p rapportée {res['p_rapportee']} / recalculée "
                                  f"{round(res['p_calculee'], 4) if res['p_calculee'] is not None else '—'}"})
    for c in r["statistiques"]["constats"]:
        out.append({**c, "source": "texte"})
    if "grim" in r:
        for d in r["grim"]["descriptifs"]:
            if not d["grim"]["possible"]:
                out.append({"code": "grim_impossible", "severite": "critique",
                            "message": d["grim"]["message"],
                            "source": f"descriptif {d.get('label', '')}", "extrait": ""})
            for test in ("grimmer", "sprite"):
                g = d.get(test)
                if g and not g["possible"] and d["grim"]["possible"]:
                    out.append({"code": f"{test}_impossible", "severite": "critique",
                                "message": g["message"],
                                "source": f"descriptif {d.get('label', '')}", "extrait": ""})
    if "bibliographie" in r:
        for c in r["bibliographie"]["constats"]:
            out.append({"code": c["code"], "severite": c["severite"], "message": c["message"],
                        "source": f"bibliographie — {c['cible']}", "extrait": ""})
    return out


def _gravite(constats: list[dict]) -> str:
    if any(c["severite"] == "critique" for c in constats):
        return "critique"
    if any(c["severite"] == "majeur" for c in constats):
        return "majeur"
    if any(c["severite"] == "mineur" for c in constats):
        return "mineur"
    return "aucune"


def _score_global(r: dict) -> int:
    """Score global 0–100 : cohérence statistique (55 %), transparence (25 %),
    bibliographie (20 %), moins une pénalité explicite par constat critique.

    Le barème est volontairement transparent : chaque point retiré correspond à
    un constat nommé, consultable dans la section 2 du rapport.
    """
    stat = r["synthese_statistique"]["score_coherence"]
    trans = r["transparence"]["score"]
    biblio = 100
    if "bibliographie" in r:
        for c in r["bibliographie"]["constats"]:
            biblio -= {"critique": 30, "majeur": 12, "mineur": 4, "info": 0}.get(c["severite"], 0)
        biblio = max(0, biblio)
    base = 0.55 * stat + 0.25 * trans + 0.20 * biblio
    critiques = sum(1 for c in r["constats"] if c["severite"] == "critique")
    majeurs = sum(1 for c in r["constats"] if c["severite"] == "majeur")
    score = base - 2.0 * critiques - 1.0 * majeurs
    return max(0, min(100, round(score)))


# ─────────────────────────── rendu Markdown ───────────────────────────
def markdown(r: dict, titre: str = "Rapport d'audit scientifique") -> str:
    s = r["synthese_statistique"]
    t = r["transparence"]
    L = [f"# {titre}", "",
         f"*Généré le {r['horodatage']} par `scitk` — audit reproductible, hors ligne.*", "",
         f"**Score global : {r['score_global']}/100** · Gravité : **{r['gravite'].upper()}**", "",
         "## 1. Synthèse", "",
         "| Indicateur | Valeur |", "|---|---|",
         f"| Résultats statistiques extraits | {s['resultats_extraits']} |",
         f"| Résultats significatifs (p < .05) | {s['significatifs']} |",
         f"| Incohérences statistique ↔ p (majeures) | {s['incoherents']} |",
         f"| Écarts d'arrondi stricts | {s.get('arrondis_stricts', 0)} |",
         f"| Erreurs de décision | {s['erreurs_de_decision']} |",
         f"| Taux d'incohérence | {s['taux_incoherence']:.1%} |",
         f"| Score de cohérence statistique | {s['score_coherence']}/100 |",
         f"| Score de transparence | {t['score']}/100 |", ""]

    if r["constats"]:
        L += ["## 2. Constats (par gravité)", "",
              "| Gravité | Code | Source | Message |", "|---|---|---|---|"]
        for c in r["constats"]:
            L.append(f"| {BADGES.get(c['severite'], c['severite'])} | `{c['code']}` | "
                     f"{c['source']} | {c['message'].replace('|', '/')} |")
        L.append("")
    else:
        L += ["## 2. Constats", "", "Aucun constat : le texte est cohérent au regard des tests appliqués.", ""]

    L += ["## 3. Recalcul des résultats", "",
          "| Type | Test | p rapportée | p recalculée | Écart | Constats |",
          "|---|---|---|---|---|---|"]
    for res in r["statistiques"]["resultats"]:
        codes = ", ".join(f"`{c['code']}`" for c in res["constats"]) or "—"
        p_rep = f"{res['p_rapportee']:.4f}" if res["p_rapportee"] is not None else "—"
        p_cal = f"{res['p_calculee']:.4f}" if res["p_calculee"] is not None else "—"
        ecart = f"{res['ecart']:.4f}" if res.get("ecart") is not None else "—"
        L.append(f"| {res['type']} | `{res['df_texte']} = {res['statistique']}` | {p_rep} | {p_cal} | {ecart} | {codes} |")
    L.append("")

    L += ["## 4. Transparence", "", "| Indicateur | Présence | Qualité |", "|---|---|---|"]
    for i in t["indicateurs"]:
        L.append(f"| {i['libelle']} | {'✅' if i['present'] else '❌'} | {i['qualite']} |")
    if t["manquants"]:
        L += ["", "**Éléments absents :** " + ", ".join(t["manquants"])]
    L.append("")

    d = r["distribution_p"]
    L += ["## 5. Distribution des p-values", ""]
    pc = d["pcurve"]
    if "n_significatifs" in pc:
        L += [f"- p-curve : {pc['part_p_inf_025']:.0%} des p < .05 sont < .025 "
              f"(test binomial p = {pc['test_skew_binomial_p']}) → {pc['interpretation']}"]
    ex = d["exces"]
    if "z" in ex:
        L += [f"- Excès de significativité : {ex['observes_significatifs']}/{ex['n_tests']} "
              f"observés vs {ex['attendus']} attendus (z = {ex['z']}, p = {ex['p']})"]
    va = d["variance"]
    if "chi2" in va:
        L += [f"- Variance des p : {va['variance_observee']} (attendu ≈ 0.0833), "
              f"p = {va['p_variance_trop_faible']} → {va['interpretation']}"]
    L.append("")

    if "grim" in r:
        L += ["## 6. Tests GRIM / GRIMMER", "", "| Descriptif | n | M | SD | Résultat |", "|---|---|---|---|---|"]
        for x in r["grim"]["descriptifs"]:
            ok = "✅" if x["grim"]["possible"] else "❌ impossible"
            L.append(f"| {x.get('label', '')} | {x['n']} | {x['mean']} | {x.get('sd', '—')} | {ok} |")
        L.append("")

    if "bibliographie" in r:
        b = r["bibliographie"]
        L += ["## 7. Bibliographie", "",
              f"- Références analysées : **{b['entrees']}**",
              f"- Constats : **{b['nb_constats']}**",
              f"- Sans DOI : **{b['stats'].get('sans_doi', 0)}** "
              f"({b['stats'].get('part_sans_doi', 0):.0%})",
              f"- Doublons détectés : **{len(b['doublons'])}**",
              f"- Références rétractées : **{len(b['retractees'])}**"]
        if b["retractees"]:
            L += ["", "| DOI | Titre | Motif |", "|---|---|---|"]
            for rr in b["retractees"]:
                L.append(f"| {rr.get('doi', '')} | {rr.get('titre', '')} | {rr.get('motif', '')[:120]} |")
        L.append("")

    L += ["---", "",
          "### Portée et limites", "",
          "Cet audit est **automatique et non décisionnel** : il signale des divergences "
          "arithmétiques et des déclarations manquantes, pas une fraude. Chaque constat doit "
          "être vérifié sur le manuscrit, les données et le code. Les erreurs de recalcul "
          "peuvent venir de la mise en forme (arrondis, tests unilatéraux, corrections).", "",
          "Tests appliqués : recalcul APA (t, F, χ², r, z), GRIM/GRIMMER/SPRITE, p-curve, "
          "excès de significativité, variance insuffisante, distribution des décimales, "
          "Benford, doublons de texte, indicateurs de transparence, rétractations."]
    return "\n".join(L)


def html_depuis_markdown(md: str, titre: str = "Rapport d'audit") -> str:
    """HTML autonome minimal (sans dépendance) : tableaux, titres, listes."""
    import re
    lignes, out, dans_table, dans_liste = md.split("\n"), [], False, False
    for ligne in lignes:
        if ligne.startswith("|"):
            cellules = [c.strip() for c in ligne.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cellules):
                continue
            if not dans_table:
                out.append("<table>")
                dans_table = True
                out.append("<tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in cellules) + "</tr>")
            else:
                out.append("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in cellules) + "</tr>")
            continue
        if dans_table:
            out.append("</table>")
            dans_table = False
        if ligne.startswith("- "):
            if not dans_liste:
                out.append("<ul>")
                dans_liste = True
            out.append(f"<li>{_inline(ligne[2:])}</li>")
            continue
        if dans_liste:
            out.append("</ul>")
            dans_liste = False
        if ligne.startswith("#"):
            niveau = len(ligne) - len(ligne.lstrip("#"))
            out.append(f"<h{niveau}>{_inline(ligne[niveau:].strip())}</h{niveau}>")
        elif ligne.strip() == "---":
            out.append("<hr>")
        elif ligne.strip():
            out.append(f"<p>{_inline(ligne)}</p>")
    if dans_table:
        out.append("</table>")
    if dans_liste:
        out.append("</ul>")
    corps = "\n".join(out)
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>{html.escape(titre)}</title><style>
:root{{--b:#0f172a;--a:#0ea5e9;--r:#dc2626}}
*{{box-sizing:border-box}}body{{margin:0;padding:2.5rem 1.25rem;background:#f8fafc;color:var(--b);
font:16px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:980px;margin:0 auto;background:#fff;padding:2.5rem;border-radius:14px;
box-shadow:0 10px 30px rgba(15,23,42,.08)}}
h1{{font-size:1.9rem;margin-top:0}}h2{{margin-top:2.2rem;font-size:1.35rem;border-bottom:2px solid #e2e8f0;padding-bottom:.35rem}}
h3{{font-size:1.05rem}}table{{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.9rem}}
th,td{{border:1px solid #e2e8f0;padding:.5rem .6rem;text-align:left;vertical-align:top}}
th{{background:#f1f5f9}}code{{background:#f1f5f9;padding:.1rem .3rem;border-radius:4px;font-size:.85em}}
hr{{border:0;border-top:1px solid #e2e8f0;margin:2rem 0}}
ul{{padding-left:1.2rem}}p{{margin:.6rem 0}}
</style></head><body><main>{corps}</main></body></html>"""


def _inline(t: str) -> str:
    import re
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
    return t


def ecrire(r: dict, prefixe: str, titre: str = "Rapport d'audit scientifique") -> dict:
    """Écrit les trois formats et renvoie les chemins."""
    p = pathlib.Path(prefixe)
    p.parent.mkdir(parents=True, exist_ok=True)
    md = markdown(r, titre)
    (p.with_suffix(".md")).write_text(md, encoding="utf-8")
    (p.with_suffix(".html")).write_text(html_depuis_markdown(md, titre), encoding="utf-8")
    (p.with_suffix(".json")).write_text(json.dumps(r, indent=2, ensure_ascii=False,
                                                   default=str), encoding="utf-8")
    return {"markdown": str(p.with_suffix(".md")), "html": str(p.with_suffix(".html")),
            "json": str(p.with_suffix(".json"))}
