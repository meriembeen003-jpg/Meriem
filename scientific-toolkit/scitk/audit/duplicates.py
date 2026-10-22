# -*- coding: utf-8 -*-
"""Détection de réutilisation de texte et de doublons de publications.

Utile pour :
  • le dédoublonnage d'une revue systématique (MESHP, DOIs multiples) ;
  • la détection de « paper mills » (abstracts quasi identiques, phrases
    torturées, titres permutés) ;
  • le repérage d'auto-plagiat entre deux versions d'un manuscrit.

Méthode : normalisation → suppression des mots vides → shingles de k mots →
Jaccard exact (petits corpus) ou MinHash (gros corpus).
"""
from __future__ import annotations
import hashlib
import math
import random
import re
import unicodedata
from collections import defaultdict

STOPWORDS = set("""
a au aux avec ce ces cet cette dans de des du elle en et eux il ils je la le les leur
lui ma mais me meme mes moi mon ne nos notre nous on ou par pas pour qu que qui sa se ses
son sur ta te tes toi ton tu un une vos votre vous c d j l a m n s t y ete etee etes etant
etre ayant avoir and or the of to in for on with by from as at is are was were be been
this that these those we our they their it its an into than then there here which who whom
""".split())


def normaliser_texte(texte: str) -> str:
    t = unicodedata.normalize("NFKD", texte.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def mots_utiles(texte: str) -> list[str]:
    return [m for m in normaliser_texte(texte).split() if m not in STOPWORDS and len(m) > 2]


def shingles(texte: str, k: int = 5) -> set[str]:
    mots = mots_utiles(texte) if " " in texte else normaliser_texte(texte).split()
    if len(mots) < k:
        return {" ".join(mots)} if mots else set()
    return {" ".join(mots[i:i + k]) for i in range(len(mots) - k + 1)}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _hash32(s: str, graine: int) -> int:
    return int(hashlib.blake2b((str(graine) + s).encode(), digest_size=4).hexdigest(), 16)


def minhash(ens: set[str], n_perm: int = 64) -> list[int]:
    if not ens:
        return [2 ** 32] * n_perm
    return [min(_hash32(s, i) for s in ens) for i in range(n_perm)]


def similarite_minhash(sig_a: list[int], sig_b: list[int]) -> float:
    return sum(1 for x, y in zip(sig_a, sig_b) if x == y) / len(sig_a)


def doublons_corpus(documents: dict[str, str], seuil: float = 0.5,
                    k: int = 5, minhash_si: int = 400) -> dict:
    """documents = {identifiant: texte}. Retourne les paires suspectes."""
    ids = list(documents)
    if len(ids) > minhash_si:                     # gros corpus : MinHash
        sigs = {i: minhash(shingles(documents[i], k)) for i in ids}
        paires = []
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                s = similarite_minhash(sigs[ids[a]], sigs[ids[b]])
                if s >= seuil:
                    paires.append({"a": ids[a], "b": ids[b], "similarite": round(s, 4), "methode": "MinHash"})
    else:                                         # petit corpus : Jaccard exact
        sh = {i: shingles(documents[i], k) for i in ids}
        paires = []
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                s = jaccard(sh[ids[a]], sh[ids[b]])
                if s >= seuil:
                    paires.append({"a": ids[a], "b": ids[b], "similarite": round(s, 4), "methode": "Jaccard"})
    paires.sort(key=lambda d: -d["similarite"])
    return {
        "documents": len(ids),
        "seuil": seuil,
        "k_shingles": k,
        "paires_suspectes": paires,
        "nb_paires": len(paires),
        "interpretation": ("aucun doublon au seuil demandé" if not paires else
                           f"{len(paires)} paire(s) de documents très proches : "
                           "vérifier l'originalité et les DOIs"),
    }


def phrases_identiques(texte_a: str, texte_b: str, longueur_min: int = 8) -> list[str]:
    """Phrases (ou fragments de n mots) partagés exactement entre deux textes."""
    def frags(t):
        mots = normaliser_texte(t).split()
        return {" ".join(mots[i:i + longueur_min]) for i in range(max(0, len(mots) - longueur_min + 1))}
    return sorted(frags(texte_a) & frags(texte_b))[:50]


def matrice_similarite(documents: dict[str, str], k: int = 5) -> dict:
    """Matrice complète (petits corpus) pour cartographier les proximités."""
    ids = list(documents)
    sh = {i: shingles(documents[i], k) for i in ids}
    return {a: {b: round(jaccard(sh[a], sh[b]), 3) for b in ids} for a in ids}


def titres_proches(titres: dict[str, str], seuil: float = 0.85) -> list[dict]:
    """Comparaison de titres (dédoublonnage de revue systématique)."""
    prep = {i: " ".join(mots_utiles(t)) for i, t in titres.items()}
    out = []
    ids = list(prep)
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            sa, sb = set(prep[ids[a]].split()), set(prep[ids[b]].split())
            j = jaccard(sa, sb)
            if j >= seuil:
                out.append({"a": ids[a], "b": ids[b], "similarite": round(j, 3),
                            "titre_a": titres[ids[a]], "titre_b": titres[ids[b]]})
    return sorted(out, key=lambda d: -d["similarite"])
