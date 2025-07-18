"""
Research Layer - Модуль для сбора и анализа данных

Этот модуль отвечает за:
- Сбор исходных действий и паттернов
- Анализ данных использования
- Группировку по категориям
- Экспорт в форматы для других модулей
"""

__version__ = "1.0.0"
__author__ = "JALM Full Stack Team"

from .collector import DataCollector
from .analyzer import PatternAnalyzer
from .config import ResearchConfig

__all__ = [
    "DataCollector",
    "PatternAnalyzer", 
    "ResearchConfig"
] 