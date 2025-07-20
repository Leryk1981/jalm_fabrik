"""
Tool Candidate Generator - генератор tool_candidates

Преобразует найденный код в формат tool_candidates для JALM Full Stack,
создавая готовые к использованию инструменты.
"""

import json
import logging
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from .client import Context7Result
from .searcher import SearchQuery

logger = logging.getLogger(__name__)

@dataclass
class ToolCandidate:
    """Кандидат инструмента для JALM"""
    name: str
    description: str
    category: str
    language: str
    source_repo: str
    source_file: str
    function_name: str
    signature: str
    example_code: str
    license: str
    stars: int
    score: float
    metadata: Dict[str, Any]
    jalm_steps: List[Dict[str, Any]]

class ToolCandidateGenerator:
    """Генератор tool_candidates"""
    
    def __init__(self, output_dir: str = "tool_candidates"):
        """
        Инициализация генератора
        
        Args:
            output_dir: Директория для сохранения tool_candidates
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"ToolCandidateGenerator инициализирован: {self.output_dir}")
    
    def generate_candidate_name(self, action_name: str, function_name: str) -> str:
        """
        Генерация имени кандидата
        
        Args:
            action_name: Название действия
            function_name: Название функции
            
        Returns:
            Уникальное имя кандидата
        """
        # Очищаем и нормализуем имена
        clean_action = action_name.lower().replace(" ", "_").replace("-", "_")
        clean_function = function_name.lower().replace(" ", "_").replace("-", "_")
        
        # Создаем уникальное имя
        candidate_name = f"{clean_action}_{clean_function}"
        
        # Добавляем хеш для уникальности
        hash_suffix = hashlib.md5(f"{action_name}:{function_name}".encode()).hexdigest()[:8]
        candidate_name = f"{candidate_name}_{hash_suffix}"
        
        return candidate_name
    
    def determine_category(self, action_name: str, description: str) -> str:
        """
        Определение категории инструмента
        
        Args:
            action_name: Название действия
            description: Описание
            
        Returns:
            Категория инструмента
        """
        text = f"{action_name} {description}".lower()
        
        # Определяем категории по ключевым словам
        if any(word in text for word in ["booking", "schedule", "appointment", "slot"]):
            return "booking"
        elif any(word in text for word in ["payment", "billing", "invoice", "charge"]):
            return "payment"
        elif any(word in text for word in ["notification", "email", "sms", "push"]):
            return "notification"
        elif any(word in text for word in ["auth", "login", "register", "user"]):
            return "authentication"
        elif any(word in text for word in ["file", "upload", "download", "storage"]):
            return "file_management"
        elif any(word in text for word in ["api", "rest", "endpoint", "service"]):
            return "api_integration"
        else:
            return "utility"
    
    def extract_metadata(self, result: Context7Result, query: SearchQuery) -> Dict[str, Any]:
        """
        Извлечение метаданных из результата поиска
        
        Args:
            result: Результат поиска
            query: Исходный запрос
            
        Returns:
            Метаданные инструмента
        """
        metadata = {
            "source": {
                "repo": result.repo,
                "file": result.source_file,
                "url": result.url,
                "license": result.license,
                "stars": result.stars
            },
            "quality": {
                "score": result.score,
                "has_example": bool(result.example),
                "example_length": len(result.example) if result.example else 0
            },
            "search": {
                "query": query.description,
                "language": query.language,
                "expected_type": query.expected_type,
                "keywords": query.keywords
            },
            "generated_at": str(Path.cwd() / "context7_helper"),
            "version": "1.0.0"
        }
        
        return metadata
    
    def generate_jalm_steps(self, result: Context7Result, query: SearchQuery) -> List[Dict[str, Any]]:
        """
        Генерация JALM шагов из найденного кода
        
        Args:
            result: Результат поиска
            query: Исходный запрос
            
        Returns:
            Список JALM шагов
        """
        steps = []
        
        # Основной шаг вызова функции
        main_step = {
            "call_tool": result.function_name,
            "args": self._extract_arguments(result.signature),
            "source": result.repo,
            "description": f"Вызов функции {result.function_name} из {result.repo}",
            "example": result.example[:200] + "..." if len(result.example) > 200 else result.example
        }
        
        steps.append(main_step)
        
        # Дополнительные шаги в зависимости от типа
        if query.expected_type == "api":
            # Добавляем шаг для HTTP запроса
            http_step = {
                "call_tool": "http_request",
                "args": {
                    "method": "POST",
                    "url": "{{api_endpoint}}",
                    "headers": {"Content-Type": "application/json"},
                    "data": "{{request_data}}"
                },
                "source": "builtin",
                "description": "HTTP запрос к API"
            }
            steps.append(http_step)
        
        return steps
    
    def _extract_arguments(self, signature: str) -> Dict[str, Any]:
        """
        Извлечение аргументов из сигнатуры функции
        
        Args:
            signature: Сигнатура функции
            
        Returns:
            Словарь аргументов
        """
        args = {}
        
        try:
            # Простое извлечение аргументов из сигнатуры
            if "(" in signature and ")" in signature:
                params_str = signature.split("(")[1].split(")")[0]
                if params_str.strip():
                    params = [p.strip() for p in params_str.split(",")]
                    for param in params:
                        if "=" in param:
                            name, default = param.split("=", 1)
                            args[name.strip()] = default.strip()
                        else:
                            args[param.strip()] = "{{" + param.strip() + "}}"
        except Exception as e:
            logger.warning(f"Ошибка при извлечении аргументов: {e}")
            args = {"input": "{{input_data}}"}
        
        return args
    
    def create_candidate(self, result: Context7Result, query: SearchQuery) -> ToolCandidate:
        """
        Создание кандидата инструмента
        
        Args:
            result: Результат поиска
            query: Исходный запрос
            
        Returns:
            Кандидат инструмента
        """
        # Генерируем имя кандидата
        candidate_name = self.generate_candidate_name(query.action_name, result.function_name)
        
        # Определяем категорию
        category = self.determine_category(query.action_name, query.description)
        
        # Извлекаем метаданные
        metadata = self.extract_metadata(result, query)
        
        # Генерируем JALM шаги
        jalm_steps = self.generate_jalm_steps(result, query)
        
        # Создаем кандидата
        candidate = ToolCandidate(
            name=candidate_name,
            description=query.description,
            category=category,
            language=result.language,
            source_repo=result.repo,
            source_file=result.source_file,
            function_name=result.function_name,
            signature=result.signature,
            example_code=result.example,
            license=result.license,
            stars=result.stars,
            score=result.score,
            metadata=metadata,
            jalm_steps=jalm_steps
        )
        
        return candidate
    
    def save_candidate(self, candidate: ToolCandidate) -> str:
        """
        Сохранение кандидата в файл
        
        Args:
            candidate: Кандидат инструмента
            
        Returns:
            Путь к сохраненному файлу
        """
        # Создаем директорию для категории
        category_dir = self.output_dir / candidate.category
        category_dir.mkdir(exist_ok=True)
        
        # Путь к файлу
        file_path = category_dir / f"{candidate.name}.json"
        
        # Сохраняем в JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(candidate), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Кандидат сохранен: {file_path}")
        return str(file_path)
    
    def generate_from_results(self, results: List[Context7Result], query: SearchQuery) -> List[ToolCandidate]:
        """
        Генерация кандидатов из результатов поиска
        
        Args:
            results: Результаты поиска
            query: Исходный запрос
            
        Returns:
            Список кандидатов
        """
        candidates = []
        
        for result in results:
            try:
                candidate = self.create_candidate(result, query)
                candidates.append(candidate)
                logger.info(f"Создан кандидат: {candidate.name}")
            except Exception as e:
                logger.error(f"Ошибка при создании кандидата: {e}")
                continue
        
        return candidates
    
    def save_candidates(self, candidates: List[ToolCandidate]) -> List[str]:
        """
        Сохранение всех кандидатов
        
        Args:
            candidates: Список кандидатов
            
        Returns:
            Список путей к сохраненным файлам
        """
        saved_paths = []
        
        for candidate in candidates:
            try:
                file_path = self.save_candidate(candidate)
                saved_paths.append(file_path)
            except Exception as e:
                logger.error(f"Ошибка при сохранении кандидата {candidate.name}: {e}")
                continue
        
        logger.info(f"Сохранено {len(saved_paths)} кандидатов")
        return saved_paths
    
    def generate_index(self, candidates: List[ToolCandidate]) -> Dict[str, Any]:
        """
        Генерация индекса всех кандидатов
        
        Args:
            candidates: Список кандидатов
            
        Returns:
            Индекс кандидатов
        """
        index = {
            "metadata": {
                "total_candidates": len(candidates),
                "categories": {},
                "generated_at": str(Path.cwd() / "context7_helper"),
                "version": "1.0.0"
            },
            "candidates": {}
        }
        
        # Группируем по категориям
        for candidate in candidates:
            if candidate.category not in index["metadata"]["categories"]:
                index["metadata"]["categories"][candidate.category] = 0
            
            index["metadata"]["categories"][candidate.category] += 1
            
            # Добавляем кандидата в индекс
            index["candidates"][candidate.name] = {
                "name": candidate.name,
                "description": candidate.description,
                "category": candidate.category,
                "language": candidate.language,
                "score": candidate.score,
                "stars": candidate.stars,
                "license": candidate.license,
                "source_repo": candidate.source_repo
            }
        
        return index
    
    def save_index(self, index: Dict[str, Any]) -> str:
        """
        Сохранение индекса кандидатов
        
        Args:
            index: Индекс кандидатов
            
        Returns:
            Путь к сохраненному индексу
        """
        index_path = self.output_dir / "index.json"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Индекс сохранен: {index_path}")
        return str(index_path) 