#!/usr/bin/env python3
"""
Простой тест для JALM CLI
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_cli_imports():
    """Тест импортов CLI"""
    try:
        import cli
        print("✅ CLI модуль импортирован успешно")
        
        from cli.core.config import Config
        print("✅ Config класс импортирован успешно")
        
        from cli.utils.logger import setup_logger
        print("✅ Logger функция импортирована успешно")
        
        from cli.commands import up, down, status, logs, test, deploy
        print("✅ Все команды импортированы успешно")
        
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    try:
        from cli.core.config import Config
        
        config = Config()
        print("✅ Конфигурация создана успешно")
        
        # Проверяем основные настройки
        services = config.config.get('services', {})
        if 'core-runner' in services:
            print("✅ Конфигурация core-runner найдена")
        else:
            print("❌ Конфигурация core-runner не найдена")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def test_logger():
    """Тест логирования"""
    try:
        from cli.utils.logger import setup_logger
        
        logger = setup_logger(debug=True)
        print("✅ Логгер создан успешно")
        
        logger.info("Тестовое сообщение")
        logger.debug("Отладочное сообщение")
        print("✅ Логирование работает")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка логирования: {e}")
        return False

def test_commands():
    """Тест команд"""
    try:
        from cli.core.config import Config
        from cli.utils.logger import setup_logger
        from cli.commands import status
        
        config = Config()
        logger = setup_logger(debug=False)
        
        # Тестируем команду status
        result = status.run(verbose=False, config=config, logger=logger)
        print("✅ Команда status выполнена")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка команд: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🧪 Тестирование JALM CLI")
    print("=" * 40)
    
    tests = [
        ("Импорты", test_cli_imports),
        ("Конфигурация", test_config),
        ("Логирование", test_logger),
        ("Команды", test_commands),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                print(f"✅ {test_name} - ПРОЙДЕН")
                passed += 1
            else:
                print(f"❌ {test_name} - ПРОВАЛЕН")
                failed += 1
        except Exception as e:
            print(f"💥 {test_name} - ОШИБКА: {e}")
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Результаты тестирования:")
    print(f"   ✅ Пройдено: {passed}")
    print(f"   ❌ Провалено: {failed}")
    print(f"   📈 Всего: {passed + failed}")
    
    if failed == 0:
        print("🎉 Все тесты прошли успешно!")
        return 0
    else:
        print("⚠️  Некоторые тесты не прошли")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 