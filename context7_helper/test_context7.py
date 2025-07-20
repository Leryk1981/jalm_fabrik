"""
Тесты для Context7 Helper

Проверка функциональности поиска кода, генерации кандидатов
и интеграции с JALM Full Stack.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Импорт модулей для тестирования
from .client import Context7APIClient, Context7Result
from .searcher import CodeSearcher, SearchQuery
from .generator import ToolCandidateGenerator, ToolCandidate
from .integration import IntegrationManager

class TestContext7APIClient(unittest.TestCase):
    """Тесты для Context7APIClient"""
    
    def setUp(self):
        """Настройка тестов"""
        self.client = Context7APIClient(api_key="test_key")
    
    @patch('requests.Session.post')
    def test_search_code_success(self, mock_post):
        """Тест успешного поиска кода"""
        # Мокаем ответ API
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "repo": "test/repo",
                    "file_path": "test.py",
                    "function_name": "test_function",
                    "signature": "def test_function():",
                    "example": "def test_function():\n    pass",
                    "score": 0.9,
                    "language": "python",
                    "license": "MIT",
                    "stars": 100,
                    "description": "Test function",
                    "url": "https://github.com/test/repo"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Выполняем поиск
        results = self.client.search_code("test query", "python", 5)
        
        # Проверяем результаты
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].function_name, "test_function")
        self.assertEqual(results[0].repo, "test/repo")
        self.assertEqual(results[0].score, 0.9)
    
    @patch('requests.Session.post')
    def test_search_code_error(self, mock_post):
        """Тест обработки ошибки при поиске"""
        mock_post.side_effect = Exception("API Error")
        
        results = self.client.search_code("test query")
        self.assertEqual(len(results), 0)

class TestCodeSearcher(unittest.TestCase):
    """Тесты для CodeSearcher"""
    
    def setUp(self):
        """Настройка тестов"""
        self.client = Mock()
        self.searcher = CodeSearcher(self.client)
    
    def test_build_search_query(self):
        """Тест построения поискового запроса"""
        query = SearchQuery(
            action_name="booking_system",
            description="Create a booking system",
            language="python",
            priority_technologies=["fastapi", "sqlalchemy"],
            expected_type="api",
            keywords=["booking", "appointment"]
        )
        
        search_string = self.searcher.build_search_query(query)
        
        # Проверяем, что все ключевые слова присутствуют
        self.assertIn("booking_system", search_string)
        self.assertIn("fastapi", search_string)
        self.assertIn("sqlalchemy", search_string)
        self.assertIn("api", search_string)
    
    def test_filter_results(self):
        """Тест фильтрации результатов"""
        # Создаем тестовые результаты
        results = [
            Context7Result(
                repo="test/repo1",
                file_path="test1.py",
                function_name="func1",
                signature="def func1():",
                example="def func1():\n    pass",
                score=0.9,
                language="python",
                license="MIT",
                stars=100,
                description="Test function 1",
                url="https://github.com/test/repo1"
            ),
            Context7Result(
                repo="test/repo2",
                file_path="test2.py",
                function_name="func2",
                signature="def func2():",
                example="def func2():\n    pass",
                score=0.8,
                language="python",
                license="proprietary",  # Неразрешенная лицензия
                stars=50,
                description="Test function 2",
                url="https://github.com/test/repo2"
            ),
            Context7Result(
                repo="test/repo3",
                file_path="test3.py",
                function_name="",  # Пустое имя функции
                signature="def func3():",
                example="def func3():\n    pass",
                score=0.7,
                language="python",
                license="MIT",
                stars=200,
                description="Test function 3",
                url="https://github.com/test/repo3"
            )
        ]
        
        filtered = self.searcher.filter_results(results)
        
        # Должен остаться только первый результат
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].function_name, "func1")

class TestToolCandidateGenerator(unittest.TestCase):
    """Тесты для ToolCandidateGenerator"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ToolCandidateGenerator(self.temp_dir)
    
    def tearDown(self):
        """Очистка после тестов"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_generate_candidate_name(self):
        """Тест генерации имени кандидата"""
        name = self.generator.generate_candidate_name("booking system", "create_booking")
        self.assertIn("booking_system", name)
        self.assertIn("create_booking", name)
        self.assertIn("_", name)  # Должен содержать хеш
    
    def test_determine_category(self):
        """Тест определения категории"""
        # Тестируем различные категории
        self.assertEqual(
            self.generator.determine_category("booking", "schedule appointment"),
            "booking"
        )
        self.assertEqual(
            self.generator.determine_category("payment", "process payment"),
            "payment"
        )
        self.assertEqual(
            self.generator.determine_category("unknown", "some function"),
            "utility"
        )
    
    def test_create_candidate(self):
        """Тест создания кандидата"""
        result = Context7Result(
            repo="test/repo",
            file_path="booking.py",
            function_name="create_booking",
            signature="def create_booking(user_id: int, slot_id: int) -> dict:",
            example="def create_booking(user_id, slot_id):\n    return {'status': 'success'}",
            score=0.9,
            language="python",
            license="MIT",
            stars=150,
            description="Create a booking",
            url="https://github.com/test/repo"
        )
        
        query = SearchQuery(
            action_name="booking_system",
            description="Create a booking system",
            language="python"
        )
        
        candidate = self.generator.create_candidate(result, query)
        
        self.assertIsInstance(candidate, ToolCandidate)
        self.assertIn("booking_system", candidate.name)
        self.assertEqual(candidate.category, "booking")
        self.assertEqual(candidate.language, "python")
        self.assertEqual(len(candidate.jalm_steps), 1)
    
    def test_save_candidate(self):
        """Тест сохранения кандидата"""
        candidate = ToolCandidate(
            name="test_candidate",
            description="Test candidate",
            category="test",
            language="python",
            source_repo="test/repo",
            source_file="test.py",
            function_name="test_func",
            signature="def test_func():",
            example_code="def test_func():\n    pass",
            license="MIT",
            stars=100,
            score=0.9,
            metadata={},
            jalm_steps=[]
        )
        
        file_path = self.generator.save_candidate(candidate)
        
        # Проверяем, что файл создан
        self.assertTrue(Path(file_path).exists())
        
        # Проверяем содержимое
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(data["name"], "test_candidate")
        self.assertEqual(data["category"], "test")

class TestIntegrationManager(unittest.TestCase):
    """Тесты для IntegrationManager"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = IntegrationManager(output_dir=self.temp_dir)
    
    def tearDown(self):
        """Очистка после тестов"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch.object(IntegrationManager, 'load_research_data')
    @patch.object(IntegrationManager, 'convert_to_search_queries')
    @patch.object(IntegrationManager, 'search_and_generate')
    @patch.object(IntegrationManager, 'save_results')
    def test_run_full_pipeline_success(self, mock_save, mock_search, mock_convert, mock_load):
        """Тест успешного выполнения полного пайплайна"""
        # Мокаем методы
        mock_load.return_value = [{"action_id": "test_action"}]
        mock_convert.return_value = [SearchQuery("test", "test", "python")]
        mock_search.return_value = [Mock()]  # Mock кандидат
        mock_save.return_value = {"candidates": ["test.json"], "index": "index.json"}
        
        result = self.manager.run_full_pipeline("research", 3)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["processed_actions"], 1)
        self.assertEqual(result["search_queries"], 1)
        self.assertEqual(result["generated_candidates"], 1)
    
    def test_get_status(self):
        """Тест получения статуса"""
        status = self.manager.get_status()
        
        self.assertIn("context7_api", status)
        self.assertIn("output_directory", status)
        self.assertIn("candidates_count", status)
        self.assertIn("categories", status)

if __name__ == '__main__':
    unittest.main() 