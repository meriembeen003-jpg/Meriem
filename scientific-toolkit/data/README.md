# Jeux de données de démonstration

| Fichier | Contenu | Particularité |
|---|---|---|
| `article_exemple.txt` | article **fictif** de psychologie de l'éducation | contient des erreurs **volontairement** plantées : erreurs de décision, GRIM impossibles, `p = .000`, phrase concessive, échelle Likert 1–5 |
| `descriptifs_exemple.json` | 5 lignes de tableau (n, M, SD) | 3 échecs GRIM, 1 échec GRIMMER/SPRITE |
| `references_exemple.bib` | 8 références | doublon de DOI, DOI mal formé, année 2039, référence rétractée (Wakefield 1998), article historique (Einstein 1905) |
| `corpus_exemple.csv` | 12 notices issues de 3 sources simulées | doublons inter-sources, article « animal » à exclure, notices sans DOI |
| `corpus_textes.json` | 4 abstracts | A et B identiques, C fortement similaire (motif « paper mill »), D hors sujet |
| `retractions.csv` | 8 rétractations **réelles et documentées** | échantillon pédagogique ; importer la Retraction Watch DB pour un usage réel |

L'article et le corpus sont entièrement fictifs. Les rétractations sont réelles :
elles servent à tester la chaîne de vérification, pas à mettre en cause qui que
ce soit au-delà de ce qui est publiquement documenté.
