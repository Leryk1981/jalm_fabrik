"""
Context7 API Client - клиент для работы с Context7 API

Обеспечивает поиск кода, получение метаданных и интеграцию
с системой поиска готовых реализаций.
"""

import os
import logging
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

@dataclass
class Context7Result:
    """Результат поиска в Context7"""
    repo: str
    file_path: str
    function_name: str
    signature: str
    example: str
    score: float
    language: str
    license: str
    stars: int
    description: str
    url: str

class Context7APIClient:
    """Клиент для работы с Context7 API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Инициализация клиента Context7
        
        Args:
            api_key: API ключ для Context7 (берется из CONTEXT7_API_KEY)
            base_url: Базовый URL API (по умолчанию http://localhost:4000/v1)
        """
        self.api_key = api_key or os.getenv("CONTEXT7_API_KEY", "")
        self.base_url = base_url or os.getenv("CONTEXT7_MCP_URL", "http://localhost:4000/v1")
        self.session = requests.Session()
        
        # Настройка заголовков
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
        
        logger.info(f"Context7APIClient инициализирован: {self.base_url}")
    
    def search_code(self, query: str, language: str = "python", top_k: int = 5) -> List[Context7Result]:
        """
        Поиск кода по запросу
        
        Args:
            query: Поисковый запрос
            language: Язык программирования
            top_k: Количество результатов
            
        Returns:
            Список результатов поиска
        """
        try:
            url = urljoin(self.base_url, "search")
            payload = {
                "query": query,
                "language": language,
                "top_k": top_k
            }
            
            logger.info(f"Поиск в Context7: {query}")
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            # Преобразование в Context7Result
            context7_results = []
            for item in results:
                result = Context7Result(
                    repo=item.get("repo", ""),
                    file_path=item.get("file_path", ""),
                    function_name=item.get("function_name", ""),
                    signature=item.get("signature", ""),
                    example=item.get("example", ""),
                    score=float(item.get("score", 0.0)),
                    language=item.get("language", language),
                    license=item.get("license", ""),
                    stars=int(item.get("stars", 0)),
                    description=item.get("description", ""),
                    url=item.get("url", "")
                )
                context7_results.append(result)
            
            logger.info(f"Найдено {len(context7_results)} результатов")
            return context7_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при поиске в Context7: {e}")
            return []
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return []
    
    def get_library_info(self, library_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение информации о библиотеке
        
        Args:
            library_id: ID библиотеки в формате /org/project
            
        Returns:
            Информация о библиотеке или None
        """
        try:
            url = urljoin(self.base_url, f"libraries/{library_id}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении информации о библиотеке {library_id}: {e}")
            return None
    
    def get_library_docs(self, library_id: str, topic: Optional[str] = None, tokens: int = 10000) -> Optional[str]:
        """
        Получение документации библиотеки
        
        Args:
            library_id: ID библиотеки
            topic: Тема документации
            tokens: Максимальное количество токенов
            
        Returns:
            Документация библиотеки или None
        """
        try:
            url = urljoin(self.base_url, "library-docs")
            payload = {
                "context7CompatibleLibraryID": library_id,
                "tokens": tokens
            }
            
            if topic:
                payload["topic"] = topic
            
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return data.get("documentation", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении документации {library_id}: {e}")
            return None
    
    def resolve_library(self, library_name: str) -> Optional[str]:
        """
        Разрешение имени библиотеки в ID
        
        Args:
            library_name: Название библиотеки
            
        Returns:
            ID библиотеки или None
        """
        try:
            url = urljoin(self.base_url, "resolve-library-id")
            payload = {"libraryName": library_name}
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get("libraryId")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при разрешении библиотеки {library_name}: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Проверка доступности Context7 API
        
        Returns:
            True если API доступен, False иначе
        """
        try:
            url = urljoin(self.base_url, "health")
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False 