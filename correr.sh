#!/bin/bash
# Rutina diaria: refresca el calendario, sube el json a GitHub y, si Boca juega hoy, manda el mail.
cd "$(dirname "$0")" || exit 1
{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
  /usr/bin/python3 traer_partidos.py
  # La web app lee partidos.json desde GitHub Pages: hay que subirlo.
  if ! git diff --quiet docs/partidos.json; then
    git add docs/partidos.json
    git commit -m "partidos al $(date '+%d/%m')"
    git push origin main
  fi
  /usr/bin/python3 avisar.py
} >> registro.log 2>&1
