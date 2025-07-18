"""
Конфигурация Research Layer
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class ResearchConfig:
    """Конфигурация для Research Layer"""
    
    # Пути к файлам данных
    patterns_dir: Path = Path("research/patterns")
    raw_actions_file: Path = Path("research/patterns/raw_actions.csv")
    raw_patterns_file: Path = Path("research/patterns/raw_patterns.csv")
    grouped_file: Path = Path("research/patterns/grouped.json")
    template_groups_file: Path = Path("research/patterns/template_groups.json")
    
    # Источники данных
    data_sources: Optional[List[str]] = None
    
    # Настройки анализа
    min_pattern_frequency: int = 3
    max_pattern_length: int = 10
    similarity_threshold: float = 0.8
    
    # Настройки экспорта
    export_formats: Optional[List[str]] = None
    
    def __post_init__(self):
        """Инициализация значений по умолчанию"""
        if self.data_sources is None:
            self.data_sources = [
                "github_api",
                "stackoverflow_api", 
                "npm_registry",
                "pypi_registry",
                "docker_hub"
            ]
        
        if self.export_formats is None:
            self.export_formats = ["csv", "json", "yaml"]
        
        # Создаем директории если не существуют
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
    
    def get_data_path(self, filename: str) -> Path:
        """Получить полный путь к файлу данных"""
        return self.patterns_dir / filename
    
    def validate(self) -> bool:
        """Проверка корректности конфигурации"""
        try:
            # Проверяем что директории существуют или могут быть созданы
            self.patterns_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Ошибка валидации конфигурации: {e}")
            return False


# Глобальная конфигурация по умолчанию
DEFAULT_CONFIG = ResearchConfig()


def load_config(config_path: str = None) -> ResearchConfig:
    """Загрузка конфигурации из файла или создание по умолчанию"""
    if config_path and os.path.exists(config_path):
        # TODO: Реализовать загрузку из YAML/JSON файла
        pass
    
    return DEFAULT_CONFIG 