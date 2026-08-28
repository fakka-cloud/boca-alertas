#!/usr/bin/env python3
"""Baja todos los partidos de Boca (oficiales y amistosos) desde ESPN
y los deja ordenados en docs/partidos.json."""

import json, sys, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

BOCA = "5"                       # id de Boca Juniors en ESPN
AR = timezone(timedelta(hours=-3))
BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"

# torneos donde Boca puede aparecer. Si en el futuro juega otro, se agrega acá.
TORNEOS = {
    "arg.1":                  "Liga Profesional",
    "arg.copa":               "Copa Argentina",
    "arg.supercopa":          "Supercopa Argentina",
    "arg.trofeo_campeones":   "Trofeo de Campeones",
    "conmebol.libertadores":  "Copa Libertadores",
    "conmebol.sudamericana":  "Copa Sudamericana",
    "conmebol.recopa":        "Recopa Sudamericana",
    "fifa.cwc":               "Mundial de Clubes",
    "club.friendly":          "Amistoso",
}

# la Liga Profesional parte el año en dos torneos; ESPN lo dice en seasonType
SUBTORNEO = {"apertura": "Apertura", "clausura": "Clausura"}


# ESPN devuelve 403 a casi cualquier User-Agent: solo pasa el de curl.
AGENTES = ["curl/8.7.1", "curl/8.4.0", "curl/7.88.1"]


def bajar(url):
    ultimo = None
    for agente in AGENTES:
        req = urllib.request.Request(url, headers={"User-Agent": agente})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 403:
                raise
            ultimo = e
    raise ultimo


def nombre_torneo(liga, ev):
    base = TORNEOS[liga]
    tipo = (ev.get("seasonType") or {}).get("name", "").lower()
    for clave, lindo in SUBTORNEO.items():
        if clave in tipo:
            return f"{base} {lindo}"
    return base


def parsear(liga, ev):
    comp = ev["competitions"][0]
    equipos = {c["homeAway"]: c for c in comp["competitors"]}
    local, visita = equipos.get("home"), equipos.get("away")
    if not local or not visita:
        return None

    cuando = datetime.strptime(ev["date"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc).astimezone(AR)
    estado = (comp.get("status") or ev.get("status") or {}).get("type", {})

    def marcador(c):
        v = c.get("score")
        if isinstance(v, dict):
            v = v.get("value") if v.get("value") is not None else v.get("displayValue")
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None

    return {
        "id": ev["id"],
        "fecha": cuando.strftime("%Y-%m-%d"),
        "hora": cuando.strftime("%H:%M"),
        "local": local["team"]["displayName"],
        "visitante": visita["team"]["displayName"],
        "escudo_local": (local["team"].get("logos") or [{}])[0].get("href", ""),
        "escudo_visitante": (visita["team"].get("logos") or [{}])[0].get("href", ""),
        "de_local": local["team"]["id"] == BOCA,
        "estadio": (comp.get("venue") or {}).get("fullName", "A confirmar"),
        "ciudad": ((comp.get("venue") or {}).get("address") or {}).get("city", ""),
        "torneo": nombre_torneo(liga, ev),
        "jugado": bool(estado.get("completed")),
        "estado": estado.get("description", ""),
        "goles_local": marcador(local),
        "goles_visitante": marcador(visita),
    }


def main():
    hoy = datetime.now(AR)
    temporadas = {hoy.year, hoy.year + 1} if hoy.month >= 11 else {hoy.year}

    # ESPN separa lo jugado de lo que viene: sin fixture da los resultados,
    # con fixture=true da el calendario. Hay que pedir las dos cosas.
    partidos, fallos = {}, []
    for liga in TORNEOS:
        for temporada in sorted(temporadas):
            for pedido in ("", "&fixture=true"):
                try:
                    data = bajar(f"{BASE}/{liga}/teams/{BOCA}/schedule?season={temporada}{pedido}")
                except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
                    fallos.append(f"{liga}/{temporada}: {e}")
                    continue
                for ev in data.get("events", []):
                    try:
                        p = parsear(liga, ev)
                    except (KeyError, IndexError, ValueError):
                        continue
                    if p:
                        partidos[p["id"]] = p      # el id evita duplicados entre pedidos

    if not partidos:
        print("no traje ningún partido:", "; ".join(fallos) or "sin detalle", file=sys.stderr)
        return 1

    salida = {
        "actualizado": hoy.strftime("%Y-%m-%d %H:%M"),
        "partidos": sorted(partidos.values(), key=lambda p: (p["fecha"], p["hora"])),
    }
    destino = Path(__file__).parent / "docs" / "partidos.json"
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")

    proximos = [p for p in salida["partidos"] if p["fecha"] >= hoy.strftime("%Y-%m-%d")]
    print(f"{len(salida['partidos'])} partidos guardados ({len(proximos)} por jugar)")
    if fallos:
        print("torneos que no respondieron:", "; ".join(fallos), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
