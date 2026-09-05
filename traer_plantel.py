#!/usr/bin/env python3
"""Baja el plantel, la tabla y el último equipo que puso Boca. Guarda docs/plantel.json."""

import json
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

CASA = Path(__file__).resolve().parent
SALIDA = CASA / "docs" / "plantel.json"

BOCA = "5"
LIGA = "arg.1"
AR = timezone(timedelta(hours=-3))
AGENTE = "curl/8.7.1"  # ESPN rechaza casi cualquier otro user-agent

PUESTOS = {
    "Goalkeeper": "Arqueros",
    "Defender": "Defensores",
    "Midfielder": "Mediocampistas",
    "Forward": "Delanteros",
}
ORDEN = ["Arqueros", "Defensores", "Mediocampistas", "Delanteros"]


def bajar(url):
    pedido = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(pedido, timeout=25) as r:
        return json.loads(r.read().decode())


def intentar(url):
    try:
        return bajar(url)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError):
        return None


def stat(jugador, categoria, nombre):
    est = jugador.get("statistics") or {}
    for c in est.get("splits", {}).get("categories", []):
        if c["name"] == categoria:
            for s in c["stats"]:
                if s["name"] == nombre:
                    return int(float(s.get("value") or 0))
    return 0


def plantel():
    datos = intentar(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{LIGA}/teams/{BOCA}/roster")
    if not datos:
        return []
    gente = []
    for a in datos.get("athletes", []):
        puesto = PUESTOS.get(a.get("position", {}).get("displayName"), "Otros")
        gente.append({
            "nombre": a.get("displayName", ""),
            "dorsal": a.get("jersey") or "",
            "puesto": puesto,
            "edad": a.get("age"),
            "pais": a.get("citizenship") or "",
            "pj": stat(a, "general", "appearances"),
            "goles": stat(a, "offensive", "totalGoals"),
            "asistencias": stat(a, "offensive", "goalAssists"),
            "amarillas": stat(a, "general", "yellowCards"),
            "rojas": stat(a, "general", "redCards"),
        })
    gente.sort(key=lambda j: (ORDEN.index(j["puesto"]) if j["puesto"] in ORDEN else 9,
                              int(j["dorsal"]) if j["dorsal"].isdigit() else 999,
                              j["nombre"]))
    return gente


def tabla():
    """Devuelve la zona donde está Boca, no las dos."""
    anio = datetime.now(AR).year
    datos = intentar(f"https://site.web.api.espn.com/apis/v2/sports/soccer/{LIGA}/standings?season={anio}")
    if not datos:
        return {"zona": "", "filas": []}
    for grupo in datos.get("children", []):
        entradas = grupo.get("standings", {}).get("entries", [])
        if not any(e["team"]["id"] == BOCA for e in entradas):
            continue
        filas = []
        for e in entradas:
            v = {s["name"]: s.get("displayValue", "") for s in e["stats"]}
            filas.append({
                "puesto": int(v.get("rank") or 0),
                "equipo": e["team"].get("shortDisplayName") or e["team"]["displayName"],
                "escudo": f"https://a.espncdn.com/i/teamlogos/soccer/500/{e['team']['id']}.png",
                "pj": v.get("gamesPlayed", ""),
                "dif": v.get("pointDifferential", ""),
                "pts": v.get("points", ""),
                "es_boca": e["team"]["id"] == BOCA,
            })
        filas.sort(key=lambda f: f["puesto"])
        nombre = grupo.get("name", "").replace("Group", "Zona")
        return {"zona": nombre, "filas": filas}
    return {"zona": "", "filas": []}


def ultimo_equipo():
    """Titulares y suplentes del último partido jugado."""
    agenda = intentar(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{LIGA}/teams/{BOCA}/schedule")
    if not agenda:
        return None
    jugados = [e for e in agenda.get("events", [])
               if e["competitions"][0]["status"]["type"].get("completed")]
    if not jugados:
        return None
    resumen = intentar(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{LIGA}/summary?event={jugados[-1]['id']}")
    if not resumen or "rosters" not in resumen:
        return None

    nuestro = next((r for r in resumen["rosters"] if r["team"]["id"] == BOCA), None)
    if not nuestro:
        return None

    def gente(titulares):
        salida = []
        for p in nuestro.get("roster", []):
            if bool(p.get("starter")) != titulares:
                continue
            if not titulares and not p.get("subbedIn"):
                salida.append({"nombre": p["athlete"]["displayName"], "dorsal": p.get("jersey", ""),
                               "puesto": p.get("position", {}).get("abbreviation", ""), "entro": False})
            elif not titulares:
                salida.append({"nombre": p["athlete"]["displayName"], "dorsal": p.get("jersey", ""),
                               "puesto": p.get("position", {}).get("abbreviation", ""), "entro": True})
            else:
                salida.append({"nombre": p["athlete"]["displayName"], "dorsal": p.get("jersey", ""),
                               "puesto": p.get("position", {}).get("abbreviation", ""),
                               "salio": bool(p.get("subbedOut"))})
        return salida

    duelo = resumen["header"]["competitions"][0]
    rival, propios, ajenos = "", None, None
    for c in duelo.get("competitors", []):
        if c["team"]["id"] == BOCA:
            propios = c.get("score")
        else:
            rival = c["team"].get("displayName", "")
            ajenos = c.get("score")
    fecha = duelo.get("date", "")[:10]
    if fecha:
        a, m, d = fecha.split("-")
        fecha = f"{d}/{m}"

    return {
        "rival": rival,
        "resultado": f"{propios}-{ajenos}" if propios is not None else "",
        "gano": (propios or "0") > (ajenos or "0"),
        "perdio": (propios or "0") < (ajenos or "0"),
        "fecha": fecha,
        "formacion": nuestro.get("formation") or "",
        "titulares": gente(True),
        "suplentes": gente(False),
    }


def main():
    datos = {
        "actualizado": datetime.now(AR).strftime("%Y-%m-%d %H:%M"),
        "plantel": plantel(),
        "tabla": tabla(),
        "ultimo": ultimo_equipo(),
    }
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"plantel: {len(datos['plantel'])} jugadores · tabla: {len(datos['tabla']['filas'])} equipos"
          f" · último: {'sí' if datos['ultimo'] else 'no'}")


if __name__ == "__main__":
    main()
