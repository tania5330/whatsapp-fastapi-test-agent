import logging
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from app.config import settings
from app.agent import build_reply
from app.whatsapp import send_text_message, verify_signature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agente de WhatsApp - Demo",
    description="Backend mínimo con FastAPI para probar WhatsApp Cloud API.",
    version="1.0.0",
)

# In-memory deduplication is sufficient for this demo only.
processed_message_ids: set[str] = set()


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "whatsapp-fastapi-test-agent",
        "webhook": "/webhook",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/webhook", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    """Meta calls this endpoint when subscribing the webhook."""
    if (
        hub_mode == "subscribe"
        and settings.verify_token
        and hub_verify_token == settings.verify_token
        and hub_challenge is not None
    ):
        return hub_challenge
    raise HTTPException(status_code=403, detail="Verificación de webhook fallida")


@app.post("/webhook")
async def receive_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(raw_body, signature):
        raise HTTPException(status_code=403, detail="Firma de Meta no válida")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON no válido")

    # Acknowledge webhook notifications that are not incoming messages (e.g. statuses).
    try:
        entries = payload.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for message in value.get("messages", []) or []:
                    message_id = message.get("id")
                    if message_id and message_id in processed_message_ids:
                        continue
                    if message_id:
                        processed_message_ids.add(message_id)

                    sender = message.get("from")
                    if not sender:
                        continue

                    if message.get("type") == "text":
                        incoming_text = message.get("text", {}).get("body", "")
                        reply = build_reply(incoming_text)
                    else:
                        reply = (
                            "Por ahora puedo procesar mensajes de texto. "
                            "Envíame tu consulta escrita, por favor."
                        )

                    try:
                        await send_text_message(sender, reply)
                    except Exception:
                        # Log the failure; return 200 so Meta does not retry indefinitely.
                        logger.exception("No se pudo responder al mensaje entrante")
    except Exception:
        logger.exception("Error procesando notificación de webhook")
        # Return 200 for a validly received notification; inspect server logs to debug.

    return {"status": "received"}
