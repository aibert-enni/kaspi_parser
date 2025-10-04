import json
import logging
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent

logger = logging.getLogger(__name__)

class DBSettings(BaseModel):
    URL: str


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_nested_delimiter="__",
    )
    db: DBSettings

settings = CommonSettings() # type: ignore

def print_settings():
    logger.info(json.dumps(settings.model_dump(), indent=2, default=str))