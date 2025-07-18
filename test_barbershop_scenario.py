#!/usr/bin/env python3
"""
Тестовый сценарий барбершопа для JALM Full Stack
"""

import json
import requests
import csv
from pathlib import Path
from typing import Dict, Any, List

class BarbershopScenarioTester:
    """Тестер сценария барбершопа"""
    
    def __init__(self):
        self.base_urls = {
            "core_runner": "http://localhost:8888",
            "tula_spec": "http://localhost:8001",
            "shablon_spec": "http://localhost:8002"
        }
        self.results = {}
    
    def test_plugin_structure(self) -> Dict[str, bool]:
        """Тест структуры плагина"""
        print("=== Тест структуры плагина барбершопа ===")
        structure_results = {}
        
        required_files = [
            "barbershop_plugin/OBJECT.jalm",
            "barbershop_plugin/FILES/plugin.js",
            "barbershop_plugin/FILES/llm_actions.json", 
            "barbershop_plugin/FILES/migrations.csv",
            "barbershop_plugin/FILES/manifest.json"
        ]
        
        for file_path in required_files:
            if Path(file_path).exists():
                print(f"✅ {file_path} существует")
                structure_results[file_path] = True
            else:
                print(f"❌ {file_path} не найден")
                structure_results[file_path] = False
        
        self.results["plugin_structure"] = structure_results
        return structure_results
    
    def test_jalm_object(self) -> Dict[str, Any]:
        """Тест JALM объекта"""
        print("\n=== Тест JALM объекта ===")
        jalm_results = {}
        
        try:
            # Читаем OBJECT.jalm
            with open("barbershop_plugin/OBJECT.jalm", 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Простая валидация структуры
            required_sections = ["name:", "communication:", "llm:", "variables:", "requires:", "generate:"]
            for section in required_sections:
                if section in content:
                    print(f"✅ Секция {section} найдена")
                    jalm_results[f"section_{section[:-1]}"] = True
                else:
                    print(f"❌ Секция {section} не найдена")
                    jalm_results[f"section_{section[:-1]}"] = False
            
            # Проверяем переменные
            if "shop_name" in content and "telegram_bot_token" in content:
                print("✅ Основные переменные найдены")
                jalm_results["variables"] = True
            else:
                print("❌ Не все переменные найдены")
                jalm_results["variables"] = False
                
        except Exception as e:
            print(f"❌ Ошибка чтения OBJECT.jalm: {e}")
            jalm_results["error"] = str(e)
        
        self.results["jalm_object"] = jalm_results
        return jalm_results
    
    def test_plugin_js(self) -> Dict[str, Any]:
        """Тест JavaScript плагина"""
        print("\n=== Тест JavaScript плагина ===")
        js_results = {}
        
        try:
            with open("barbershop_plugin/FILES/plugin.js", 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем ключевые элементы
            checks = [
                ("window.BARBERS", "Переменная BARBERS"),
                ("window.CHATBOT_URL", "Переменная CHATBOT_URL"),
                ("createBookingWidget", "Функция создания виджета"),
                ("openTelegramChat", "Функция открытия чата"),
                ("booking-modal", "Модальное окно"),
                ("barber-item", "Элементы барберов")
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✅ {description} найдено")
                    js_results[check] = True
                else:
                    print(f"❌ {description} не найдено")
                    js_results[check] = False
                    
        except Exception as e:
            print(f"❌ Ошибка чтения plugin.js: {e}")
            js_results["error"] = str(e)
        
        self.results["plugin_js"] = js_results
        return js_results
    
    def test_llm_actions(self) -> Dict[str, Any]:
        """Тест LLM действий"""
        print("\n=== Тест LLM действий ===")
        actions_results = {}
        
        try:
            with open("barbershop_plugin/FILES/llm_actions.json", 'r', encoding='utf-8') as f:
                actions = json.load(f)
            
            print(f"✅ Загружено {len(actions)} действий")
            actions_results["load_success"] = True
            
            # Проверяем ключевые интенты
            required_intents = ["book_slot", "show_schedule", "welcome_message"]
            for intent in required_intents:
                intent_found = any(action.get("intent") == intent for action in actions)
                if intent_found:
                    print(f"✅ Интент {intent} найден")
                    actions_results[f"intent_{intent}"] = True
                else:
                    print(f"❌ Интент {intent} не найден")
                    actions_results[f"intent_{intent}"] = False
            
            # Проверяем структуру действий
            for action in actions:
                if "intent" in action and "channel" in action:
                    print(f"✅ Действие {action['intent']} корректно")
                    actions_results[f"action_{action['intent']}"] = True
                else:
                    print(f"❌ Действие {action.get('intent', 'unknown')} некорректно")
                    actions_results[f"action_{action.get('intent', 'unknown')}"] = False
                    
        except Exception as e:
            print(f"❌ Ошибка чтения llm_actions.json: {e}")
            actions_results["error"] = str(e)
        
        self.results["llm_actions"] = actions_results
        return actions_results
    
    def test_migrations_csv(self) -> Dict[str, Any]:
        """Тест CSV миграций"""
        print("\n=== Тест CSV миграций ===")
        csv_results = {}
        
        try:
            with open("barbershop_plugin/FILES/migrations.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            print(f"✅ Загружено {len(rows)} барберов")
            csv_results["load_success"] = True
            
            # Проверяем структуру
            required_columns = ["name", "tg_id", "photo", "speciality"]
            for column in required_columns:
                if column in rows[0].keys():
                    print(f"✅ Колонка {column} найдена")
                    csv_results[f"column_{column}"] = True
                else:
                    print(f"❌ Колонка {column} не найдена")
                    csv_results[f"column_{column}"] = False
            
            # Проверяем данные
            for i, row in enumerate(rows):
                if row.get("name") and row.get("tg_id"):
                    print(f"✅ Барбер {row['name']} (@{row['tg_id']}) корректно")
                    csv_results[f"barber_{i}"] = True
                else:
                    print(f"❌ Барбер {i} некорректно")
                    csv_results[f"barber_{i}"] = False
                    
        except Exception as e:
            print(f"❌ Ошибка чтения migrations.csv: {e}")
            csv_results["error"] = str(e)
        
        self.results["migrations_csv"] = csv_results
        return csv_results
    
    def test_manifest(self) -> Dict[str, Any]:
        """Тест манифеста"""
        print("\n=== Тест манифеста ===")
        manifest_results = {}
        
        try:
            with open("barbershop_plugin/FILES/manifest.json", 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Проверяем основные поля
            required_fields = ["name", "version", "entry_point", "files"]
            for field in required_fields:
                if field in manifest:
                    print(f"✅ Поле {field} найдено")
                    manifest_results[f"field_{field}"] = True
                else:
                    print(f"❌ Поле {field} не найдено")
                    manifest_results[f"field_{field}"] = False
            
            # Проверяем зависимости
            if "dependencies" in manifest and "tula_spec" in manifest["dependencies"]:
                print("✅ Зависимости Tula Spec найдены")
                manifest_results["dependencies"] = True
            else:
                print("❌ Зависимости Tula Spec не найдены")
                manifest_results["dependencies"] = False
                
        except Exception as e:
            print(f"❌ Ошибка чтения manifest.json: {e}")
            manifest_results["error"] = str(e)
        
        self.results["manifest"] = manifest_results
        return manifest_results
    
    def test_integration_with_jalm(self) -> Dict[str, Any]:
        """Тест интеграции с JALM Full Stack"""
        print("\n=== Тест интеграции с JALM Full Stack ===")
        integration_results = {}
        
        # Тест доступности сервисов
        for service, url in self.base_urls.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service} доступен")
                    integration_results[f"{service}_health"] = True
                else:
                    print(f"❌ {service} недоступен")
                    integration_results[f"{service}_health"] = False
            except:
                print(f"❌ {service} недоступен")
                integration_results[f"{service}_health"] = False
        
        # Тест функций Tula Spec
        try:
            response = requests.get(f"{self.base_urls['tula_spec']}/functions")
            if response.status_code == 200:
                functions = response.json()
                required_functions = ["slot_validator", "booking_widget", "notify_system"]
                for func in required_functions:
                    func_found = any(f["id"] == func for f in functions)
                    if func_found:
                        print(f"✅ Функция {func} доступна")
                        integration_results[f"function_{func}"] = True
                    else:
                        print(f"❌ Функция {func} недоступна")
                        integration_results[f"function_{func}"] = False
        except Exception as e:
            print(f"❌ Ошибка проверки функций: {e}")
            integration_results["functions_error"] = str(e)
        
        self.results["integration"] = integration_results
        return integration_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🎯 Тестирование сценария барбершопа")
        print("=" * 60)
        
        # Тесты структуры
        self.test_plugin_structure()
        self.test_jalm_object()
        self.test_plugin_js()
        self.test_llm_actions()
        self.test_migrations_csv()
        self.test_manifest()
        
        # Тесты интеграции
        self.test_integration_with_jalm()
        
        # Итоговый отчет
        self._print_summary()
        
        return self.results
    
    def _print_summary(self):
        """Вывод итогового отчета"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ БАРБЕРШОПА")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_category, results in self.results.items():
            if isinstance(results, dict):
                category_tests = len([v for v in results.values() if isinstance(v, bool)])
                category_passed = len([v for v in results.values() if v is True])
                total_tests += category_tests
                passed_tests += category_passed
                
                print(f"\n{test_category.replace('_', ' ').title()}:")
                print(f"  Тестов: {category_tests}, Пройдено: {category_passed}")
                
                if category_tests > 0:
                    success_rate = (category_passed / category_tests) * 100
                    print(f"  Успешность: {success_rate:.1f}%")
        
        print(f"\n📈 ОБЩИЙ РЕЗУЛЬТАТ:")
        print(f"  Всего тестов: {total_tests}")
        print(f"  Пройдено: {passed_tests}")
        print(f"  Провалено: {total_tests - passed_tests}")
        
        if total_tests > 0:
            overall_success_rate = (passed_tests / total_tests) * 100
            print(f"  Общая успешность: {overall_success_rate:.1f}%")
            
            if overall_success_rate >= 90:
                print("  🎉 ОТЛИЧНО! Сценарий барбершопа готов к развертыванию!")
            elif overall_success_rate >= 70:
                print("  ✅ ХОРОШО! Сценарий работает, есть небольшие доработки.")
            else:
                print("  ⚠️ ТРЕБУЕТ ВНИМАНИЯ! Есть критические проблемы.")

def main():
    """Основная функция"""
    tester = BarbershopScenarioTester()
    results = tester.run_all_tests()
    
    # Сохранение результатов
    with open("barbershop_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Результаты сохранены в barbershop_test_results.json")

if __name__ == "__main__":
    main() 