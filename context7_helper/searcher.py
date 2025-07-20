"""
Code Searcher - поисковик кода с фильтрацией и оценкой

Обеспечивает интеллектуальный поиск кода с фильтрацией по лицензиям,
качеству и релевантности для JALM Full Stack.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .client import Context7APIClient, Context7Result

logger = logging.getLogger(__name__)

@dataclass
class SearchQuery:
    """Поисковый запрос"""
    action_name: str
    description: str
    language: str = "python"
    priority_technologies: List[str] = None
    expected_type: str = "function"  # function, api, cli, endpoint
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.priority_technologies is None:
            self.priority_technologies = ["python", "fastapi", "flask"]
        if self.keywords is None:
            self.keywords = []

class CodeSearcher:
    """Поисковик кода с фильтрацией"""
    
    # Разрешенные лицензии
    ALLOWED_LICENSES = {
        "mit", "apache-2.0", "apache2", "apache 2.0", 
        "bsd-3-clause", "bsd-2-clause", "isc", "unlicense"
    }
    
    # Минимальное количество звезд
    MIN_STARS = 50
    
    def __init__(self, client: Context7APIClient):
        """
        Инициализация поисковика
        
        Args:
            client: Клиент Context7 API
        """
        self.client = client
        logger.info("CodeSearcher инициализирован")
    
    def build_search_query(self, query: SearchQuery) -> str:
        """
        Построение поискового запроса для Context7
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Оптимизированная поисковая строка
        """
        # Базовые ключевые слова
        keywords = [query.action_name, query.description]
        
        # Добавляем приоритетные технологии
        keywords.extend(query.priority_technologies)
        
        # Добавляем пользовательские ключевые слова
        keywords.extend(query.keywords)
        
        # Добавляем тип ожидаемого результата
        if query.expected_type == "function":
            keywords.extend(["function", "def", "python"])
        elif query.expected_type == "api":
            keywords.extend(["api", "endpoint", "route", "fastapi", "flask"])
        elif query.expected_type == "cli":
            keywords.extend(["cli", "command", "argparse", "click"])
        
        # Убираем дубликаты и объединяем
        unique_keywords = list(set(keywords))
        search_query = " ".join(unique_keywords)
        
        logger.info(f"Построен поисковый запрос: {search_query}")
        return search_query
    
    def filter_results(self, results: List[Context7Result]) -> List[Context7Result]:
        """
        Фильтрация результатов по качеству
        
        Args:
            results: Список результатов поиска
            
        Returns:
            Отфильтрованные результаты
        """
        filtered = []
        
        for result in results:
            # Проверка лицензии
            license_name = (result.license or "").lower()
            if license_name not in self.ALLOWED_LICENSES:
                logger.debug(f"Пропущен результат с лицензией: {license_name}")
                continue
            
            # Проверка количества звезд
            if result.stars < self.MIN_STARS:
                logger.debug(f"Пропущен результат с {result.stars} звездами")
                continue
            
            # Проверка наличия функции
            if not result.function_name:
                logger.debug("Пропущен результат без имени функции")
                continue
            
            # Проверка примера кода
            if not result.example or len(result.example.strip()) < 10:
                logger.debug("Пропущен результат без примера кода")
                continue
            
            filtered.append(result)
        
        logger.info(f"Отфильтровано {len(filtered)} из {len(results)} результатов")
        return filtered
    
    def score_results(self, results: List[Context7Result], query: SearchQuery) -> List[Context7Result]:
        """
        Оценка и сортировка результатов
        
        Args:
            results: Список результатов
            query: Исходный запрос
            
        Returns:
            Отсортированные результаты
        """
        scored_results = []
        
        for result in results:
            score = result.score  # Базовый скор от Context7
            
            # Бонус за популярность
            if result.stars > 1000:
                score += 0.2
            elif result.stars > 500:
                score += 0.1
            elif result.stars > 100:
                score += 0.05
            
            # Бонус за релевантность технологий
            for tech in query.priority_technologies:
                if tech.lower() in result.description.lower():
                    score += 0.1
                if tech.lower() in result.example.lower():
                    score += 0.15
            
            # Бонус за качество примера
            if len(result.example) > 100:
                score += 0.1
            
            # Бонус за MIT лицензию
            if result.license.lower() == "mit":
                score += 0.05
            
            # Создаем новый результат с обновленным скором
            updated_result = Context7Result(
                repo=result.repo,
                file_path=result.file_path,
                function_name=result.function_name,
                signature=result.signature,
                example=result.example,
                score=min(score, 1.0),  # Ограничиваем скор до 1.0
                language=result.language,
                license=result.license,
                stars=result.stars,
                description=result.description,
                url=result.url
            )
            
            scored_results.append(updated_result)
        
        # Сортировка по скору
        scored_results.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"Оценено и отсортировано {len(scored_results)} результатов")
        return scored_results
    
    def search(self, query: SearchQuery, top_k: int = 5) -> List[Context7Result]:
        """
        Полноценный поиск кода
        
        Args:
            query: Поисковый запрос
            top_k: Количество результатов
            
        Returns:
            Отсортированные результаты поиска
        """
        try:
            # Проверка доступности API
            if not self.client.health_check():
                logger.error("Context7 API недоступен")
                return []
            
            # Построение поискового запроса
            search_string = self.build_search_query(query)
            
            # Поиск в Context7
            raw_results = self.client.search_code(
                query=search_string,
                language=query.language,
                top_k=top_k * 2  # Ищем больше для фильтрации
            )
            
            if not raw_results:
                logger.warning("Не найдено результатов в Context7")
                return []
            
            # Фильтрация результатов
            filtered_results = self.filter_results(raw_results)
            
            if not filtered_results:
                logger.warning("Нет результатов после фильтрации")
                return []
            
            # Оценка и сортировка
            scored_results = self.score_results(filtered_results, query)
            
            # Возвращаем топ результаты
            return scored_results[:top_k]
            
        except Exception as e:
            logger.error(f"Ошибка при поиске кода: {e}")
            return []
    
    def search_multiple(self, queries: List[SearchQuery], top_k: int = 3) -> Dict[str, List[Context7Result]]:
        """
        Поиск по нескольким запросам
        
        Args:
            queries: Список поисковых запросов
            top_k: Количество результатов на запрос
            
        Returns:
            Словарь результатов по запросам
        """
        results = {}
        
        for query in queries:
            logger.info(f"Поиск для действия: {query.action_name}")
            query_results = self.search(query, top_k)
            results[query.action_name] = query_results
        
        return results 