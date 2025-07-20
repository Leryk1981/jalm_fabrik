#!/usr/bin/env python3
"""
Тест интеграции Context7 Helper с JALM Full Stack
"""

import sys
import os
from pathlib import Path

# Добавляем путь к context7_helper
sys.path.insert(0, str(Path(__file__).parent / "context7_helper"))

def test_context7_import():
    """Тест импорта Context7 Helper"""
    try:
        from context7_helper import Context7APIClient, CodeSearcher, ToolCandidateGenerator, IntegrationManager
        print("✅ Импорт Context7 Helper успешен")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта Context7 Helper: {e}")
        return False

def test_context7_cli():
    """Тест CLI Context7 Helper"""
    try:
        from context7_helper.cli import main
        print("✅ CLI Context7 Helper доступен")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта CLI: {e}")
        return False

def test_integration_manager():
    """Тест IntegrationManager"""
    try:
        from context7_helper import IntegrationManager
        
        # Создаем менеджер
        manager = IntegrationManager()
        
        # Проверяем статус
        status = manager.get_status()
        print(f"✅ IntegrationManager создан, статус: {status['context7_api']}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка IntegrationManager: {e}")
        return False

def test_search_functionality():
    """Тест функциональности поиска"""
    try:
        from context7_helper import CodeSearcher, SearchQuery
        from context7_helper.client import Context7APIClient
        
        # Создаем клиент (без API ключа для теста)
        client = Context7APIClient()
        
        # Создаем поисковик
        searcher = CodeSearcher(client)
        
        # Создаем тестовый запрос
        query = SearchQuery(
            action_name="test_search",
            description="Test search functionality",
            language="python"
        )
        
        # Тестируем построение запроса
        search_string = searcher.build_search_query(query)
        print(f"✅ Поисковый запрос построен: {search_string[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return False

def test_generator_functionality():
    """Тест функциональности генератора"""
    try:
        from context7_helper import ToolCandidateGenerator
        from context7_helper.client import Context7Result
        from context7_helper.searcher import SearchQuery
        
        # Создаем генератор
        generator = ToolCandidateGenerator(output_dir="test_candidates")
        
        # Создаем тестовый результат
        result = Context7Result(
            repo="test/repo",
            file_path="test.py",
            function_name="test_function",
            signature="def test_function():",
            example="def test_function():\n    pass",
            score=0.9,
            language="python",
            license="MIT",
            stars=100,
            description="Test function",
            url="https://github.com/test/repo"
        )
        
        # Создаем тестовый запрос
        query = SearchQuery(
            action_name="test_action",
            description="Test action",
            language="python"
        )
        
        # Тестируем создание кандидата
        candidate = generator.create_candidate(result, query)
        print(f"✅ Кандидат создан: {candidate.name}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка генератора: {e}")
        return False

def test_cli_commands():
    """Тест CLI команд"""
    try:
        import subprocess
        import sys
        
        # Тестируем команду status
        result = subprocess.run([
            sys.executable, "-m", "context7_helper.cli", "status"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI команда status работает")
            return True
        else:
            print(f"⚠️ CLI команда status вернула код {result.returncode}")
            print(f"Вывод: {result.stdout}")
            print(f"Ошибки: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка CLI команд: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование интеграции Context7 Helper")
    print("=" * 50)
    
    tests = [
        ("Импорт модулей", test_context7_import),
        ("CLI доступность", test_context7_cli),
        ("IntegrationManager", test_integration_manager),
        ("Функциональность поиска", test_search_functionality),
        ("Функциональность генератора", test_generator_functionality),
        ("CLI команды", test_cli_commands),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - ПРОЙДЕН")
            else:
                print(f"❌ {test_name} - ПРОВАЛЕН")
        except Exception as e:
            print(f"❌ {test_name} - ОШИБКА: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Context7 Helper интегрирован успешно!")
        return 0
    else:
        print("⚠️ Некоторые тесты не пройдены. Проверьте интеграцию.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 