# Face Login Local

Aplicacion local en Python para registro e inicio de sesion tradicional y facial.

## Cambios principales

- Persistencia local con `SQLite` en `data/app.db`.
- Contraseñas con hash PBKDF2, no texto plano.
- Captura robusta con OpenCV: `Esc` captura y cerrar la ventana cancela.
- Verificacion facial con `InsightFace` mediante embeddings, no ORB.
- Estructura modular para separar UI, base de datos, camara y biometria.

## Estructura

```text
app/
  auth_service.py
  camera_service.py
  config.py
  database.py
  face_service.py
  main.py
  security.py
  ui.py
data/
  app.db
  faces/
Login_Vision.py
requirements.txt
```

## Dependencias

Instala las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

`InsightFace` necesita `onnxruntime`. Si falta alguna dependencia, la aplicacion igual abre, pero deja deshabilitado el flujo facial con un mensaje claro en la pantalla principal.

## Ejecucion

```bash
python Login_Vision.py
```

## Flujo facial

1. Ingresa el usuario.
2. Abre la camara.
3. Presiona `Esc` para capturar.
4. Si cierras la ventana de la camara, el flujo se cancela.
5. La app exige exactamente un rostro por captura.
6. La carga del modelo intenta GPU primero y si falla cambia a CPU.

## Limpieza aplicada

- Los usuarios legacy en archivos planos se migran automaticamente a `SQLite` y luego se eliminan.
- El flujo nuevo ya no lee credenciales desde la raiz del proyecto.
- `data/` y `.venv/` quedan fuera del control de versiones.

## Limitaciones actuales

- No hay liveness o anti-spoofing.
- Es una app local de escritorio, no un servicio multiusuario.
