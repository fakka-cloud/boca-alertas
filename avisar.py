#!/usr/bin/env python3
"""Si Boca juega hoy, manda el mail de aviso. Pensado para correr a las 9 de la mañana."""

import json, os, smtplib, ssl, sys
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

AR = timezone(timedelta(hours=-3))
CASA = Path(__file__).parent
PARTIDOS = CASA / "docs" / "partidos.json"
YA_AVISE = CASA / "avisados.json"

# el usuario pidió los nombres cortos, como los dice la gente
APODOS = {
    "Boca Juniors": "boca", "River Plate": "river", "Racing Club": "racing",
    "Independiente": "independiente", "San Lorenzo": "san lorenzo",
    "Argentinos Juniors": "argentinos", "Vélez Sarsfield": "vélez",
    "Estudiantes de La Plata": "estudiantes", "Newell's Old Boys": "newell's",
    "Rosario Central": "central", "Atlético Tucumán": "atlético tucumán",
    "Central Córdoba (Santiago del Estero)": "central córdoba",
    "Gimnasia y Esgrima La Plata": "gimnasia", "Unión (Santa Fe)": "unión",
    "Instituto (Córdoba)": "instituto", "Talleres (Córdoba)": "talleres",
    "Defensa y Justicia": "defensa", "Godoy Cruz": "godoy cruz",
}

def corto(nombre):
    if nombre in APODOS:
        return APODOS[nombre]
    # "Gimnasia (Mendoza)" queda feo entero: me quedo con lo de afuera del paréntesis
    return nombre.split("(")[0].strip().lower()

def cancha(estadio):
    # "Alberto José Armando (La Bombonera)" -> "la bombonera"
    if "(" in estadio and ")" in estadio:
        return estadio[estadio.index("(") + 1:estadio.index(")")].strip().lower()
    return estadio.lower()

def linea(p):
    """boca vs. lanus - 21.00 - la bombonera - copa argentina"""
    rival = corto(p["visitante"]) if p["de_local"] else corto(p["local"])
    quien = f"boca vs. {rival}" if p["de_local"] else f"{rival} vs. boca"
    return f'{quien} - {p["hora"].replace(":", ".")} - {cancha(p["estadio"])} - {p["torneo"].lower()}'

def leer_env():
    datos = {}
    archivo = CASA / ".env"
    if archivo.exists():
        for renglon in archivo.read_text(encoding="utf-8").splitlines():
            if "=" in renglon and not renglon.strip().startswith("#"):
                clave, valor = renglon.split("=", 1)
                datos[clave.strip()] = valor.strip()
    # en GitHub Actions las credenciales vienen por variables de entorno
    datos.update({k: v for k, v in os.environ.items() if k.startswith(("SMTP_", "AVISAR_"))})
    return datos

def mandar(env, partidos, hoy):
    cuerpo = "\n".join(linea(p) for p in partidos)
    msg = EmailMessage()
    msg["Subject"] = "hoy juega boca ⚽" if len(partidos) == 1 else "hoy juega boca (2 partidos) ⚽"
    msg["From"] = f'{env.get("SMTP_NOMBRE", "avisos")} <{env["SMTP_USER"]}>'
    msg["To"] = env["AVISAR_A"]
    msg.set_content(f"{cuerpo}\n\ncalendario completo: https://fakka-cloud.github.io/boca-alertas/\n")

    with smtplib.SMTP_SSL(env["SMTP_HOST"], int(env["SMTP_PORT"]),
                          context=ssl.create_default_context(), timeout=120) as s:
        s.login(env["SMTP_USER"], env["SMTP_PASS"])
        s.send_message(msg)

def main():
    prueba = "--prueba" in sys.argv          # muestra el mail sin mandarlo
    forzar = "--forzar" in sys.argv          # manda aunque ya haya avisado hoy

    hoy = datetime.now(AR).strftime("%Y-%m-%d")
    if not PARTIDOS.exists():
        print("falta docs/partidos.json: corré traer_partidos.py primero", file=sys.stderr)
        return 1

    datos = json.loads(PARTIDOS.read_text(encoding="utf-8"))
    de_hoy = [p for p in datos["partidos"] if p["fecha"] == hoy]
    if not de_hoy:
        print(f"{hoy}: boca no juega hoy")
        return 0

    for p in de_hoy:
        print(linea(p))
    if prueba:
        print("(prueba: no mandé nada)")
        return 0

    avisados = json.loads(YA_AVISE.read_text(encoding="utf-8")) if YA_AVISE.exists() else []
    if hoy in avisados and not forzar:
        print("ya había avisado hoy, no repito")
        return 0

    env = leer_env()
    faltan = [c for c in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "AVISAR_A") if not env.get(c)]
    if faltan:
        print("faltan credenciales:", ", ".join(faltan), file=sys.stderr)
        return 1

    mandar(env, de_hoy, hoy)
    YA_AVISE.write_text(json.dumps(sorted(set(avisados + [hoy]))[-60:]), encoding="utf-8")
    print(f'mail enviado a {env["AVISAR_A"]}')
    return 0

if __name__ == "__main__":
    sys.exit(main())
