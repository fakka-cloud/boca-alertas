#!/bin/bash
# Respaldo local: si GitHub ya avisó hoy, esto no manda nada duplicado.
cd "$(dirname "$0")" || exit 1
{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
  # Traer lo que haya hecho GitHub (incluido avisados.json) para no repetir el mail.
  git pull --rebase --quiet
  /usr/bin/python3 traer_partidos.py
  /usr/bin/python3 traer_plantel.py
  /usr/bin/python3 avisar.py
  git add docs/partidos.json docs/plantel.json avisados.json
  git diff --staged --quiet || { git commit -m "partidos al $(date '+%d/%m')"; git push origin main; }
} >> registro.log 2>&1
