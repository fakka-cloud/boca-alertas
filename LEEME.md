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

## Los dos avisadores

- **En la Mac** (ya andando): `com.facundo.boca-alertas.plist` corre a las 9:00.
  Si la Mac está apagada a esa hora, el aviso sale cuando la prendés.
- **En GitHub** (falta activarlo): `.github/workflows/aviso-diario.yml` corre a las
  9:00 aunque la Mac esté apagada. Para que funcione hay que hacer los pasos de abajo.

## Pasos que tenés que hacer vos en GitHub

1. Crear el repo `boca-alertas` en <https://github.com/organizations/fakka-cloud/repositories/new>
   (público, vacío, sin README).
2. En la carpeta del proyecto, subirlo:

   ```bash
   cd ~/boca-alertas && git push -u origin main
   ```

3. Prender la app: **Settings → Pages → Source: Deploy from a branch → main / docs → Save**.
   Queda en `https://fakka-cloud.github.io/boca-alertas/`.
4. Cargar las claves del mail en **Settings → Secrets and variables → Actions → New secret**,
   una por una (los valores están en el archivo `.env` de esta carpeta):
   `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `AVISAR_A`.
5. Probarlo: pestaña **Actions → aviso diario de boca → Run workflow**.

El `.env` con la contraseña **no se sube** al repo (está en el `.gitignore`).
