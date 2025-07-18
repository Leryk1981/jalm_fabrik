"""
Логирование для CLI
"""

import logging
import sys
from typing import Optional

def setup_logger(debug: bool = False, level: Optional[str] = None) -> logging.Logger:
    """Настраивает и возвращает логгер"""
    
    # Определяем уровень логирования
    if level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    elif debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    # Создаем логгер
    logger = logging.getLogger('jalm-cli')
    logger.setLevel(log_level)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Создаем обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Настраиваем формат
    if debug:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = 'jalm-cli') -> logging.Logger:
    """Получает логгер по имени"""
    return logging.getLogger(name) 