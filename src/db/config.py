from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FORMAT = "%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s"
DT_FORMAT = "%d.%m.%Y %H:%M:%S"


class Settings(BaseSettings):
    """Настройки подключения к базе данных."""

    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    BOT_TOKEN: str
    SERVER_URL: str
    UVICORN_PORT: int
    UVICORN_SERVER: str

    @property
    def database_url(self):
        """Возвращает DATABASE_URL."""
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        """Класс конфигурации настроек."""

        env_file = BASE_DIR / ".env"
        extra = "ignore"


settings = Settings()
