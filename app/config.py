import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    whatsapp_token: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    verify_token: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
    app_secret: str = os.getenv("META_APP_SECRET", "")
    graph_api_version: str = os.getenv("META_GRAPH_API_VERSION", "v23.0")
    port: int = int(os.getenv("PORT", "8000"))

settings = Settings()
