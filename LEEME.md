# Boca — avisos y calendario

Dos cosas:

1. **La app** (`docs/`): calendario de Boca con los próximos partidos y los resultados.
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
| `avisar.py` | si Boca juega hoy, manda el mail |
| `correr.sh` | hace las dos cosas seguidas (lo que ejecuta la Mac a las 9) |
| `docs/index.html` | la app |

Probar sin mandar nada:

```bash
python3 ~/boca-alertas/avisar.py --prueba
```

## Quién manda el aviso

- **La Mac** (ya andando): `com.facundo.boca-alertas.plist` corre a las 9:00.
  Refresca el calendario, lo sube a GitHub y manda el mail si Boca juega hoy.
  Si a las 9 la Mac está apagada, el aviso sale cuando la prendés.
- **GitHub Actions** (opcional, apagado): `.github/workflows/aviso-diario.yml` haría lo
  mismo con la Mac apagada, pero el token de GitHub no tiene el permiso `workflow`,
  así que el archivo queda local (está en el `.gitignore`). Para prenderlo hay que
  darle ese permiso al token y cargar las claves como *secrets* del repo:
  `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `AVISAR_A` (salen del `.env`).

## Lo que falta hacer a mano

Prender la web app: **Settings → Pages → Source: Deploy from a branch → main / docs → Save**.
Queda en `https://fakka-cloud.github.io/boca-alertas/`, y se instala en el iPhone
desde Safari con **Compartir → Agregar a inicio**.

El `.env` con la contraseña **no se sube** al repo (está en el `.gitignore`).
