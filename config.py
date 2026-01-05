from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
import sys

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout), # Вивід у консоль
            logging.FileHandler("app.log", encoding="utf-8") # Запис у файл
        ]
    )

setup_logging()

class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str

    setlist_api_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()