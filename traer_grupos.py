#!/usr/bin/env python3
"""Baja la fase de grupos y/o la instancia de playoffs de los torneos de copa que juega Boca.
Guarda docs/grupos.json."""

import json
import urllib.error
import urllib.request
from pathlib import Path

CASA = Path(__file__).resolve().parent
SALIDA = CASA / "docs" / "grupos.json"

BOCA = "5"
TEMPORADA = 2026
AGENTE = "curl/8.7.1"  # ESPN rechaza casi cualquier otro user-agent

# torneos de copa (la liga ya tiene su propia tabla de zona en traer_plantel.py)
COPAS = {
    "arg.copa":               "Copa Argentina",
    "arg.supercopa":          "Supercopa Argentina",
    "arg.trofeo_campeones":   "Trofeo de Campeones",
    "conmebol.libertadores":  "Copa Libertadores",
    "conmebol.sudamericana":  "Copa Sudamericana",
    "conmebol.recopa":        "Recopa Sudamericana",
    "fifa.cwc":               "Mundial de Clubes",
}


def bajar(url):
    pedido = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(pedido, timeout=25) as r:
        return json.loads(r.read().decode())


def intentar(url):
    try:
        return bajar(url)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError):
        return None


def grupo_de_boca(codigo):
    """Si el torneo tiene fase de grupos y Boca juega en uno, devuelve su tabla."""
    datos = intentar(f"https://site.web.api.espn.com/apis/v2/sports/soccer/{codigo}/standings?season={TEMPORADA}")
    if not datos:
        return None
    for grupo in datos.get("children", []):
        entradas = (grupo.get("standings") or {}).get("entries", [])
        if not any(e["team"]["id"] == BOCA for e in entradas):
            continue
        filas = []
        for e in entradas:
            stats = {s["name"]: s.get("displayValue", "") for s in e.get("stats", [])}
            filas.append({
                "equipo": e["team"]["displayName"],
                "es_boca": e["team"]["id"] == BOCA,
                "pj": stats.get("gamesPlayed", ""),
                "pg": stats.get("wins", ""),
                "pe": stats.get("ties", ""),
                "pp": stats.get("losses", ""),
                "gf": stats.get("pointsFor", ""),
                "gc": stats.get("pointsAgainst", ""),
                "dg": stats.get("pointDifferential", ""),
                "pts": stats.get("points", ""),
                "nota": (e.get("note") or {}).get("description", ""),
            })
        filas.sort(key=lambda f: int(f["pts"] or 0), reverse=True)
        nombre_grupo = grupo.get("name", "").replace("Group", "Grupo")
        return {"nombre_grupo": nombre_grupo, "filas": filas}
    return None


FASES = {
    "Round of 64": "Ronda de 64",
    "Round of 32": "Ronda de 32",
    "Round of 16": "Octavos de Final",
    "Quarterfinals": "Cuartos de Final",
    "Semifinals": "Semifinal",
    "Final": "Final",
    "Group Stage": "Fase de Grupos",
}


def fase_actual(codigo):
    """Si no hay grupos (o Boca ya no está en fase de grupos), devuelve la instancia actual del torneo."""
    datos = intentar(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{codigo}/scoreboard?season={TEMPORADA}")
    if not datos:
        return None
    ligas = datos.get("leagues") or []
    if not ligas:
        return None
    tipo = (ligas[0].get("season") or {}).get("type") or {}
    nombre = tipo.get("name", "")
    if not nombre:
        return None
    return FASES.get(nombre, nombre)


def boca_juega(codigo):
    """Chequea si Boca tiene partidos programados o jugados en este torneo esta temporada."""
    datos = intentar(
        f"https://site.api.espn.com/apis/site/v2/sports/soccer/{codigo}/teams/{BOCA}/schedule?season={TEMPORADA}"
    )
    if not datos:
        return False
    return bool(datos.get("events"))


def main():
    salida = []
    for codigo, nombre in COPAS.items():
        if not boca_juega(codigo):
            continue
        entrada = {"torneo": nombre}
        grupo = grupo_de_boca(codigo)
        if grupo:
            entrada["tipo"] = "grupo"
            entrada.update(grupo)
        else:
            fase = fase_actual(codigo)
            if not fase:
                continue
            entrada["tipo"] = "fase"
            entrada["fase"] = fase
        salida.append(entrada)

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps({"grupos": salida}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"guardado {SALIDA} con {len(salida)} torneo(s)")


if __name__ == "__main__":
    main()
