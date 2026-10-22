# -*- coding: utf-8 -*-
"""Interface en ligne de commande `scitk`.

Exemples
  python3 -m scitk audit article.txt --out rapports/article
  python3 -m scitk biblio references.bib --auteur "Dupont"
  python3 -m scitk grim --mean 3.77 --sd 0.31 --n 60 --lo 1 --hi 5
  python3 -m scitk search "open science reproducibility" --sources openalex,crossref
  python3 -m scitk review corpus.csv --inclusion "randomi" --exclusion "animal"
  python3 -m scitk retractions --doi 10.1016/S0140-6736(97)11096-0
  python3 -m scitk catalogue --categorie audit
"""
from __future__ import annotations
import argparse
import json
import pathlib
import sys

from .audit import apa, grim, refs, retractions, transparency, duplicates, chiffres, report
from .search import federated, unpaywall
from .search.http import Client, ErreurReseau
from .search.models import Travail
from .pipeline.review import RevueSystematique


def _lire(chemin: str) -> str:
    return pathlib.Path(chemin).read_text(encoding="utf-8", errors="replace")


def _sortie(obj, args):
    if getattr(args, "json", False):
        print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))
    return obj


# ─────────────────────────── commandes ───────────────────────────
def cmd_audit(args):
    texte = _lire(args.fichier)
    refs_list = refs.charger_bibliographie(args.biblio) if args.biblio else None
    descriptifs = None
    if args.descriptifs:
        lignes = json.loads(_lire(args.descriptifs))
        descriptifs = lignes
    r = report.auditer_article(texte, references=refs_list, descriptifs=descriptifs,
                               auteur=args.auteur or "", base_retractations=args.base_retractations)
    if args.out:
        chemins = report.ecrire(r, args.out)
        print(f"Rapport écrit :\n  {chemins['markdown']}\n  {chemins['html']}\n  {chemins['json']}")
    if args.json:
        print(json.dumps({k: v for k, v in r.items() if k != "statistiques"}, indent=2,
                         ensure_ascii=False, default=str))
    else:
        s = r["synthese_statistique"]
        print(f"\n=== AUDIT ===\n{r['synthese_statistique']['resultats_extraits']} résultats · "
              f"{s['incoherents']} incohérences · {s['erreurs_de_decision']} erreurs de décision "
              f"· score {r['score_global']}/100 (gravité {r['gravite']})")
        for c in r["constats"][:25]:
            print(f"  [{c['severite'].upper():8}] {c['code']:22} {c['message'][:110]}")


def cmd_biblio(args):
    references = refs.charger_bibliographie(args.fichier)
    res = refs.audit_bibliographie(references, auteur_auditeur=args.auteur or "",
                                   base_retractations=args.base_retractations)
    if args.json:
        print(json.dumps(res.dict(), indent=2, ensure_ascii=False, default=str))
        return
    print(f"\n=== BIBLIOGRAPHIE : {res.entrees} références ===")
    print(f"Constats : {res.nb_problemes} · doublons : {len(res.doublons)} "
          f"· rétractées : {len(res.retractees)}")
    for c in sorted(res.constats, key=lambda c: c.severite):
        print(f"  [{c.severite.upper():8}] {c.code:20} {c.cible[:30]:30} {c.message[:90]}")


def cmd_grim(args):
    if args.sd is not None:
        v = grim.grimmer(args.mean, args.sd, args.n, args.decimals, args.decimals,
                         lo=args.lo, hi=args.hi)
    else:
        v = grim.grim(args.mean, args.n, args.decimals)
    print(json.dumps(v.dict(), indent=2, ensure_ascii=False))


def cmd_sprite(args):
    v = grim.sprite(args.mean, args.sd, args.n, args.lo, args.hi)
    print(json.dumps(v.dict(), indent=2, ensure_ascii=False))


def cmd_search(args):
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    try:
        res = federated.rechercher(Client(), args.requete, sources, args.limite,
                                   args.annee_min, email=args.email or "")
    except ErreurReseau as e:
        print(f"Réseau indisponible : {e}\n"
              "→ Utilisez le mode hors ligne : `scitk review corpus.csv` ou les fixtures de tests.",
              file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(res.dict(), indent=2, ensure_ascii=False, default=str))
        return
    print(f"\n{len(res.travaux)} travaux uniques ({res.total_brut} bruts, {res.doublons} doublons)")
    print("Sources :", ", ".join(f"{k}={v}" for k, v in res.par_source.items()))
    for e, m in res.erreurs.items():
        print(f"  ! {e}: {m[:120]}")
    for t in res.travaux[:args.limite]:
        print(f"\n• {t.titre[:110]}\n  {', '.join(t.auteurs[:3])} ({t.annee}) — {t.revue[:60]}")
        print(f"  DOI {t.doi or '—'} · {t.citations if t.citations is not None else '?'} citations "
              f"· sources {','.join(t.sources_multiples)}")


def cmd_review(args):
    revue = RevueSystematique(nom=args.nom, question=args.question or args.fichier)
    revue.criteres_inclusion = args.inclusion or []
    revue.criteres_exclusion = args.exclusion or []
    revue.annee_min = args.annee_min
    revue.exiger_resume = args.exiger_resume
    chemin = pathlib.Path(args.fichier)
    if chemin.suffix.lower() == ".json":
        donnees = json.loads(_lire(args.fichier))
        travaux = [Travail(**{k: v for k, v in d.items() if k in Travail.__dataclass_fields__})
                   for d in donnees]
    elif chemin.suffix.lower() in (".bib", ".ris"):
        travail = []
        for r in refs.charger_bibliographie(args.fichier):
            travail.append(Travail(titre=r.get("title", ""), doi=r.get("doi", ""),
                                   annee=int(r["year"]) if str(r.get("year", "")).isdigit() else None,
                                   auteurs=[r.get("author", "")] if r.get("author") else [],
                                   revue=r.get("journal", ""), resume=r.get("abstract", "")))
        travaux = travail
    else:
        import csv
        travaux = []
        with open(args.fichier, encoding="utf-8", errors="replace") as f:
            for ligne in csv.DictReader(f):
                travaux.append(Travail(
                    titre=ligne.get("titre") or ligne.get("title") or "",
                    doi=(ligne.get("doi") or ligne.get("DOI") or ""),
                    annee=int(ligne["annee"]) if (ligne.get("annee") or "").isdigit() else None,
                    auteurs=[a for a in (ligne.get("auteurs") or "").split(";") if a],
                    revue=ligne.get("revue") or ligne.get("journal") or "",
                    resume=ligne.get("resume") or ligne.get("abstract") or "",
                    citations=int(ligne["citations"]) if (ligne.get("citations") or "").isdigit() else None,
                    oa_url=ligne.get("oa_url") or "",
                    source=ligne.get("source") or "fichier",
                ))
    revue.par_source = {args.fichier: len(travaux)}
    revue.identifies = len(travaux)
    revue.travaux = travaux
    revue.journal.append({"etape": "import", "fichier": args.fichier, "n": len(travaux)})
    revue.dedupliquer().cribler().evaluer_acces()
    chemins = revue.exporter(args.sortie, args.prefixe)
    print(revue)
    for k, v in chemins.items():
        print(f"  {k:14} {v}")


def cmd_retractions(args):
    if args.doi:
        res = retractions.chercher(doi=args.doi, base=args.base)
        print(json.dumps(res or {"statut": "aucune rétractation connue dans la base"},
                         indent=2, ensure_ascii=False))
    elif args.texte:
        res = retractions.verifier_texte(_lire(args.texte), base=args.base)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(retractions.statistiques(base=args.base), indent=2, ensure_ascii=False))


def cmd_transparence(args):
    t = transparency.auditer(_lire(args.fichier))
    print(json.dumps(t.dict(), indent=2, ensure_ascii=False))


def cmd_similarite(args):
    docs = json.loads(_lire(args.fichier))
    if isinstance(docs, list):                       # [{id, texte}]
        docs = {d.get("id", str(i)): d.get("texte", "") for i, d in enumerate(docs)}
    res = duplicates.doublons_corpus(docs, seuil=args.seuil)
    print(json.dumps(res, indent=2, ensure_ascii=False))


def cmd_chiffres(args):
    valeurs = json.loads(_lire(args.fichier)) if args.fichier else args.valeurs
    out = {
        "decimales": chiffres.uniformite_decimales(valeurs),
        "benford": chiffres.benford(valeurs),
        "doublons": chiffres.doublons_numeriques(valeurs),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_catalogue(args):
    p = pathlib.Path(__file__).resolve().parent.parent / "catalog" / "outils.json"
    if not p.exists():
        print("catalog/outils.json absent : lancer `python3 scripts/build_catalog.py`.")
        return
    outils = json.loads(p.read_text(encoding="utf-8"))
    if args.categorie:
        outils = [o for o in outils if o.get("categorie") == args.categorie]
    outils.sort(key=lambda o: -(o.get("etoiles") or 0))
    print(f"{len(outils)} outils")
    for o in outils[:args.limite]:
        etoiles = o.get("etoiles") or "?"
        print(f"{str(etoiles):>7}★ {o['repo']:<48} {o.get('note', '')[:80]}")


def cmd_sources(args):
    for k, v in federated.SOURCES.items():
        print(f"{k:<18} {v}")


# ─────────────────────────── argparse ───────────────────────────
def construire_parseur() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="scitk",
                                description="Boîte à outils de recherche et d'audit scientifiques")
    sub = p.add_subparsers(dest="commande", required=True)

    a = sub.add_parser("audit", help="audit complet d'un article (texte)")
    a.add_argument("fichier")
    a.add_argument("--biblio", help="fichier .bib/.ris des références")
    a.add_argument("--descriptifs", help="JSON [{label,n,mean,sd}] pour GRIM/GRIMMER")
    a.add_argument("--auteur", help="nom de l'auteur audité (auto-citations)")
    a.add_argument("--base-retractations", dest="base_retractations")
    a.add_argument("--out", help="préfixe des rapports (.md/.html/.json)")
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_audit)

    b = sub.add_parser("biblio", help="audit d'une bibliographie")
    b.add_argument("fichier")
    b.add_argument("--auteur")
    b.add_argument("--base-retractations", dest="base_retractations")
    b.add_argument("--json", action="store_true")
    b.set_defaults(func=cmd_biblio)

    g = sub.add_parser("grim", help="test GRIM / GRIMMER")
    g.add_argument("--mean", type=float, required=True)
    g.add_argument("--sd", type=float)
    g.add_argument("--n", type=int, required=True)
    g.add_argument("--decimals", type=int, default=2)
    g.add_argument("--lo", type=int)
    g.add_argument("--hi", type=int)
    g.set_defaults(func=cmd_grim)

    s = sub.add_parser("sprite", help="test SPRITE (bornes exactes)")
    s.add_argument("--mean", type=float, required=True)
    s.add_argument("--sd", type=float, required=True)
    s.add_argument("--n", type=int, required=True)
    s.add_argument("--lo", type=int, default=1)
    s.add_argument("--hi", type=int, default=5)
    s.set_defaults(func=cmd_sprite)

    se = sub.add_parser("search", help="recherche fédérée en ligne")
    se.add_argument("requete")
    se.add_argument("--sources", default="openalex,crossref,europepmc")
    se.add_argument("--limite", type=int, default=20)
    se.add_argument("--annee-min", dest="annee_min", type=int)
    se.add_argument("--email", default="")
    se.add_argument("--json", action="store_true")
    se.set_defaults(func=cmd_search)

    r = sub.add_parser("review", help="pipeline de revue systématique (fichier local)")
    r.add_argument("fichier")
    r.add_argument("--nom", default="Revue systématique")
    r.add_argument("--question")
    r.add_argument("--inclusion", action="append")
    r.add_argument("--exclusion", action="append")
    r.add_argument("--annee-min", dest="annee_min", type=int)
    r.add_argument("--exiger-resume", dest="exiger_resume", action="store_true")
    r.add_argument("--sortie", default="revue")
    r.add_argument("--prefixe", default="revue")
    r.set_defaults(func=cmd_review)

    rt = sub.add_parser("retractions", help="vérification de rétractations")
    rt.add_argument("--doi")
    rt.add_argument("--texte")
    rt.add_argument("--base")
    rt.set_defaults(func=cmd_retractions)

    tr = sub.add_parser("transparence", help="indicateurs de transparence")
    tr.add_argument("fichier")
    tr.set_defaults(func=cmd_transparence)

    du = sub.add_parser("similarite", help="doublons / réutilisation de texte")
    du.add_argument("fichier")
    du.add_argument("--seuil", type=float, default=0.5)
    du.set_defaults(func=cmd_similarite)

    ch = sub.add_parser("chiffres", help="tests sur les chiffres (décimales, Benford)")
    ch.add_argument("fichier", nargs="?")
    ch.add_argument("--valeurs", nargs="*", type=float, default=[])
    ch.set_defaults(func=cmd_chiffres)

    ca = sub.add_parser("catalogue", help="catalogue des outils GitHub")
    ca.add_argument("--categorie")
    ca.add_argument("--limite", type=int, default=40)
    ca.set_defaults(func=cmd_catalogue)

    so = sub.add_parser("sources", help="sources de recherche disponibles")
    so.set_defaults(func=cmd_sources)
    return p


def main(argv=None):
    args = construire_parseur().parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
