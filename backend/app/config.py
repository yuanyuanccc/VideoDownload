import os
from pydantic import BaseModel
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_model: str = "deepseek-chat"
    free_daily_limit: int = 1
    max_subtitle_length: int = 10000
    max_chat_context: int = 5
    bilibili_sessdata: str = os.getenv("BILIBILI_SESSDATA", "")


@lru_cache()
def get_settings() -> Settings:
    return Settings()