import hashlib
import hmac
import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Validate X-Hub-Signature-256 when META_APP_SECRET is configured."""
    if not settings.app_secret:
        return True  # Convenient for the first local test; configure in production.
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.app_secret.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    received = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, received)


async def send_text_message(to: str, body: str) -> dict[str, Any]:
    if not settings.whatsapp_token or not settings.phone_number_id:
        raise RuntimeError(
            "Faltan WHATSAPP_ACCESS_TOKEN o WHATSAPP_PHONE_NUMBER_ID en el archivo .env"
        )

    url = (
        f"https://graph.facebook.com/{settings.graph_api_version}/"
        f"{settings.phone_number_id}/messages"
    )
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.is_error:
            logger.error("Meta API error %s: %s", response.status_code, response.text)
        response.raise_for_status()
        return response.json()
