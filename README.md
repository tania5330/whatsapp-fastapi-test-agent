# Agente de WhatsApp de prueba (Python + FastAPI)

Backend mínimo para comprobar el ciclo:

**WhatsApp personal → número de prueba de Meta → webhook FastAPI → respuesta automática.**

El agente es intencionalmente sencillo y basado en reglas. No utiliza todavía un modelo de IA ni una base de datos. Así puedes validar la conexión antes de integrar el agente real.

## 1. Requisitos

- Python 3.11 o superior (recomendado: 3.12).
- Una app de Meta con WhatsApp configurado.
- Número de prueba de Meta y un destinatario permitido/verificado.
- Token de acceso de Meta válido.
- Para recibir webhooks desde Meta, el backend debe tener una URL HTTPS pública. Para desarrollo local puedes usar un túnel HTTPS como ngrok o Cloudflare Tunnel.

## 2. Configuración local en Windows

Abre PowerShell dentro de la carpeta del proyecto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Abre `.env` y completa:

- `WHATSAPP_PHONE_NUMBER_ID`: identificador del número de teléfono de prueba.
- `WHATSAPP_BUSINESS_ACCOUNT_ID`: identificador de la cuenta de mensajes/WABA. Se conserva para futuras integraciones; este demo no lo necesita para enviar mensajes.
- `WHATSAPP_ACCESS_TOKEN`: token temporal generado por Meta.
- `WHATSAPP_VERIFY_TOKEN`: inventa una clave privada, por ejemplo una frase larga aleatoria. Debe ser exactamente la misma que introducirás en Meta.
- `META_APP_SECRET`: opcional al principio. Para producción, configúralo para validar la firma de Meta.
- `META_GRAPH_API_VERSION`: usa una versión Graph API vigente habilitada en tu app. El valor del ejemplo es configurable y puede requerir actualización desde el panel/documentación de Meta.

No compartas el `.env`, no lo subas a GitHub y no pegues el token en capturas.

## 3. Ejecutar el backend

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Comprueba en el navegador:

- `http://localhost:8000/` — estado del servicio.
- `http://localhost:8000/health` — health check.
- `http://localhost:8000/docs` — documentación interactiva.

## 4. Exponerlo para recibir webhooks

Meta no puede llamar a `localhost`. Debes exponer el puerto 8000 mediante un túnel HTTPS.

Ejemplo con ngrok, si ya lo tienes instalado:

```powershell
ngrok http 8000
```

Copia la URL HTTPS que te proporciona, por ejemplo `https://xxxx.ngrok-free.app`.

La URL de devolución de llamada será:

```text
https://TU-DOMINIO-PUBLICO/webhook
```

No uses literalmente `TU-DOMINIO-PUBLICO`: reemplázalo por tu URL real.

## 5. Configurar el webhook en Meta

En el panel de tu app de Meta:

1. Abre el producto/caso de uso de WhatsApp y localiza la configuración de webhooks.
2. En **URL de devolución de llamada**, pega `https://TU-DOMINIO-PUBLICO/webhook`.
3. En **Token de verificación**, pega exactamente el valor de `WHATSAPP_VERIFY_TOKEN` de tu `.env`.
4. Pulsa **Verificar y guardar**.
5. Suscribe el webhook al campo **messages**.

La interfaz de Meta puede variar. Si Meta solicita una URL HTTPS accesible, asegúrate de que el servidor y el túnel sigan ejecutándose.

## 6. Probar la conversación

Con el servidor y el túnel activos:

1. Desde el WhatsApp personal que agregaste como destinatario permitido, escribe al número de prueba de Meta.
2. Prueba `Hola`, `ayuda`, `horario`, `precio` o `contacto`.
3. El backend debería responder automáticamente.

Si el mensaje inicial de plantilla funcionó, pero no llegan respuestas a mensajes entrantes, revisa:
- Que la URL de callback sea correcta y termine en `/webhook`.
- Que el campo `messages` esté suscrito.
- Que el túnel y FastAPI sigan activos.
- Los registros (logs) de la terminal.
- Que el token no haya caducado y que `PHONE_NUMBER_ID` sea el correcto.

## 7. Desplegar

El proyecto incluye `Dockerfile` y `render.yaml` para facilitar un despliegue en Render:

1. Sube el proyecto a un repositorio Git privado.
2. En Render, crea un servicio web desde ese repositorio (Blueprint o Docker).
3. Configura las variables de entorno solicitadas por el servicio con los valores de tu `.env`.
4. Despliega y copia la URL HTTPS pública asignada.
5. Registra `https://TU-SERVICIO.onrender.com/webhook` en Meta y suscribe `messages`.

No subas el archivo `.env` al repositorio. Introduce los secretos directamente en el panel del proveedor.

## 8. Qué incluye y qué no incluye

Incluye:
- Endpoint de verificación GET `/webhook`.
- Endpoint de recepción POST `/webhook`.
- Envío de respuestas de texto mediante WhatsApp Cloud API.
- Respuestas de demostración por reglas.
- Health check y documentación automática.
- Validación opcional de firma `X-Hub-Signature-256` si configuras `META_APP_SECRET`.
- Ignora notificaciones de estado que no contengan mensajes entrantes.

Limitaciones deliberadas de esta demo:
- Deduplicación de mensajes en memoria: se pierde al reiniciar y no sirve para varias instancias.
- Sin base de datos, memoria conversacional, IA generativa ni panel administrativo.
- El token temporal de Meta caduca. Para producción se debe implementar una gestión segura de credenciales y un token apropiado.
- Antes de producción: persistencia/idempotencia, reintentos, colas, logging/monitorización, validación de firma obligatoria y gestión de errores.

## 9. Estructura

```text
whatsapp_fastapi_test_agent/
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   ├── main.py
│   └── whatsapp.py
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── render.yaml
├── requirements.txt
└── README.md
```
