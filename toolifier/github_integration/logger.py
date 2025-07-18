"""Модуль логирования проекта"""

from loguru import logger
import os
import sys

class ProjectLogger:
    def __init__(self):
        self._setup_logging()
    
    def _setup_logging(self):
        """Настройка логгера"""
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        logger.add(
            "logs/app.log",
            rotation="100 MB",
            retention="30 days",
            compression="zip"
        )

# Инициализация глобального логгера
log = logger

