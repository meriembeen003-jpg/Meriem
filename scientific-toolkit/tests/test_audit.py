# -*- coding: utf-8 -*-
"""Tests du moteur d'audit : APA, GRIM, chiffres, doublons, bibliographie, PRISMA."""
import json, math, pathlib, sys, unittest

RACINE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
from scitk.audit import apa, grim, chiffres, duplicates, refs, transparency, retractions
from scitk.pipeline.review import RevueSystematique
from scitk.search.models import Travail, dedupliquer
from scitk.search.http import Client, TransportFactice
from scitk.search import crossref, openalex, europepmc


def _codes(audit):
    return [c.code for c in audit.constats] + [c.code for r in audit.resultats for c in r.constats]


class TestAPA(unittest.TestCase):
    def test_extraction(self):
        txt = ("Le groupe différait, t(38) = 2.15, p = .034 ; l'interaction était "
               "F(2, 45) = 3.21, p = .049 ; χ²(1, N = 140) = 4.50, p = .034 ; "
               "la corrélation valait r(28) = .41, p = .021 ; z = 1.96, p = .050.")
        a = apa.audit_texte(txt)
        self.assertEqual(a.nb_resultats, 5)
        types = [r.type for r in a.resultats]
        self.assertEqual(types, ["F", "chi2", "t", "r", "z"])

    def test_recalcul_exact(self):
        a = apa.audit_texte("t(38) = 2.15, p = .038")
        self.assertAlmostEqual(a.resultats[0].p_calculee, 0.0380, places=3)
        self.assertEqual(a.resultats[0].constats, [])

    def test_erreur_de_decision(self):
        # t(28)=1.85 -> p=.0749, mais l'article annonce p=.042 (significatif)
        a = apa.audit_texte("La différence était significative, t(28) = 1.85, p = .042.")
        codes = [c.code for c in a.resultats[0].constats]
        self.assertIn("erreur_decision", codes)
        self.assertEqual(a.nb_erreurs_decision, 1)

    def test_p_zero(self):
        a = apa.audit_texte("Le modèle était significatif, F(1, 20) = 9.5, p = .000.")
        self.assertIn("p_zero", _codes(a))

    def test_inegalite_fausse(self):
        a = apa.audit_texte("t(10) = 0.10, p < .05")
        self.assertIn("incoherence_inegalite", [c.code for c in a.resultats[0].constats])

    def test_arrondi_statistique_tolere(self):
        # F(2,45)=3.21 -> p=.0498 ; p=.049 est compatible avec l'arrondi de F
        a = apa.audit_texte("F(2, 45) = 3.21, p = .049")
        severites = [c.severite for c in a.resultats[0].constats]
        self.assertNotIn("majeur", severites)

    def test_score_borne(self):
        a = apa.audit_texte("t(38) = 2.15, p = .034")
        self.assertTrue(0 <= a.score <= 100)

    def test_r_invalide(self):
        a = apa.audit_texte("r(20) = 1.4, p = .02")
        self.assertIn("r_invalide", [c.code for c in a.resultats[0].constats])


class TestGRIM(unittest.TestCase):
    def test_grim_possible(self):
        self.assertTrue(grim.grim(1.44, 25, 2).possible)
        self.assertTrue(grim.grim(3.77, 60, 2).possible)

    def test_grim_impossible(self):
        self.assertFalse(grim.grim(1.43, 25, 2).possible)
        self.assertFalse(grim.grim(5.19, 18, 2).possible)
        self.assertFalse(grim.grim(3.11, 60, 2).possible)

    def test_borne_sd(self):
        smin, smax = grim._bornes_sd(40, 120, 1, 5)
        self.assertAlmostEqual(smin, 0.0, places=6)
        self.assertAlmostEqual(smax, 2.0255, places=3)

    def test_sprite(self):
        self.assertTrue(grim.sprite(3.0, 1.2, 40, 1, 5).possible)
        self.assertFalse(grim.sprite(4.9, 0.05, 40, 1, 5).possible)
        self.assertFalse(grim.sprite(2.0, 3.0, 30, 1, 5).possible)

    def test_descriptifs(self):
        res = grim.audit_descriptifs([
            {"label": "ok", "n": 60, "mean": 3.77, "sd": 1.02},
            {"label": "ko", "n": 18, "mean": 5.19, "sd": 0.28},
        ], lo=1, hi=5)
        self.assertEqual(res["nb_incoherents"], 1)


class TestChiffres(unittest.TestCase):
    def test_decimales_uniformes(self):
        vals = [round(1 + (i * 7 % 100) / 100, 2) for i in range(200)]
        res = chiffres.uniformite_decimales(vals)
        self.assertIn("p", res)

    def test_pourcentages(self):
        self.assertTrue(chiffres.pourcentages(100, [52.0, 48.0])["coherent"])
        self.assertFalse(chiffres.pourcentages(100, [52.0, 52.0])["coherent"])

    def test_effectifs(self):
        self.assertTrue(chiffres.effectifs(140, [70, 70])["coherent"])
        self.assertFalse(chiffres.effectifs(140, [70, 60])["coherent"])


class TestDoublons(unittest.TestCase):
    def test_jaccard_identique(self):
        a = "essai controle randomise evaluation programme remediation lecture eleves"
        self.assertAlmostEqual(duplicates.jaccard(duplicates.shingles(a),
                                                  duplicates.shingles(a)), 1.0)

    def test_corpus(self):
        docs = json.loads((RACINE / "data" / "corpus_textes.json").read_text())
        res = duplicates.doublons_corpus(docs, seuil=0.5)
        paires = {(p["a"], p["b"]) for p in res["paires_suspectes"]}
        self.assertTrue({("article_A", "article_B")} <= paires)
        self.assertNotIn(("article_A", "article_D"), paires)


class TestBiblio(unittest.TestCase):
    def test_parsing_et_audit(self):
        refs_list = refs.charger_bibliographie(str(RACINE / "data" / "references_exemple.bib"))
        self.assertEqual(len(refs_list), 8)
        audit = refs.audit_bibliographie(refs_list)
        codes = [c.code for c in audit.constats]
        self.assertIn("doublon_doi", codes)
        self.assertIn("doi_invalide", codes)
        self.assertIn("annee_aberrante", codes)
        self.assertIn("retractee", codes)
        self.assertGreaterEqual(len(audit.retractees), 1)

    def test_doi_valide(self):
        self.assertTrue(refs.doi_valide("10.1038/s41586-023-05742-0"))
        self.assertFalse(refs.doi_valide("doi-invalide-2019"))


class TestRetractions(unittest.TestCase):
    def test_lookup(self):
        r = retractions.chercher(doi="10.1038/s41586-023-05742-0")
        self.assertIsNotNone(r)
        self.assertIn("superconductivity", r["titre"])
        self.assertIsNone(retractions.chercher(doi="10.1000/inexistant.1"))


class TestTransparence(unittest.TestCase):
    def test_indicateurs(self):
        texte = ("Data availability statement: all data are available at https://zenodo.org/1234. "
                 "The authors declare no conflicts of interest. Funding: this work was supported by "
                 "grant ANR-19. Code is available at https://github.com/x/y. "
                 "Ethical approval was granted by the IRB. A power analysis was conducted.")
        t = transparency.auditer(texte)
        presents = {i.cle for i in t.indicateurs if i.present}
        for cle in ("donnees", "code", "conflits", "ethique", "puissance", "financement"):
            self.assertIn(cle, presents)
        self.assertGreater(t.score, 50)


class TestReview(unittest.TestCase):
    def test_pipeline(self):
        import csv
        travaux = []
        with open(RACINE / "data" / "corpus_exemple.csv", encoding="utf-8") as f:
            for ligne in csv.DictReader(f):
                travaux.append(Travail(titre=ligne["titre"], doi=ligne["doi"],
                                       annee=int(ligne["annee"]), resume=ligne["resume"]))
        revue = RevueSystematique(nom="Test", question="Remédiation lecture")
        revue.criteres_inclusion = ["lecture|reading"]
        revue.criteres_exclusion = ["rodent|animal"]
        revue.identifies = len(travaux)
        revue.travaux = travaux
        revue.dedupliquer().cribler()
        p = revue.prisma()
        self.assertLess(p["inclus"], 12)
        self.assertGreaterEqual(p["doublons"], 2)
        titres = {t.titre for t in revue.travaux}
        self.assertFalse(any("rodent" in t.lower() for t in titres))


class TestClientsHorsLigne(unittest.TestCase):
    """Les tests utilisent des fixtures : aucune requête réseau nécessaire."""

    def test_crossref_fixture(self):
        fixture = json.dumps({"message": {"items": [{
            "DOI": "10.1234/test.1", "title": ["Un article de test"],
            "author": [{"given": "Marie", "family": "Dupont"}],
            "container-title": ["Revue de test"],
            "issued": {"date-parts": [[2021]]},
            "is-referenced-by-count": 12, "type": "journal-article",
            "abstract": "<jats:p>Résumé de test.</jats:p>", "URL": "https://doi.org/10.1234/test.1",
        }]}}).encode()
        client = Client(transport=TransportFactice({"api.crossref.org": fixture}), cache=False)
        travaux = crossref.rechercher(client, "test")
        self.assertEqual(len(travaux), 1)
        self.assertEqual(travaux[0].auteurs, ["Marie Dupont"])
        self.assertEqual(travaux[0].annee, 2021)
        self.assertEqual(travaux[0].resume, "Résumé de test.")

    def test_openalex_fixture(self):
        fixture = json.dumps({"results": [{
            "id": "https://openalex.org/W123", "title": "OpenAlex test",
            "doi": "https://doi.org/10.1234/oa.1", "publication_year": 2020,
            "authorships": [{"author": {"display_name": "A. Auteur"}}],
            "primary_location": {"source": {"display_name": "Journal X"}},
            "cited_by_count": 5,
            "open_access": {"is_oa": True, "oa_url": "https://example.org/x.pdf"},
            "abstract_inverted_index": {"Bonjour": [0], "monde": [1]},
            "concepts": [{"display_name": "Science"}],
        }]}).encode()
        client = Client(transport=TransportFactice({"api.openalex.org": fixture}), cache=False)
        travaux = openalex.rechercher(client, "test")
        self.assertEqual(travaux[0].resume, "Bonjour monde")
        self.assertTrue(travaux[0].est_oa)

    def test_europepmc_fixture(self):
        fixture = json.dumps({"resultList": {"result": [{
            "id": "123", "source": "MED", "title": "Europe PMC test", "doi": "10.1/epmc",
            "pubYear": "2019", "authorString": "Dupont M, Martin C.",
            "journalTitle": "BMJ", "abstractText": "Résumé.", "citedByCount": 7,
            "isOpenAccess": "Y",
        }]}}).encode()
        client = Client(transport=TransportFactice({"ebi.ac.uk": fixture}), cache=False)
        travaux = europepmc.rechercher(client, "test")
        self.assertEqual(travaux[0].auteurs, ["Dupont M", "Martin C"])
        self.assertTrue(travaux[0].est_oa)


class TestDedup(unittest.TestCase):
    def test_fusion(self):
        a = Travail(titre="Essai A", doi="10.1/x", source="openalex", citations=3)
        b = Travail(titre="Essai A", doi="10.1/X", source="crossref", citations=9,
                    resume="Résumé", annee=2020)
        uniques, n = dedupliquer([a, b])
        self.assertEqual(len(uniques), 1)
        self.assertEqual(n, 1)
        self.assertEqual(uniques[0].citations, 9)
        self.assertEqual(uniques[0].resume, "Résumé")
        self.assertEqual(uniques[0].sources_multiples, ["crossref", "openalex"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
