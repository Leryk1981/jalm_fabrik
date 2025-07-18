#!/usr/bin/env python3
"""
Тест импорта API модулей JALM Full Stack
"""

import sys
from pathlib import Path

def test_tula_spec_api_import():
    """Тест импорта Tula Spec API"""
    print("=== Тест импорта Tula Spec API ===")
    
    try:
        # Добавляем путь к API
        sys.path.append(str(Path("tula_spec/api")))
        
        # Импортируем модуль
        import main as tula_api
        
        print("✅ Tula Spec API импортирован успешно")
        
        # Проверяем наличие основных функций
        if hasattr(tula_api, 'app'):
            print("✅ FastAPI приложение найдено")
        else:
            print("❌ FastAPI приложение не найдено")
            return False
        
        if hasattr(tula_api, 'load_registry'):
            print("✅ Функция load_registry найдена")
        else:
            print("❌ Функция load_registry не найдена")
            return False
        
        if hasattr(tula_api, 'load_function'):
            print("✅ Функция load_function найдена")
        else:
            print("❌ Функция load_function не найдена")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта Tula Spec API: {e}")
        return False

def test_shablon_spec_api_import():
    """Тест импорта Shablon Spec API"""
    print("\n=== Тест импорта Shablon Spec API ===")
    
    try:
        # Добавляем путь к API
        sys.path.append(str(Path("shablon_spec/api")))
        
        # Импортируем модуль
        import main as shablon_api
        
        print("✅ Shablon Spec API импортирован успешно")
        
        # Проверяем наличие основных функций
        if hasattr(shablon_api, 'app'):
            print("✅ FastAPI приложение найдено")
        else:
            print("❌ FastAPI приложение не найдено")
            return False
        
        if hasattr(shablon_api, 'load_registry'):
            print("✅ Функция load_registry найдена")
        else:
            print("❌ Функция load_registry не найдена")
            return False
        
        if hasattr(shablon_api, 'validate_jalm_syntax'):
            print("✅ Функция validate_jalm_syntax найдена")
        else:
            print("❌ Функция validate_jalm_syntax не найдена")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта Shablon Spec API: {e}")
        return False

def test_core_runner_import():
    """Тест импорта Core Runner"""
    print("\n=== Тест импорта Core Runner ===")
    
    try:
        # Добавляем путь к kernel
        sys.path.append(str(Path("core-runner/kernel/src")))
        
        # Импортируем модуль
        import main as core_runner
        
        print("✅ Core Runner импортирован успешно")
        
        # Проверяем наличие основных функций
        if hasattr(core_runner, 'execute_jalm'):
            print("✅ Функция execute_jalm найдена")
        else:
            print("❌ Функция execute_jalm не найдена")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта Core Runner: {e}")
        return False

def test_requirements_files():
    """Тест файлов requirements"""
    print("\n=== Тест файлов requirements ===")
    
    requirements_files = [
        "core-runner/requirements.txt",
        "tula_spec/requirements.txt",
        "shablon_spec/requirements.txt"
    ]
    
    all_exist = True
    
    for req_file in requirements_files:
        if Path(req_file).exists():
            print(f"✅ {req_file} существует")
            
            # Проверяем содержимое
            with open(req_file, 'r') as f:
                content = f.read()
                if 'fastapi' in content.lower():
                    print(f"   ✅ Содержит FastAPI")
                else:
                    print(f"   ⚠️ Не содержит FastAPI")
        else:
            print(f"❌ {req_file} не найден")
            all_exist = False
    
    return all_exist

def test_dockerfiles():
    """Тест Dockerfile"""
    print("\n=== Тест Dockerfile ===")
    
    dockerfiles = [
        "core-runner/kernel/Dockerfile",
        "tula_spec/Dockerfile",
        "shablon_spec/Dockerfile"
    ]
    
    all_exist = True
    
    for dockerfile in dockerfiles:
        if Path(dockerfile).exists():
            print(f"✅ {dockerfile} существует")
            
            # Проверяем содержимое
            with open(dockerfile, 'r') as f:
                content = f.read()
                if 'python' in content.lower():
                    print(f"   ✅ Содержит Python")
                else:
                    print(f"   ⚠️ Не содержит Python")
        else:
            print(f"❌ {dockerfile} не найден")
            all_exist = False
    
    return all_exist

def main():
    """Основная функция"""
    print("🔧 Тест импорта API модулей JALM Full Stack")
    print("=" * 60)
    
    results = {}
    
    # Тест импорта API
    results["tula_spec_api"] = test_tula_spec_api_import()
    results["shablon_spec_api"] = test_shablon_spec_api_import()
    results["core_runner"] = test_core_runner_import()
    
    # Тест файлов
    results["requirements"] = test_requirements_files()
    results["dockerfiles"] = test_dockerfiles()
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТА ИМПОРТА")
    print("=" * 60)
    
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
            print("  🎉 ОТЛИЧНО! Все API модули готовы к запуску!")
        elif success_rate >= 80:
            print("  ✅ ХОРОШО! Большинство модулей готовы.")
        else:
            print("  ⚠️ ТРЕБУЕТ ВНИМАНИЯ! Есть проблемы с модулями.")

if __name__ == "__main__":
    main() 