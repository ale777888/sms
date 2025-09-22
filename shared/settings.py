"""项目配置加载模块。"""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseSettings, Field, validator


class EnvSettings(BaseSettings):
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    sms_token: str = Field(..., env="SMS_TOKEN")
    base_url: str = Field("https://sms-szfang.com/yhapi", env="BASE_URL")
    db_url: str = Field("sqlite:///./data/tg_sms.db", env="DB_URL")
    jwt_secret: str = Field(..., env="JWT_SECRET")
    poll_base: float = Field(6.0, env="POLL_BASE")
    poll_timeout: int = Field(120, env="POLL_TIMEOUT")
    poll_jitter: float = Field(3.0, env="POLL_JITTER")
    poll_max_backoff: float = Field(30.0, env="POLL_MAX_BACKOFF")
    price_currency: str = Field("CNY", env="PRICE_CURRENCY")
    log_dir: Path = Field(Path("/var/log/tg-sms-suite"), env="LOG_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("log_dir")
    def _ensure_log_dir(cls, value: Path) -> Path:
        value.mkdir(parents=True, exist_ok=True)
        return value


settings = EnvSettings()
