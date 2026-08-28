#!/bin/bash
# Rutina diaria: refresca el calendario y, si Boca juega hoy, manda el mail.
cd "$(dirname "$0")" || exit 1
{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
  /usr/bin/python3 traer_partidos.py
  /usr/bin/python3 avisar.py
} >> registro.log 2>&1
