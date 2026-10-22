# Droit, éthique, données

## 1. Accès au texte intégral

| Voie | Statut | Outils |
|---|---|---|
| Accès ouvert (gold, green, hybrid, bronze) | légal, encouragé | `unpywall`, `pyalex`, Europe PMC, HAL, Zenodo, dépôts institutionnels |
| Prêt entre bibliothèques, accès institutionnel | légal selon contrat | portails éditeurs, EZproxy |
| Demande directe à l'auteur, preprint | légal | arXiv, bioRxiv, OSF Preprints, ResearchGate (dépôt par l'auteur) |
| **Sci-Hub, LibGen, Z-Library** | **contrefaçon dans la plupart des juridictions** | `PyPaperBot`, `SciDownl`, `libgen-mcp` |

Les outils de contournement sont **archivés à titre documentaire** parce qu'ils
figurent parmi les dépôts les plus utilisés de l'écosystème ; ce kit ne les
exécute pas et privilégie systématiquement la voie légale. Utiliser Sci-Hub
peut exposer à des poursuites, faire bloquer l'accès réseau d'une institution
et compromettre la publication qui en dépend.

## 2. Licences des outils archivés

Les 74 dépôts conservent **leur licence d'origine** (fichier `LICENSE` dans chaque
dossier) : MIT, Apache-2.0, BSD, GPL-2.0/3.0, AGPL-3.0, CC-BY, ou « non précisée ».

- **MIT / Apache / BSD** : réutilisation libre, attribution.
- **GPL / AGPL** : un logiciel dérivé distribué doit rester sous la même licence.
  L'AGPL s'applique aussi à un service réseau : ne pas exposer publiquement un
  service bâti sur du code AGPL sans en publier les sources.
- **« NOASSERTION » / sans licence** : pas de droit d'usage explicite — lire le
  code est permis, le réutiliser ne l'est pas sans autorisation de l'auteur.

`catalog/outils.csv` donne la licence SPDX de chaque dépôt : à vérifier **avant**
toute intégration dans un produit.

## 3. Données personnelles (RGPD)

Un audit scientifique manipule des données sur des personnes : auteurs, éditeurs,
membres de comités. Trois règles :

1. **Minimisation** : ne collecter que ce qui est nécessaire à la vérification.
2. **Base légale** : intérêt légitime pour l'intégrité scientifique, mais
   proportionnalité obligatoire (pas de profilage systématique d'auteurs).
3. **Droit de réponse** : tout constat doit pouvoir être contesté. Un rapport
   interne ne se diffuse pas publiquement sans vérification contradictoire.

Les journaux produits par `scitk` sont locaux ; aucun envoi automatique.

## 4. Déontologie de l'auditeur

- Distinguer **erreur**, **négligence** et **fraude** : seule la dernière suppose
  une intention, et elle ne se déduit jamais d'un calcul.
- Signaler d'abord à l'auteur ou à l'éditeur (COPE : *flowcharts* sur la
  suspicion de mauvaise conduite).
- Conserver les preuves : texte source, version du logiciel, date, paramètres.
  `scitk` horodate chaque rapport et fige les paramètres dans le JSON.
- Ne pas utiliser un score automatique comme verdict. Un score de 27/100 dit
  « ce manuscrit contient des incohérences vérifiables », pas « ce manuscrit
  est frauduleux ».
