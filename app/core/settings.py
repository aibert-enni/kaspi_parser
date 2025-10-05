import json
import logging
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent

logger = logging.getLogger(__name__)

class DBSettings(BaseModel):
    URL: str

class ParserSettings(BaseModel):
    SLEEP_TIME_MINUTES: int

class AsyncioSettings(BaseModel):
    MAX_CONCURRENT_TASKS: int = 1

class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_nested_delimiter="__",
    )
    db: DBSettings
    parser: ParserSettings
    asyncio: AsyncioSettings

settings = CommonSettings() # type: ignore

def print_settings():
    logger.info(json.dumps(settings.model_dump(), indent=2, default=str))