"""
Конфигурация CLI
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Класс для управления конфигурацией CLI"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = self._load_config()
        
    def _get_default_config_path(self) -> str:
        """Получает путь к файлу конфигурации по умолчанию"""
        home = Path.home()
        config_dir = home / '.jalm'
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / 'config.json')
    
    def _load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию из файла"""
        default_config = {
            'services': {
                'core-runner': {
                    'port': 8000,
                    'path': './core-runner',
                    'docker_image': 'jalm/core-runner:latest'
                },
                'tula-spec': {
                    'port': 8001,
                    'path': './tula_spec',
                    'docker_image': 'jalm/tula-spec:latest'
                },
                'shablon-spec': {
                    'port': 8002,
                    'path': './shablon_spec',
                    'docker_image': 'jalm/shablon-spec:latest'
                }
            },
            'docker': {
                'compose_file': './docker/docker-compose.yml',
                'network': 'jalm-network'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Объединяем с конфигурацией по умолчанию
                    self._merge_configs(default_config, user_config)
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
        
        return default_config
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]):
        """Объединяет конфигурации"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_configs(default[key], value)
            else:
                default[key] = value
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Получает конфигурацию сервиса"""
        return self.config.get('services', {}).get(service_name, {})
    
    def get_docker_config(self) -> Dict[str, Any]:
        """Получает конфигурацию Docker"""
        return self.config.get('docker', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Получает конфигурацию логирования"""
        return self.config.get('logging', {})
    
    def save(self):
        """Сохраняет конфигурацию в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
    
    def update(self, key: str, value: Any):
        """Обновляет значение в конфигурации"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value 