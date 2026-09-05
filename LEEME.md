# Boca — avisos y calendario

Dos cosas:

1. **La app** (`docs/`): calendario de Boca con los próximos partidos, los resultados,
   el plantel completo con estadísticas y la tabla de posiciones.
   Se instala en el iPhone desde Safari → Compartir → *Agregar a inicio*.
2. **El mail**: todos los días a las 9 de la mañana, si Boca juega, llega un mail así:

   ```
   boca vs. lanús - 21.30 - la bombonera - liga profesional clausura
   ```

Incluye partidos oficiales y amistosos: Liga Profesional (Apertura y Clausura),
Copa Argentina, Supercopa, Libertadores, Sudamericana, Recopa, Mundial de Clubes
y amistosos.

## Cómo funciona

| archivo | qué hace |
|---|---|
| `traer_partidos.py` | baja los partidos de ESPN y los guarda en `docs/partidos.json` |
| `traer_plantel.py` | baja el plantel, las estadísticas, la tabla y el último equipo → `docs/plantel.json` |
| `avisar.py` | si Boca juega hoy, manda el mail |
| `correr.sh` | hace todo seguido (lo que ejecuta la Mac a las 9) |
| `docs/index.html` | la app |

La app tiene cuatro solapas:

- **Próximos**: el próximo partido con cuenta regresiva y el resto del calendario.
- **Resultados**: los partidos ya jugados con el marcador.
- **Plantel**: goleador, asistidor y amonestado del año; el equipo del último partido
  (formación, titulares y suplentes, con ↑ el que entró y ↓ el que salió) y todo el
  plantel por puesto con partidos jugados, goles y asistencias.
- **Tabla**: las posiciones de la zona de Boca, con Boca resaltado.

*Lesionados* y *cedidos a préstamo* no están: la API gratuita de ESPN no los publica
para el fútbol argentino.

Probar sin mandar nada:

```bash
python3 ~/boca-alertas/avisar.py --prueba
```

## Quién manda el aviso

- **GitHub Actions** (el principal): `.github/workflows/aviso-diario.yml` corre todos los
  días a las 12:00 UTC = 9:00 de Argentina, con la Mac apagada. Necesita las claves
  cargadas como *secrets* del repo: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`,
  `AVISAR_A` (salen del `.env`).
- **La Mac** (respaldo): `com.facundo.boca-alertas.plist` corre a las 9:00.
  Antes de mandar hace `git pull`, así que si GitHub ya avisó hoy no manda nada duplicado
  (la lista de días ya avisados vive en `avisados.json`, que sí se sube al repo).

El archivo del workflow está en el `.gitignore` porque el token de GitHub no tiene el
permiso `workflow`: para editarlo hay que hacerlo desde la web de GitHub.

## La app

Anda en `https://fakka-cloud.github.io/boca-alertas/`.
Se instala en el iPhone desde Safari con **Compartir → Agregar a inicio**.

El `.env` con la contraseña **no se sube** al repo (está en el `.gitignore`).
