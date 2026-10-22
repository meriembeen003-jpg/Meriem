# Protocoles d'audit prêts à l'emploi

Six scénarios concrets, de l'article isolé à l'échelle d'une revue. Chaque
protocole indique les commandes, ce qu'on peut conclure, et ce qu'on ne peut **pas**
conclure.

---

## Protocole 1 — Auditer un article reçu en relecture (20 minutes)

**Objectif** : vérifier la cohérence arithmétique et la transparence avant de rendre
un avis.

```bash
# 1. extraire le texte du PDF (si nécessaire)
pdftotext -layout article.pdf article.txt          # ou :
python3 -c "import fitz;print(chr(10).join(p.get_text() for p in fitz.open('article.pdf')))" > article.txt

# 2. audit complet
python3 -m scitk audit article.txt --out audit/article --json > audit/article.json

# 3. transparence seule
python3 -m scitk transparence article.txt
```

**Lecture des résultats**

| Signal | Interprétation prudente | Action |
|---|---|---|
| `erreur_decision` | la p-value rapportée contredit la statistique | demander les sorties brutes |
| `incoherence` répétée (> 10 % des résultats) | erreurs de recalcul systématiques | demander le script d'analyse |
| `claim_contredit` | texte et chiffres ne disent pas la même chose | signaler précisément la phrase |
| `p_zero` | `p = .000` | correction de rédaction (non substantielle) |
| GRIM impossible | moyenne incompatible avec n et une échelle entière | demander les données |
| transparence < 40 | aucune déclaration de données/code | conditionner l'acceptation |

**Ne pas conclure** : une incohérence n'est pas une fraude. Arrondis, tests
unilatéraux, modèles mixtes, corrections de continuité, p-values issues de
bootstraps produisent des écarts légitimes.

---

## Protocole 2 — Audit d'un tableau de résultats (GRIM/GRIMMER/SPRITE)

**Objectif** : vérifier que les moyennes et écarts-types d'un tableau sont
arithmétiquement possibles.

```bash
# test isolé
python3 -m scitk grim --mean 3.77 --sd 0.31 --n 60 --lo 1 --hi 5

# bornes exactes de l'écart-type
python3 -m scitk sprite --mean 4.90 --sd 0.05 --n 40 --lo 1 --hi 5
```

En lot, via JSON :

```json
[
  {"label": "Groupe A", "n": 60, "mean": 3.77, "sd": 1.02},
  {"label": "Sous-groupe B", "n": 18, "mean": 5.19, "sd": 0.28}
]
```

```bash
python3 -m scitk audit article.txt --descriptifs tableau.json --out audit/tableau
```

**Conditions d'application** : données **entières** (Likert, score total, comptage),
bornes connues (`--lo`, `--hi`), `n` exact. Sur des mesures continues, ces tests
ne s'appliquent pas.

---

## Protocole 3 — Vérifier une bibliographie et les rétractations

```bash
# audit d'un fichier BibTeX / RIS / liste de DOIs
python3 -m scitk biblio references.bib --auteur "Dupont" --json > biblio.json

# rétractations dans un texte (repère les DOI cités)
python3 -m scitk retractions --texte manuscrit.txt

# base complète (60 000 rétractations) : télécharger l'export Retraction Watch
python3 - <<'EOF'
from scitk.audit import retractions
print(retractions.importer_base_retraction_watch("retraction_watch.csv"))
EOF

# puis relancer l'audit avec la base complète
python3 -m scitk biblio references.bib --base-retractations retraction_watch.csv
```

**Contrôles automatiques** : DOI mal formé, DOI dupliqué, année aberrante, titre
quasi identique (preprint + version publiée), absence de DOI, auto-citations
excessives, référence rétractée.

**Ce que l'outil ne fait pas** : vérifier que la référence *existe* (il faut
Crossref/OpenAlex en ligne) ni que le contenu cité correspond à l'article cité
(« citation mismatch » — travail humain, aidé par SciScore/Scite).

---

## Protocole 4 — Détecter un « paper mill » dans un lot de soumissions

```bash
# similarité de textes (abstracts)
python3 -m scitk similarite abstracts.json --seuil 0.45
```

```json
[
  {"id": "S001", "texte": "Randomized controlled trial of …"},
  {"id": "S002", "texte": "Randomized controlled trial of …"}
]
```

**Signaux croisés à examiner**

- similarité > 0.5 entre abstracts d'auteurs différents ;
- GRIM/GRIMMER impossibles en série ;
- décimales anormalement uniformes ou, au contraire, excès de 0/5 ;
- figures dupliquées (hors périmètre de ce kit : voir `imagehash`, `Proofig`, `ImageTwin`) ;
- métadonnées incohérentes (affiliations fantaisistes, ORCID absents, revues
  absentes de DOAJ) ;
- phrases « torturées » (traductions automatiques de tournures courantes).

**Prudence** : la similarité de textes entre deux articles est fréquente et légitime
dans une même équipe ou pour des versions successives. Toujours vérifier les auteurs,
les affiliations et les dates avant de conclure.

---

## Protocole 5 — Audit d'une revue ou d'un auteur (analyse de corpus)

**Objectif** : passer d'erreurs individuelles à un profil statistique.

```python
from scitk.audit import apa
from pathlib import Path

audits = [apa.audit_texte(p.read_text()) for p in Path("articles/").glob("*.txt")]
print(apa.comparer_litterature(audits))
# {'articles': 42, 'resultats': 611, 'taux_incoherence': 0.031,
#  'erreurs_decision': 3, 'part_significatifs': 0.86, 'score_moyen': 71.2}
```

Puis, sur l'ensemble des p-values extraites :

- **p-curve** : une distribution plate près de .05 signale une sélection ;
- **excès de significativité** : compare le nombre de résultats significatifs
  à ce que la puissance déclarée permettrait ;
- **variance insuffisante** : `Var(p)` très inférieure à 1/12 = p-values
  possiblement fabriquées.

**Ce qu'on peut conclure** : « la distribution des résultats de ce corpus est
statistiquement incompatible avec l'hypothèse de tests non sélectionnés ».
**Ce qu'on ne peut pas conclure** : « cet auteur a fabriqué ses données ».
La sélection de résultats peut venir des auteurs, des relecteurs, de la revue
(biais de publication), ou de la discipline.

---

## Protocole 6 — Revue systématique reproductible

```bash
# 1. corpus local (export Scopus/WoS/PubMed consolidé)
python3 -m scitk review corpus.csv \
    --nom "Remédiation en lecture" \
    --question "Quelle est l'efficacité des programmes de remédiation en lecture au primaire ?" \
    --inclusion "reading|lecture" \
    --exclusion "rodent|animal|adult" \
    --annee-min 2000 --exiger-resume \
    --sortie revue/lecture
```

```bash
# 2. ou recherche en ligne (machine connectée)
python3 -m scitk search "reading remediation randomized trial" \
    --sources openalex,crossref,europepmc,semanticscholar \
    --limite 100 --annee-min 2000 --json > revue/brut.json
python3 -m scitk review revue/brut.json --inclusion "reading|lecture" --sortie revue/lecture
```

**Sorties** : `*_prisma.json` (chiffres), `*_prisma.txt` (diagramme de flux),
`*_journal.json` (chaque décision avec sa règle), `*.csv/.ris/.bib` (corpus final),
`*_rapport.md` (rapport complet).

**Exigence PRISMA** : les critères doivent être **écrits avant** le criblage.
Le journal produit ici est un audit trail : il montre quelles règles ont été
appliquées, dans quel ordre, et combien d'études chaque règle a éliminées.

**Limite** : le criblage automatique est un *pré-filtre*. Une revue publiable
exige une double lecture humaine et un calcul de l'accord inter-juges (κ).

---

## Check-list de relecture (à joindre à un avis)

- [ ] Les statistiques rapportées sont-elles recalculables (ddl et p fournis) ?
- [ ] Les conclusions suivent-elles les seuils annoncés, y compris pour les
      résultats secondaires ?
- [ ] Les tailles d'effet et intervalles de confiance sont-ils rapportés ?
- [ ] Les analyses multiples sont-elles corrigées ou préenregistrées ?
- [ ] Les données et le code sont-ils disponibles, ou leur absence est-elle justifiée ?
- [ ] Les références citées existent-elles et correspondent-elles au propos ?
- [ ] Aucune référence rétractée n'est-elle citée sans mention ?
- [ ] Les tests GRIM/GRIMMER sont-ils applicables et, le cas échéant, passés ?
- [ ] Les limites déclarées correspondent-elles aux faiblesses réelles ?
