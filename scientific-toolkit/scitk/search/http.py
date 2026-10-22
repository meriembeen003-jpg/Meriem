# -*- coding: utf-8 -*-
"""Client HTTP minimal, poli et testable (urllib, bibliothèque standard).

• cache disque (évite de marteler les API et permet le hors-ligne) ;
• respect des quotas : temporisation, en-têtes User-Agent identifiables ;
• transport injectable : les tests utilisent `TransportFactice` pour fonctionner
  sans réseau (le sandbox d'exécution n'a pas accès aux API scientifiques).
"""
from __future__ import annotations
import hashlib
import json
import os
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request


class ErreurReseau(RuntimeError):
    """Réseau indisponible ou API en erreur."""


class Transport:
    def get(self, url: str, params: dict | None = None, headers: dict | None = None) -> bytes:
        q = ("?" + urllib.parse.urlencode(params, doseq=True)) if params else ""
        req = urllib.request.Request(url + q, headers={
            "User-Agent": "scitk/1.0 (audit scientifique; mailto:audit@example.org)",
            "Accept": "application/json, application/atom+xml, text/xml;q=0.9, */*;q=0.8",
            **(headers or {}),
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            raise ErreurReseau(f"HTTP {e.code} sur {url}") from e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            motif = getattr(e, "reason", e)
            raise ErreurReseau(f"réseau indisponible pour {url} ({motif})") from e


class TransportFactice(Transport):
    """Transport de test : renvoie des réponses enregistrées (fixtures)."""

    def __init__(self, reponses: dict[str, bytes] | None = None, defaut: bytes = b"{}"):
        self.reponses = reponses or {}
        self.defaut = defaut
        self.appels: list[tuple[str, dict]] = []

    def get(self, url, params=None, headers=None):
        self.appels.append((url, params or {}))
        for motif, contenu in self.reponses.items():
            if motif in url:
                return contenu
        return self.defaut


def cache_dir() -> pathlib.Path:
    d = pathlib.Path(os.environ.get("SCITK_CACHE", pathlib.Path.home() / ".cache" / "scitk"))
    d.mkdir(parents=True, exist_ok=True)
    return d


class Client:
    """Accès HTTP avec cache et temporisation par hôte."""

    def __init__(self, transport: Transport | None = None, cache: bool = True,
                 ttl: int = 60 * 60 * 24, delai: float = 0.15):
        self.transport = transport or Transport()
        self.cache = cache
        self.ttl = ttl
        self.delai = delai
        self._dernier: dict[str, float] = {}
        self.stats = {"requetes": 0, "cache": 0, "erreurs": 0}

    def _cle(self, url: str, params: dict) -> pathlib.Path:
        h = hashlib.sha256((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()[:32]
        return cache_dir() / f"{h}.json"

    def get_json(self, url: str, params: dict | None = None,
                 headers: dict | None = None, forcer: bool = False) -> dict:
        params = params or {}
        chemin = self._cle(url, params)
        if self.cache and not forcer and chemin.exists():
            age = time.time() - chemin.stat().st_mtime
            if age < self.ttl:
                self.stats["cache"] += 1
                return json.loads(chemin.read_text(encoding="utf-8"))
        hote = urllib.parse.urlparse(url).netloc
        dernier = self._dernier.get(hote)
        if dernier and self.delai:
            reste = self.delai - (time.time() - dernier)
            if reste > 0:
                time.sleep(reste)
        try:
            brut = self.transport.get(url, params, headers)
        except ErreurReseau:
            self.stats["erreurs"] += 1
            raise
        finally:
            self._dernier[hote] = time.time()
        self.stats["requetes"] += 1
        try:
            data = json.loads(brut.decode("utf-8", "replace"))
        except json.JSONDecodeError:
            # réponses XML (arXiv) : renvoyées encapsulées
            data = {"_xml": brut.decode("utf-8", "replace")}
        if self.cache:
            try:
                chemin.write_text(json.dumps(data), encoding="utf-8")
            except OSError:
                pass
        return data

    def get_texte(self, url: str, params: dict | None = None,
                  headers: dict | None = None) -> str:
        brut = self.transport.get(url, params, headers)
        self.stats["requetes"] += 1
        return brut.decode("utf-8", "replace")
