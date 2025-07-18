"""
Модуль сбора исходных действий и паттернов для Research Layer
"""

import csv
import json
import yaml
import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .config import ResearchConfig

logger = logging.getLogger(__name__)


class DataCollector:
    """
    Класс для сбора исходных данных (actions, patterns) из различных источников.
    Фокусируется на паттернах для создания чистых клиентских контейнеров JALM.
    """
    
    def __init__(self, config: Optional[ResearchConfig] = None):
        self.config = config or ResearchConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'JALM-Research-Layer/1.0'
        })
        
    def collect_actions(self) -> List[Dict[str, Any]]:
        """
        Собрать сырые действия из источников данных.
        Фокус на паттернах создания SPA/SSR, FastAPI/Go микросервисов.
        """
        actions = []
        
        for source in self.config.data_sources:
            try:
                if source == "github_api":
                    actions.extend(self._collect_from_github())
                elif source == "stackoverflow_api":
                    actions.extend(self._collect_from_stackoverflow())
                elif source == "npm_registry":
                    actions.extend(self._collect_from_npm())
                elif source == "pypi_registry":
                    actions.extend(self._collect_from_pypi())
                elif source == "docker_hub":
                    actions.extend(self._collect_from_dockerhub())
                    
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка сбора данных из {source}: {e}")
                
        return actions
    
    def collect_patterns(self) -> List[Dict[str, Any]]:
        """
        Собрать паттерны использования на основе собранных действий.
        Анализирует структуру для создания чистых контейнеров.
        """
        actions = self.collect_actions()
        patterns = []
        
        # Группировка по типам приложений
        app_types = {
            'spa': self._extract_spa_patterns(actions),
            'ssr': self._extract_ssr_patterns(actions),
            'api': self._extract_api_patterns(actions),
            'microservice': self._extract_microservice_patterns(actions)
        }
        
        for app_type, type_patterns in app_types.items():
            for pattern in type_patterns:
                patterns.append({
                    'pattern_name': f"{app_type}_{pattern['name']}",
                    'components': pattern['components'],
                    'env_vars': pattern['env_vars'],
                    'config_structure': pattern['config_structure'],
                    'frequency': pattern['frequency'],
                    'app_type': app_type,
                    'collected_at': datetime.now().isoformat()
                })
                
        return patterns
    
    def _collect_from_github(self) -> List[Dict[str, Any]]:
        """Сбор данных из GitHub API"""
        actions = []
        
        # Поиск популярных SPA/SSR проектов
        search_queries = [
            "react spa docker",
            "vue spa docker", 
            "next.js docker",
            "nuxt.js docker",
            "fastapi docker",
            "go microservice docker"
        ]
        
        for query in search_queries:
            try:
                # GitHub Search API
                response = self.session.get(
                    "https://api.github.com/search/repositories",
                    params={
                        'q': query,
                        'sort': 'stars',
                        'order': 'desc',
                        'per_page': 10
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for repo in data.get('items', []):
                        actions.append({
                            'action_type': f"create_{query.split()[0]}",
                            'technology': query.split()[0],
                            'complexity': self._estimate_complexity(repo),
                            'source': 'github',
                            'usage_count': repo.get('stargazers_count', 0),
                            'repo_name': repo.get('full_name'),
                            'description': repo.get('description'),
                            'language': repo.get('language'),
                            'created_at': repo.get('created_at')
                        })
                        
            except Exception as e:
                logger.error(f"Ошибка GitHub API для {query}: {e}")
                
        return actions
    
    def _collect_from_stackoverflow(self) -> List[Dict[str, Any]]:
        """Сбор данных из StackOverflow API"""
        actions = []
        
        # Поиск вопросов по конфигурации
        tags = ['docker', 'env', 'config', 'deployment']
        
        for tag in tags:
            try:
                response = self.session.get(
                    "https://api.stackexchange.com/2.3/questions",
                    params={
                        'tagged': tag,
                        'site': 'stackoverflow',
                        'sort': 'votes',
                        'order': 'desc',
                        'pagesize': 20
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for question in data.get('items', []):
                        actions.append({
                            'action_type': f"configure_{tag}",
                            'technology': tag,
                            'complexity': 1,  # StackOverflow вопросы обычно базовые
                            'source': 'stackoverflow',
                            'usage_count': question.get('score', 0),
                            'title': question.get('title'),
                            'tags': question.get('tags', []),
                            'created_at': datetime.fromtimestamp(question.get('creation_date', 0)).isoformat()
                        })
                        
            except Exception as e:
                logger.error(f"Ошибка StackOverflow API для {tag}: {e}")
                
        return actions
    
    def _collect_from_npm(self) -> List[Dict[str, Any]]:
        """Сбор данных из NPM Registry"""
        actions = []
        
        # Популярные пакеты для SPA/SSR
        packages = ['react', 'vue', 'angular', 'next', 'nuxt', 'create-react-app']
        
        for package in packages:
            try:
                response = self.session.get(f"https://registry.npmjs.org/{package}")
                
                if response.status_code == 200:
                    data = response.json()
                    latest = data.get('dist-tags', {}).get('latest')
                    if latest:
                        version_data = data.get('versions', {}).get(latest, {})
                        actions.append({
                            'action_type': f"install_{package}",
                            'technology': package,
                            'complexity': 1,
                            'source': 'npm',
                            'usage_count': int(data.get('downloads', {}).get('last-day', 0)),
                            'package_name': package,
                            'version': latest,
                            'dependencies': version_data.get('dependencies', {}),
                            'description': version_data.get('description')
                        })
                        
            except Exception as e:
                logger.error(f"Ошибка NPM API для {package}: {e}")
                
        return actions
    
    def _collect_from_pypi(self) -> List[Dict[str, Any]]:
        """Сбор данных из PyPI"""
        actions = []
        
        # Популярные пакеты для API
        packages = ['fastapi', 'flask', 'django', 'uvicorn', 'gunicorn']
        
        for package in packages:
            try:
                response = self.session.get(f"https://pypi.org/pypi/{package}/json")
                
                if response.status_code == 200:
                    data = response.json()
                    info = data.get('info', {})
                    actions.append({
                        'action_type': f"install_{package}",
                        'technology': package,
                        'complexity': 1,
                        'source': 'pypi',
                        'usage_count': int(info.get('downloads', {}).get('last_day', 0)),
                        'package_name': package,
                        'version': info.get('version'),
                        'dependencies': info.get('requires_dist', []),
                        'description': info.get('summary')
                    })
                    
            except Exception as e:
                logger.error(f"Ошибка PyPI API для {package}: {e}")
                
        return actions
    
    def _collect_from_dockerhub(self) -> List[Dict[str, Any]]:
        """Сбор данных из Docker Hub"""
        actions = []
        
        # Популярные базовые образы
        images = ['node:alpine', 'python:alpine', 'golang:alpine', 'nginx:alpine']
        
        for image in images:
            try:
                # Docker Hub API (ограниченный доступ)
                response = self.session.get(f"https://hub.docker.com/v2/repositories/library/{image.split(':')[0]}")
                
                if response.status_code == 200:
                    data = response.json()
                    actions.append({
                        'action_type': f"use_base_image",
                        'technology': image.split(':')[0],
                        'complexity': 1,
                        'source': 'docker_hub',
                        'usage_count': data.get('pull_count', 0),
                        'image_name': image,
                        'description': data.get('description'),
                        'star_count': data.get('star_count', 0)
                    })
                    
            except Exception as e:
                logger.error(f"Ошибка Docker Hub API для {image}: {e}")
                
        return actions
    
    def _estimate_complexity(self, repo: Dict[str, Any]) -> int:
        """Оценка сложности репозитория"""
        complexity = 1
        
        # Факторы сложности
        if repo.get('language') in ['TypeScript', 'Rust', 'Go']:
            complexity += 1
        if repo.get('size', 0) > 1000:
            complexity += 1
        if repo.get('forks_count', 0) > 100:
            complexity += 1
            
        return min(complexity, 5)  # Максимум 5
    
    def _extract_spa_patterns(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Извлечение паттернов для SPA приложений"""
        patterns = []
        
        spa_actions = [a for a in actions if 'react' in a.get('technology', '').lower() or 'vue' in a.get('technology', '').lower()]
        
        if spa_actions:
            patterns.append({
                'name': 'basic_spa',
                'components': ['frontend', 'api', 'database'],
                'env_vars': ['REACT_APP_API_URL', 'REACT_APP_ENV'],
                'config_structure': {'frontend': {'build': 'dist'}, 'api': {'port': 8080}},
                'frequency': len(spa_actions)
            })
            
        return patterns
    
    def _extract_ssr_patterns(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Извлечение паттернов для SSR приложений"""
        patterns = []
        
        ssr_actions = [a for a in actions if 'next' in a.get('technology', '').lower() or 'nuxt' in a.get('technology', '').lower()]
        
        if ssr_actions:
            patterns.append({
                'name': 'basic_ssr',
                'components': ['frontend', 'api', 'database', 'cache'],
                'env_vars': ['NEXT_PUBLIC_API_URL', 'DATABASE_URL', 'REDIS_URL'],
                'config_structure': {'frontend': {'build': 'dist'}, 'api': {'port': 8080}, 'cache': {'ttl': 300}},
                'frequency': len(ssr_actions)
            })
            
        return patterns
    
    def _extract_api_patterns(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Извлечение паттернов для API приложений"""
        patterns = []
        
        api_actions = [a for a in actions if 'fastapi' in a.get('technology', '').lower() or 'flask' in a.get('technology', '').lower()]
        
        if api_actions:
            patterns.append({
                'name': 'basic_api',
                'components': ['api', 'database', 'auth'],
                'env_vars': ['DATABASE_URL', 'SECRET_KEY', 'CORS_ORIGINS'],
                'config_structure': {'api': {'port': 8080}, 'database': {'pool_size': 10}},
                'frequency': len(api_actions)
            })
            
        return patterns
    
    def _extract_microservice_patterns(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Извлечение паттернов для микросервисов"""
        patterns = []
        
        micro_actions = [a for a in actions if 'go' in a.get('technology', '').lower() or 'microservice' in a.get('action_type', '').lower()]
        
        if micro_actions:
            patterns.append({
                'name': 'basic_microservice',
                'components': ['service', 'database', 'message_queue'],
                'env_vars': ['SERVICE_PORT', 'DB_URL', 'MQ_URL'],
                'config_structure': {'service': {'port': 8080}, 'health': {'endpoint': '/healthz'}},
                'frequency': len(micro_actions)
            })
            
        return patterns
    
    def export(self, data: List[Dict[str, Any]], format: str = "csv", filename: str = None) -> str:
        """
        Экспортировать собранные данные в указанный формат
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_data_{timestamp}.{format}"
            
        filepath = self.config.get_data_path(filename)
        
        if format == "csv":
            if data:
                # Собираем все уникальные поля
                all_fields = set()
                for item in data:
                    all_fields.update(item.keys())
                
                # Очищаем данные от сложных объектов
                cleaned_data = []
                for item in data:
                    cleaned_item = {}
                    for field in all_fields:
                        value = item.get(field, '')
                        if isinstance(value, (dict, list)):
                            cleaned_item[field] = json.dumps(value)
                        else:
                            cleaned_item[field] = value
                    cleaned_data.append(cleaned_item)
                
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
                    writer.writeheader()
                    writer.writerows(cleaned_data)
                    
        elif format == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        elif format == "yaml":
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                
        logger.info(f"Данные экспортированы в {filepath}")
        return str(filepath) 