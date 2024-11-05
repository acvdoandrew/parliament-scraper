from pydantic import BaseSettings


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list = ["*"]
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    REQUEST_TIMEOUT: float = 30.0  # seconds

    # HTTPX specific settings
    HTTPX_TIMEOUT: float = 30.0
    HTTPX_MAX_REDIRECTS: int = 5
    HTTPX_VERIFY_SSL: bool = True

    # Optional: Add limits
    HTTPX_LIMITS_MAX_CONNECTIONS: int = 100
    HTTPX_LIMITS_MAX_KEEPALIVE: int = 20


settings = Settings()
