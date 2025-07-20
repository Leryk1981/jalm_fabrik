"""
Integration Manager - интеграция Context7 Helper с JALM Full Stack

Обеспечивает интеграцию с Research Layer, CLI и другими компонентами
JALM Full Stack для автоматического поиска и генерации tool_candidates.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from .client import Context7APIClient
from .searcher import CodeSearcher, SearchQuery
from .generator import ToolCandidateGenerator, ToolCandidate

logger = logging.getLogger(__name__)

class IntegrationManager:
    """Менеджер интеграции Context7 Helper"""
    
    def __init__(self, api_key: Optional[str] = None, output_dir: str = "tool_candidates"):
        """
        Инициализация менеджера интеграции
        
        Args:
            api_key: API ключ для Context7
            output_dir: Директория для сохранения результатов
        """
        self.client = Context7APIClient(api_key)
        self.searcher = CodeSearcher(self.client)
        self.generator = ToolCandidateGenerator(output_dir)
        
        logger.info("IntegrationManager инициализирован")
    
    def load_research_data(self, research_dir: str = "research") -> List[Dict[str, Any]]:
        """
        Загрузка данных из Research Layer
        
        Args:
            research_dir: Директория с данными исследований
            
        Returns:
            Список действий для поиска
        """
        actions = []
        research_path = Path(research_dir)
        
        # Загружаем raw_actions.csv
        raw_actions_path = research_path / "raw_actions.csv"
        if raw_actions_path.exists():
            try:
                import csv
                with open(raw_actions_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        actions.append({
                            "action_id": row.get("action_id", ""),
                            "actor": row.get("actor", ""),
                            "source": row.get("source", ""),
                            "freq": row.get("freq", ""),
                            "blocker": row.get("blocker", "")
                        })
                logger.info(f"Загружено {len(actions)} действий из raw_actions.csv")
            except Exception as e:
                logger.error(f"Ошибка при загрузке raw_actions.csv: {e}")
        
        # Загружаем grouped.json
        grouped_path = research_path / "grouped.json"
        if grouped_path.exists():
            try:
                with open(grouped_path, 'r', encoding='utf-8') as f:
                    grouped_data = json.load(f)
                    # Добавляем группированные данные
                    for group in grouped_data.get("groups", []):
                        for action in group.get("actions", []):
                            actions.append({
                                "action_id": action.get("name", ""),
                                "actor": action.get("actor", ""),
                                "source": "grouped",
                                "freq": action.get("frequency", ""),
                                "blocker": action.get("blocker", ""),
                                "group": group.get("name", "")
                            })
                logger.info(f"Загружено {len(actions)} действий из grouped.json")
            except Exception as e:
                logger.error(f"Ошибка при загрузке grouped.json: {e}")
        
        return actions
    
    def convert_to_search_queries(self, actions: List[Dict[str, Any]]) -> List[SearchQuery]:
        """
        Преобразование действий в поисковые запросы
        
        Args:
            actions: Список действий
            
        Returns:
            Список поисковых запросов
        """
        queries = []
        
        for action in actions:
            action_id = action.get("action_id", "")
            actor = action.get("actor", "")
            source = action.get("source", "")
            
            # Определяем тип ожидаемого результата
            expected_type = "function"
            if "api" in action_id.lower() or "endpoint" in action_id.lower():
                expected_type = "api"
            elif "cli" in action_id.lower() or "command" in action_id.lower():
                expected_type = "cli"
            
            # Определяем приоритетные технологии
            priority_technologies = ["python", "fastapi"]
            if expected_type == "api":
                priority_technologies.extend(["flask", "django"])
            elif expected_type == "cli":
                priority_technologies.extend(["argparse", "click"])
            
            # Создаем поисковый запрос
            query = SearchQuery(
                action_name=action_id,
                description=f"{action_id} for {actor} from {source}",
                language="python",
                priority_technologies=priority_technologies,
                expected_type=expected_type,
                keywords=[action_id, actor, source]
            )
            
            queries.append(query)
        
        logger.info(f"Создано {len(queries)} поисковых запросов")
        return queries
    
    def search_and_generate(self, queries: List[SearchQuery], top_k: int = 3) -> List[ToolCandidate]:
        """
        Поиск и генерация кандидатов
        
        Args:
            queries: Список поисковых запросов
            top_k: Количество результатов на запрос
            
        Returns:
            Список сгенерированных кандидатов
        """
        all_candidates = []
        
        for i, query in enumerate(queries):
            logger.info(f"Обработка запроса {i+1}/{len(queries)}: {query.action_name}")
            
            try:
                # Поиск кода
                results = self.searcher.search(query, top_k)
                
                if not results:
                    logger.warning(f"Не найдено результатов для {query.action_name}")
                    continue
                
                # Генерация кандидатов
                candidates = self.generator.generate_from_results(results, query)
                all_candidates.extend(candidates)
                
                logger.info(f"Создано {len(candidates)} кандидатов для {query.action_name}")
                
            except Exception as e:
                logger.error(f"Ошибка при обработке запроса {query.action_name}: {e}")
                continue
        
        logger.info(f"Всего создано {len(all_candidates)} кандидатов")
        return all_candidates
    
    def save_results(self, candidates: List[ToolCandidate]) -> Dict[str, str]:
        """
        Сохранение результатов
        
        Args:
            candidates: Список кандидатов
            
        Returns:
            Словарь с путями к сохраненным файлам
        """
        saved_files = {}
        
        # Сохраняем кандидатов
        candidate_paths = self.generator.save_candidates(candidates)
        saved_files["candidates"] = candidate_paths
        
        # Генерируем и сохраняем индекс
        index = self.generator.generate_index(candidates)
        index_path = self.generator.save_index(index)
        saved_files["index"] = index_path
        
        return saved_files
    
    def run_full_pipeline(self, research_dir: str = "research", top_k: int = 3) -> Dict[str, Any]:
        """
        Запуск полного пайплайна поиска и генерации
        
        Args:
            research_dir: Директория с данными исследований
            top_k: Количество результатов на запрос
            
        Returns:
            Результаты выполнения пайплайна
        """
        logger.info("Запуск полного пайплайна Context7 Helper")
        
        try:
            # 1. Загрузка данных из Research Layer
            actions = self.load_research_data(research_dir)
            
            if not actions:
                logger.warning("Не найдено данных для обработки")
                return {"success": False, "error": "Нет данных для обработки"}
            
            # 2. Преобразование в поисковые запросы
            queries = self.convert_to_search_queries(actions)
            
            # 3. Поиск и генерация кандидатов
            candidates = self.search_and_generate(queries, top_k)
            
            if not candidates:
                logger.warning("Не создано кандидатов")
                return {"success": False, "error": "Не создано кандидатов"}
            
            # 4. Сохранение результатов
            saved_files = self.save_results(candidates)
            
            # 5. Формирование отчета
            report = {
                "success": True,
                "processed_actions": len(actions),
                "search_queries": len(queries),
                "generated_candidates": len(candidates),
                "saved_files": saved_files,
                "categories": {}
            }
            
            # Статистика по категориям
            for candidate in candidates:
                category = candidate.category
                if category not in report["categories"]:
                    report["categories"][category] = 0
                report["categories"][category] += 1
            
            logger.info(f"Пайплайн завершен успешно: {len(candidates)} кандидатов")
            return report
            
        except Exception as e:
            logger.error(f"Ошибка в пайплайне: {e}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Получение статуса Context7 Helper
        
        Returns:
            Статус системы
        """
        status = {
            "context7_api": self.client.health_check(),
            "output_directory": str(self.generator.output_dir),
            "output_directory_exists": self.generator.output_dir.exists(),
            "candidates_count": 0,
            "categories": {}
        }
        
        # Подсчет кандидатов
        if self.generator.output_dir.exists():
            for category_dir in self.generator.output_dir.iterdir():
                if category_dir.is_dir():
                    category_name = category_dir.name
                    candidate_count = len(list(category_dir.glob("*.json")))
                    status["categories"][category_name] = candidate_count
                    status["candidates_count"] += candidate_count
        
        return status
    
    def cleanup_old_candidates(self, days: int = 7) -> int:
        """
        Очистка старых кандидатов
        
        Args:
            days: Количество дней для хранения
            
        Returns:
            Количество удаленных файлов
        """
        import time
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        if self.generator.output_dir.exists():
            for json_file in self.generator.output_dir.rglob("*.json"):
                try:
                    file_time = datetime.fromtimestamp(json_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        json_file.unlink()
                        deleted_count += 1
                        logger.info(f"Удален старый файл: {json_file}")
                except Exception as e:
                    logger.error(f"Ошибка при удалении {json_file}: {e}")
        
        logger.info(f"Удалено {deleted_count} старых файлов")
        return deleted_count 