#!/usr/bin/env python3
"""
Оффлайн тестирование JALM Full Stack
Проверяет функции без запуска серверов
"""

import sys
import json
from pathlib import Path

def test_tula_spec_functions():
    """Тест функций Tula Spec"""
    print("=== Тест функций Tula Spec ===")
    
    # Добавляем путь к функциям
    sys.path.append(str(Path("tula_spec/functions")))
    
    try:
        # Тест slot_validator
        from slot_validator import create, _validate_input
        
        test_slot = {
            "slot": {
                "datetime": "2024-06-15T10:00:00Z",
                "duration": 60,
                "service_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
        
        result = create(test_slot)
        print(f"✅ slot_validator.create(): {result['status']}")
        
        # Тест booking_widget
        from booking_widget import create as create_widget
        
        widget_result = create_widget("123e4567-e89b-12d3-a456-426614174000", "user-123")
        print(f"✅ booking_widget.create(): {widget_result['widget_id'][:8]}...")
        
        # Тест notify_system
        from notify_system import send
        
        notify_result = send("Тестовое уведомление", "web", "test@example.com", "test")
        print(f"✅ notify_system.send(): {notify_result['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования функций: {e}")
        return False

def test_shablon_spec_templates():
    """Тест шаблонов Shablon Spec"""
    print("\n=== Тест шаблонов Shablon Spec ===")
    
    # Добавляем путь к API
    sys.path.append(str(Path("shablon_spec/api")))
    
    try:
        from main import validate_jalm_syntax, generate_hash, load_registry
        
        # Тест загрузки реестра
        registry = load_registry()
        print(f"✅ Реестр загружен: {registry['metadata']['total_templates']} шаблонов")
        
        # Тест валидации шаблонов
        templates_dir = Path("shablon_spec/templates")
        
        for template_file in templates_dir.glob("*.jalm"):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            validation = validate_jalm_syntax(content)
            print(f"✅ {template_file.name}: {'валиден' if validation.is_valid else 'невалиден'}")
            
            if validation.errors:
                print(f"   Ошибки: {validation.errors}")
            
            # Тест генерации хеша
            hash_value = generate_hash(content)
            print(f"   Хеш: {hash_value[:8]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования шаблонов: {e}")
        return False

def test_core_runner_components():
    """Тест компонентов Core Runner"""
    print("\n=== Тест компонентов Core Runner ===")
    
    try:
        # Проверяем наличие файлов
        core_files = [
            "core-runner/kernel/src/main.py",
            "core-runner/Makefile",
            "catalog/core-runner.engine.json"
        ]
        
        for file_path in core_files:
            if Path(file_path).exists():
                print(f"✅ {file_path} существует")
            else:
                print(f"❌ {file_path} не найден")
                return False
        
        # Проверяем структуру каталогов
        core_dirs = [
            "core-runner/kernel/src",
            "core-runner/cfg",
            "core-runner/state-store"
        ]
        
        for dir_path in core_dirs:
            if Path(dir_path).exists():
                print(f"✅ {dir_path} существует")
            else:
                print(f"❌ {dir_path} не найден")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Core Runner: {e}")
        return False

def test_project_structure():
    """Тест структуры проекта"""
    print("\n=== Тест структуры проекта ===")
    
    try:
        # Проверяем основные компоненты
        components = [
            "core-runner",
            "tula_spec", 
            "shablon_spec",
            "catalog",
            "FINAL_SPECIFICATION.md"
        ]
        
        for component in components:
            if Path(component).exists():
                print(f"✅ {component} существует")
            else:
                print(f"❌ {component} не найден")
                return False
        
        # Проверяем отчеты
        reports = [
            "TULA_SPEC_REPORT.md",
            "SHABLON_SPEC_REPORT.md", 
            "JALM_FULL_STACK_COMPLETE.md"
        ]
        
        for report in reports:
            if Path(report).exists():
                print(f"✅ {report} существует")
            else:
                print(f"❌ {report} не найден")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования структуры: {e}")
        return False

def main():
    """Основная функция"""
    print("🧪 Оффлайн тестирование JALM Full Stack")
    print("=" * 50)
    
    results = {}
    
    # Тест структуры проекта
    results["project_structure"] = test_project_structure()
    
    # Тест компонентов Core Runner
    results["core_runner"] = test_core_runner_components()
    
    # Тест функций Tula Spec
    results["tula_spec"] = test_tula_spec_functions()
    
    # Тест шаблонов Shablon Spec
    results["shablon_spec"] = test_shablon_spec_templates()
    
    # Итоговый отчет
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ОФФЛАЙН ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📈 РЕЗУЛЬТАТ:")
    print(f"  Всего тестов: {total_tests}")
    print(f"  Пройдено: {passed_tests}")
    print(f"  Провалено: {total_tests - passed_tests}")
    
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"  Успешность: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("  🎉 ОТЛИЧНО! Все компоненты готовы к запуску!")
        elif success_rate >= 75:
            print("  ✅ ХОРОШО! Большинство компонентов готовы.")
        else:
            print("  ⚠️ ТРЕБУЕТ ВНИМАНИЯ! Есть проблемы с компонентами.")
    
    # Сохранение результатов
    with open("offline_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Результаты сохранены в offline_test_results.json")

if __name__ == "__main__":
    main() 