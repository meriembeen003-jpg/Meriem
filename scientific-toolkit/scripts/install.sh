#!/usr/bin/env bash
# Installation du kit : vérifications, tests, dépendances optionnelles.
set -uo pipefail
cd "$(dirname "$0")/.."
VERT=$'\033[32m'; JAUNE=$'\033[33m'; ROUGE=$'\033[31m'; RAZ=$'\033[0m'

echo "== 1. Python =="
python3 --version || { echo "${ROUGE}Python 3.10+ requis${RAZ}"; exit 1; }
python3 - <<'PY' || exit 1
import sys
sys.exit(0 if sys.version_info >= (3, 10) else 1)
PY

echo "== 2. Tests du moteur d'audit (aucune dépendance) =="
python3 -m unittest discover -s tests || {
  echo "${ROUGE}Les tests échouent : corriger avant de continuer.${RAZ}"; exit 1; }

echo "== 3. Dépendances optionnelles =="
if python3 -m pip install -q -r requirements.txt; then
  echo "${VERT}dépendances installées${RAZ}"
else
  echo "${JAUNE}installation partielle (réseau ou compilation indisponible) :"
  echo "l'audit, le catalogue et le pipeline PRISMA fonctionnent sans ces paquets.${RAZ}"
fi

echo "== 4. Catalogue =="
python3 -m scitk catalogue --limite 8

echo
echo "${VERT}Prêt.${RAZ} Essayer :"
echo "  python3 -m scitk audit data/article_exemple.txt --out demos/out/audit_article"
echo "  python3 -m scitk review data/corpus_exemple.csv --inclusion 'lecture|reading' --sortie demos/out/revue"
echo "  bash demos/run_all.sh"
