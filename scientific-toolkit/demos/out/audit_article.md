# Rapport d'audit scientifique

*Généré le 2026-10-22T18:30:51+00:00 par `scitk` — audit reproductible, hors ligne.*

**Score global : 32/100** · Gravité : **CRITIQUE**

## 1. Synthèse

| Indicateur | Valeur |
|---|---|
| Résultats statistiques extraits | 10 |
| Résultats significatifs (p < .05) | 7 |
| Incohérences statistique ↔ p (majeures) | 1 |
| Écarts d'arrondi stricts | 4 |
| Erreurs de décision | 2 |
| Taux d'incohérence | 10.0% |
| Score de cohérence statistique | 76/100 |
| Score de transparence | 59/100 |

## 2. Constats (par gravité)

| Gravité | Code | Source | Message |
|---|---|---|---|
| 🔴 CRITIQUE | `claim_contredit` | t — t(28) | Le texte qualifie le résultat de significatif, mais p recalculée = 0.0749. |
| 🔴 CRITIQUE | `claim_contredit` | t — t(38) | Le texte qualifie le résultat de significatif, mais p recalculée = 0.0550. |
| 🔴 CRITIQUE | `erreur_decision` | t — t(28) | La décision change : p rapportée = 0.0420 mais p recalculée = 0.0749 (seuil 0.05). |
| 🔴 CRITIQUE | `grim_impossible` | descriptif Groupe contrôle — score lecture | M = 3.11 est impossible avec n = 60 et 1 item(s) entier(s) (la somme devrait être 186.600, donc un multiple de 1) ; la moyenne réalisable la plus proche est 3.1 |
| 🔴 CRITIQUE | `grim_impossible` | descriptif Sous-groupe A — satisfaction | M = 4.37 est impossible avec n = 25 et 1 item(s) entier(s) (la somme devrait être 109.250, donc un multiple de 1) ; la moyenne réalisable la plus proche est 4.36 |
| 🔴 CRITIQUE | `grim_impossible` | descriptif Sous-groupe B — satisfaction | M = 5.19 est impossible avec n = 18 et 1 item(s) entier(s) (la somme devrait être 93.420, donc un multiple de 1) ; la moyenne réalisable la plus proche est 5.17 |
| 🔴 CRITIQUE | `grimmer_impossible` | descriptif Groupe programme — score lecture | (M = 3.77, SD = 0.31) est impossible avec n = 60 entiers : aucune somme de carrés compatible. |
| 🔴 CRITIQUE | `grimmer_impossible` | descriptif Échantillon total — motivation | (M = 4.9, SD = 0.05) est impossible avec n = 40 entiers : aucune somme de carrés compatible. |
| 🔴 CRITIQUE | `retractee` | bibliographie — wakefield1998 | Référence rétractée : Ileal-lymphoid-nodular hyperplasia non-specific colitis and pervasive developmental disorder in children (1998) — Retraction Watch (cas emblématique) |
| 🔴 CRITIQUE | `sprite_impossible` | descriptif Groupe programme — score lecture | SD = 0.31 est hors des bornes atteignables [0.427 ; 1.845] pour n = 60 entiers dans [1, 5] avec M = 3.77. |
| 🔴 CRITIQUE | `sprite_impossible` | descriptif Échantillon total — motivation | SD = 0.05 est hors des bornes atteignables [0.304 ; 0.632] pour n = 40 entiers dans [1, 5] avec M = 4.9. |
| 🟠 MAJEUR | `annee_aberrante` | bibliographie — futur | Année 2039 invraisemblable (bornes 1500–2027). |
| 🟠 MAJEUR | `doi_invalide` | bibliographie — doimalforme | DOI mal formé : doi-invalide-2019 |
| 🟠 MAJEUR | `doublon_doi` | bibliographie — 10.1000/rpe.2021.015 | DOI présent 2 fois dans la bibliographie. |
| 🟠 MAJEUR | `doublon_titre` | bibliographie — dupont2021 ≈ dupont2021bis | Titres quasi identiques (100%) : doublon probable ou preprint + version publiée. |
| 🟠 MAJEUR | `incoherence` | t — t(28) | p recalculée = 0.0749 (intervalle 0.0742–0.0756) incompatible avec p rapportée = 0.0420. |
| 🟡 MINEUR | `doi_absent` | bibliographie — futur | Pas de DOI : vérification d'existence et de rétractation impossible. |
| 🟡 MINEUR | `doi_absent` | bibliographie — sansdoi | Pas de DOI : vérification d'existence et de rétractation impossible. |
| 🟡 MINEUR | `incoherence` | F — F(2, 45) | Écart faible mais réel : p recalculée = 0.0498 (intervalle 0.0495–0.0500) vs p rapportée = 0.0490. |
| 🟡 MINEUR | `incoherence` | t — t(138) | Écart faible mais réel : p recalculée = 0.0173 (intervalle 0.0170–0.0175) vs p rapportée = 0.0190. |
| 🟡 MINEUR | `incoherence` | t — t(38) | Écart faible mais réel : p recalculée = 0.0380 (intervalle 0.0376–0.0384) vs p rapportée = 0.0340. |
| 🟡 MINEUR | `incoherence` | r — r(28) | Écart faible mais réel : p recalculée = 0.0244 (intervalle 0.0226–0.0264) vs p rapportée = 0.0210. |
| 🟡 MINEUR | `p_zero` | texte | p = .000 apparaît dans le texte (impossible). |

## 3. Recalcul des résultats

| Type | Test | p rapportée | p recalculée | Écart | Constats |
|---|---|---|---|---|---|
| F | `F(2, 45) = 3.21` | 0.0490 | 0.0498 | 0.0008 | `incoherence` |
| F | `F(3, 96) = 4.02` | 0.0100 | 0.0097 | 0.0003 | — |
| chi2 | `chi2(1) = 4.5` | 0.0340 | 0.0339 | 0.0001 | — |
| t | `t(138) = 2.41` | 0.0190 | 0.0173 | 0.0017 | `incoherence` |
| t | `t(28) = 1.85` | 0.0420 | 0.0749 | 0.0329 | `erreur_decision`, `incoherence`, `claim_contredit` |
| t | `t(38) = 2.15` | 0.0340 | 0.0380 | 0.0040 | `incoherence` |
| t | `t(38) = 1.98` | 0.0550 | 0.0550 | 0.0000 | `claim_contredit` |
| t | `t(58) = 2.41` | 0.0190 | 0.0191 | 0.0001 | — |
| r | `r(28) = 0.41` | 0.0210 | 0.0244 | 0.0034 | `incoherence` |
| r | `r(45) = 0.12` | 0.4220 | 0.4217 | 0.0003 | — |

## 4. Transparence

| Indicateur | Présence | Qualité |
|---|---|---|
| Disponibilité des données | ✅ | fort |
| Disponibilité du code / des analyses | ❌ | absent |
| Préenregistrement / rapport enregistré | ✅ | fort |
| Financement déclaré | ❌ | absent |
| Conflits d'intérêts | ✅ | fort |
| Approbation éthique / consentement | ❌ | absent |
| Justification de la taille d'échantillon | ❌ | absent |
| Protocole disponible | ✅ | fort |
| Limites discutées | ✅ | fort |
| Matériel supplémentaire | ✅ | fort |

**Éléments absents :** Disponibilité du code / des analyses, Financement déclaré, Approbation éthique / consentement, Justification de la taille d'échantillon

## 5. Distribution des p-values

- p-curve : 50% des p < .05 sont < .025 (test binomial p = 0.636719) → distribution plate ou en hausse près de .05 : compatible avec une sélection de résultats / un fichier tiroir — n faible, résultat indicatif
- Excès de significativité : 8/10 observés vs 5.0 attendus (z = 1.897, p = 0.05778)
- Variance des p : 0.01546 (attendu ≈ 0.0833), p = 0.004319

## 6. Tests GRIM / GRIMMER

| Descriptif | n | M | SD | Résultat |
|---|---|---|---|---|
| Groupe programme — score lecture | 60 | 3.77 | 0.31 | ✅ |
| Groupe contrôle — score lecture | 60 | 3.11 | 0.44 | ❌ impossible |
| Sous-groupe A — satisfaction | 25 | 4.37 | 0.42 | ❌ impossible |
| Sous-groupe B — satisfaction | 18 | 5.19 | 0.28 | ❌ impossible |
| Échantillon total — motivation | 40 | 4.9 | 0.05 | ✅ |

## 7. Bibliographie

- Références analysées : **8**
- Constats : **7**
- Sans DOI : **2** (25%)
- Doublons détectés : **2**
- Références rétractées : **1**

| DOI | Titre | Motif |
|---|---|---|
| 10.1016/s0140-6736(97)11096-0 | Ileal-lymphoid-nodular hyperplasia non-specific colitis and pervasive developmental disorder in children | Fabrication/Falsification des données ; conflits d'intérêts non déclarés |

---

### Portée et limites

Cet audit est **automatique et non décisionnel** : il signale des divergences arithmétiques et des déclarations manquantes, pas une fraude. Chaque constat doit être vérifié sur le manuscrit, les données et le code. Les erreurs de recalcul peuvent venir de la mise en forme (arrondis, tests unilatéraux, corrections).

Tests appliqués : recalcul APA (t, F, χ², r, z), GRIM/GRIMMER/SPRITE, p-curve, excès de significativité, variance insuffisante, distribution des décimales, Benford, doublons de texte, indicateurs de transparence, rétractations.