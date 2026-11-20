"""Environment-based application configuration."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    sportradar_api_key: str
    access_level: str
    language_code: str
    database_url: str
    request_timeout: int

def get_settings() -> Settings:
    return Settings(
        sportradar_api_key=os.getenv("SPORTRADAR_API_KEY", "").strip(),
        access_level=os.getenv("SPORTRADAR_ACCESS_LEVEL", "trial").strip(),
        language_code=os.getenv("SPORTRADAR_LANGUAGE", "en").strip(),
        database_url=os.getenv("DATABASE_URL", "sqlite:///tennis_analytics.db").strip(),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
    )
