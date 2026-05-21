# Face Login Local

Aplicacion local en Python para registro e inicio de sesion tradicional y facial.

## Funcionalidades

- Registro e inicio de sesion con usuario y contrasena (hash PBKDF2).
- Registro e inicio de sesion facial con `InsightFace` (embeddings, no ORB).
- Preview en vivo de la camara: rectangulos verdes, puntos cyan en landmarks, contador de rostros.
- Persistencia local con `SQLite` en `data/app.db`.
- Separacion visual entre modo tradicional y modo facial en la UI.
- Captura robusta con OpenCV: `Esc` captura, cerrar la ventana cancela.
- Migracion automatica de usuarios legacy en archivos planos a `SQLite`.
- Carga del modelo con fallback de GPU a CPU.

## Estructura

```text
app/
  auth_service.py   -- logica de registro/login tradicional y facial
  camera_service.py -- captura OpenCV con deteccion en vivo y cancelacion
  config.py         -- rutas, umbrales y constantes
  database.py       -- esquema SQLite y migracion legacy
  face_service.py   -- deteccion, preview, extraccion y verificacion facial
  main.py           -- composicion de servicios y arranque
  security.py       -- hash y verificacion de contraseñas
  ui.py             -- interfaz Tkinter con modos separados
data/
  app.db
  faces/
Login_Vision.py
requirements.txt
```

## Dependencias

```bash
pip install -r requirements.txt
```

`InsightFace` necesita `onnxruntime`. Si falta `InsightFace`, la aplicacion igual abre pero deshabilita el flujo facial con un mensaje en pantalla.

### Conflicto conocido con opencv-python-headless

`InsightFace` instala `albumentations`, que a su vez instala `opencv-python-headless`. Si ambos paquetes OpenCV coexisten, `cv2.imshow()` deja de funcionar (GUI: NONE) y la ventana de camara no abre.

**Solucion:**
```bash
pip uninstall opencv-python-headless -y
pip install opencv-python --force-reinstall
```

## Ejecucion

```bash
python Login_Vision.py
```

## Flujo facial

1. Ingresa el usuario.
2. Abre la camara con preview en vivo (rectangulos, puntos, contador).
3. Presiona `Esc` para capturar.
4. Si cierras la ventana de la camara, el flujo se cancela.
5. La app exige exactamente un rostro por captura.
6. Los embeddings se normalizan L2; el umbral de coincidencia es `0.65` (cosine > 0.79).

## Flujo tradicional

1. Ingresa usuario y contrasena.
2. Las contraseñas se almacenan con hash PBKDF2 (120,000 iteraciones).
3. La verificacion usa comparacion de tiempo constante (`hmac.compare_digest`).

## Limpieza aplicada

- Los usuarios legacy en archivos planos se migran automaticamente a `SQLite` y luego se eliminan.
- El flujo nuevo ya no lee credenciales desde la raiz del proyecto.
- `data/`, `.venv/` y `__pycache__/` quedan fuera del control de versiones.

## Ajuste del umbral facial

Si el login facial rechaza demasiado o acepta a cualquiera, edita `FACE_MATCH_THRESHOLD` en `app/config.py`:

| Umbral | Cosine equivalente | Efecto |
|--------|-------------------|--------|
| `0.55` | > 0.85 | Muy estricto |
| `0.65` | > 0.79 | Default actual |
| `0.80` | > 0.68 | Mas permisivo |
| `1.00` | > 0.50 | Baja seguridad |

## Limitaciones actuales

- No hay liveness o anti-spoofing.
- Es una app local de escritorio, no un servicio multiusuario.
