"""Модуль конфигурации проекта"""

from pydantic import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    """Настройки приложения"""
    api_host: str = "localhost"
    api_port: int = 8000
    github_token: Optional[str] = None
    log_level: str = "INFO"
    
    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        env_file_encoding = "utf-8"

# Глобальный объект конфигурации
config = Settings()

