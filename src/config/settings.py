import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Server Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # Cache Settings
    CACHE_TTL = int(os.getenv("CACHE_TTL", 900))
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", 100))

    # CORS Settings
    ALLOWED_ORIGINS = ["*"]

    # Scraping Settings
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
    USER_AGENT = os.getenv(
        "USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )


settings = Settings()
