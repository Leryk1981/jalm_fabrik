#!/usr/bin/env python3
"""
Комплексное тестирование JALM Full Stack
Проверяет все три компонента: core-runner, tula_spec, shablon_spec
"""

import requests
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List

class JALMFullStackTester:
    """Тестер для JALM Full Stack"""
    
    def __init__(self):
        self.base_urls = {
            "core_runner": "http://localhost:8000",
            "tula_spec": "http://localhost:8001", 
            "shablon_spec": "http://localhost:8002"
        }
        self.results = {}
    
    def test_health_checks(self) -> Dict[str, bool]:
        """Тест проверки здоровья всех сервисов"""
        print("=== Тест проверки здоровья сервисов ===")
        health_results = {}
        
        for service, url in self.base_urls.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"✅ {service}: {health_data}")
                    health_results[service] = True
                else:
                    print(f"❌ {service}: HTTP {response.status_code}")
                    health_results[service] = False
            except requests.exceptions.RequestException as e:
                print(f"❌ {service}: {e}")
                health_results[service] = False
        
        self.results["health_checks"] = health_results
        return health_results
    
    def test_tula_spec_functions(self) -> Dict[str, Any]:
        """Тест функций Tula Spec"""
        print("\n=== Тест функций Tula Spec ===")
        function_results = {}
        
        # Тест получения списка функций
        try:
            response = requests.get(f"{self.base_urls['tula_spec']}/functions")
            if response.status_code == 200:
                functions = response.json()
                print(f"✅ Получено {len(functions)} функций")
                function_results["list_functions"] = True
                
                # Тест каждой функции
                for func in functions:
                    func_id = func["id"]
                    print(f"  Тестирование {func_id}...")
                    
                    # Тест получения метаданных
                    meta_response = requests.get(f"{self.base_urls['tula_spec']}/functions/{func_id}")
                    if meta_response.status_code == 200:
                        print(f"    ✅ Метаданные получены")
                        
                        # Тест выполнения функции
                        test_params = self._get_test_params_for_function(func_id)
                        if test_params:
                            exec_response = requests.post(
                                f"{self.base_urls['tula_spec']}/functions/{func_id}/execute",
                                json={"params": test_params}
                            )
                            if exec_response.status_code == 200:
                                result = exec_response.json()
                                print(f"    ✅ Выполнение: {result['status']}")
                                function_results[f"{func_id}_execution"] = True
                            else:
                                print(f"    ❌ Ошибка выполнения: {exec_response.status_code}")
                                function_results[f"{func_id}_execution"] = False
                        else:
                            print(f"    ⚠️ Нет тестовых параметров для {func_id}")
                    else:
                        print(f"    ❌ Ошибка получения метаданных: {meta_response.status_code}")
                        function_results[f"{func_id}_metadata"] = False
            else:
                print(f"❌ Ошибка получения списка функций: {response.status_code}")
                function_results["list_functions"] = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка Tula Spec: {e}")
            function_results["error"] = str(e)
        
        self.results["tula_spec_functions"] = function_results
        return function_results
    
    def test_shablon_spec_templates(self) -> Dict[str, Any]:
        """Тест шаблонов Shablon Spec"""
        print("\n=== Тест шаблонов Shablon Spec ===")
        template_results = {}
        
        # Тест получения списка шаблонов
        try:
            response = requests.get(f"{self.base_urls['shablon_spec']}/templates")
            if response.status_code == 200:
                templates = response.json()
                print(f"✅ Получено {len(templates)} шаблонов")
                template_results["list_templates"] = True
                
                # Тест каждой категории
                categories_response = requests.get(f"{self.base_urls['shablon_spec']}/categories")
                if categories_response.status_code == 200:
                    categories = categories_response.json()
                    print(f"✅ Категории: {categories['categories']}")
                    template_results["categories"] = True
                
                # Тест каждого шаблона
                for template in templates:
                    template_id = template["id"]
                    print(f"  Тестирование {template_id}...")
                    
                    # Тест получения метаданных
                    meta_response = requests.get(f"{self.base_urls['shablon_spec']}/templates/{template_id}")
                    if meta_response.status_code == 200:
                        print(f"    ✅ Метаданные получены")
                        
                        # Тест получения содержимого
                        content_response = requests.get(f"{self.base_urls['shablon_spec']}/templates/{template_id}/content")
                        if content_response.status_code == 200:
                            content_data = content_response.json()
                            print(f"    ✅ Содержимое получено (хеш: {content_data['hash'][:8]}...)")
                            
                            # Тест валидации
                            validation_response = requests.post(
                                f"{self.base_urls['shablon_spec']}/templates/validate",
                                json={"jalm_content": content_data["content"]}
                            )
                            if validation_response.status_code == 200:
                                validation_result = validation_response.json()
                                if validation_result["is_valid"]:
                                    print(f"    ✅ Валидация пройдена")
                                    template_results[f"{template_id}_validation"] = True
                                else:
                                    print(f"    ❌ Ошибки валидации: {validation_result['errors']}")
                                    template_results[f"{template_id}_validation"] = False
                            else:
                                print(f"    ❌ Ошибка валидации: {validation_response.status_code}")
                                template_results[f"{template_id}_validation"] = False
                        else:
                            print(f"    ❌ Ошибка получения содержимого: {content_response.status_code}")
                            template_results[f"{template_id}_content"] = False
                    else:
                        print(f"    ❌ Ошибка получения метаданных: {meta_response.status_code}")
                        template_results[f"{template_id}_metadata"] = False
            else:
                print(f"❌ Ошибка получения списка шаблонов: {response.status_code}")
                template_results["list_templates"] = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка Shablon Spec: {e}")
            template_results["error"] = str(e)
        
        self.results["shablon_spec_templates"] = template_results
        return template_results
    
    def test_core_runner_execution(self) -> Dict[str, Any]:
        """Тест выполнения в Core Runner"""
        print("\n=== Тест выполнения в Core Runner ===")
        execution_results = {}
        
        # Простой тест JALM-интента
        test_intent = """
BEGIN test-intent
  IMPORT slot_validator tula:hash~ab12fe
  IMPORT notify_system v1.0.0
  
  WHEN test TRIGGERS
    RUN slot_uuid := slot_validator.create({
      "slot": {
        "datetime": "2024-06-15T10:00:00Z",
        "duration": 60,
        "service_id": "123e4567-e89b-12d3-a456-426614174000"
      }
    })
    
    IF slot_uuid.status == "valid" THEN
      RUN notify_system.send("Тест пройден", "web", "test@example.com", "test")
      system.log("evt: test_success")
    ELSE
      system.log("evt: test_failed")
  
  ON ERROR handleError
END
"""
        
        try:
            response = requests.post(
                f"{self.base_urls['core_runner']}/execute",
                json={
                    "intent_content": test_intent,
                    "params": {
                        "test_param": "test_value"
                    },
                    "timeout": 30
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Выполнение JALM: {result.get('execution_id', 'unknown')}")
                execution_results["intent_execution"] = True
                execution_results["execution_id"] = result.get("execution_id", "")
            else:
                print(f"❌ Ошибка выполнения интента: {response.status_code}")
                execution_results["intent_execution"] = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка Core Runner: {e}")
            execution_results["error"] = str(e)
        
        self.results["core_runner_execution"] = execution_results
        return execution_results
    
    def test_integration(self) -> Dict[str, Any]:
        """Тест интеграции между компонентами"""
        print("\n=== Тест интеграции между компонентами ===")
        integration_results = {}
        
        # Тест загрузки функций из tula_spec в core_runner
        try:
            # Получаем функции из tula_spec
            tula_response = requests.get(f"{self.base_urls['tula_spec']}/functions")
            if tula_response.status_code == 200:
                functions = tula_response.json()
                print(f"✅ Получено {len(functions)} функций из Tula Spec")
                
                # Получаем шаблоны из shablon_spec
                shablon_response = requests.get(f"{self.base_urls['shablon_spec']}/templates")
                if shablon_response.status_code == 200:
                    templates = shablon_response.json()
                    print(f"✅ Получено {len(templates)} шаблонов из Shablon Spec")
                    
                    # Проверяем зависимости
                    for template in templates:
                        template_id = template["id"]
                        dependencies = template.get("dependencies", {}).get("tula_spec", [])
                        if dependencies:
                            print(f"  Шаблон {template_id} зависит от {len(dependencies)} функций")
                            integration_results[f"{template_id}_dependencies"] = True
                        else:
                            print(f"  Шаблон {template_id} не имеет зависимостей")
                            integration_results[f"{template_id}_dependencies"] = False
                    
                    integration_results["function_template_integration"] = True
                else:
                    print(f"❌ Ошибка получения шаблонов: {shablon_response.status_code}")
                    integration_results["function_template_integration"] = False
            else:
                print(f"❌ Ошибка получения функций: {tula_response.status_code}")
                integration_results["function_template_integration"] = False
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка интеграции: {e}")
            integration_results["error"] = str(e)
        
        self.results["integration"] = integration_results
        return integration_results
    
    def _get_test_params_for_function(self, func_id: str) -> Dict[str, Any]:
        """Получение тестовых параметров для функции"""
        test_params = {
            "slot_validator": {
                "slot": {
                    "datetime": "2024-06-15T10:00:00Z",
                    "duration": 60,
                    "service_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            },
            "booking_widget": {
                "calendar_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-123"
            },
            "notify_system": {
                "message": "Тестовое уведомление",
                "channel": "web",
                "recipient": "test@example.com",
                "notification_type": "test"
            }
        }
        return test_params.get(func_id, {})
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🚀 Запуск комплексного тестирования JALM Full Stack")
        print("=" * 60)
        
        # Тест проверки здоровья
        health_results = self.test_health_checks()
        
        # Проверяем, что все сервисы доступны
        if not all(health_results.values()):
            print("\n❌ Не все сервисы доступны. Запустите сервисы перед тестированием:")
            print("cd core-runner && python api/main.py")
            print("cd tula_spec && python api/main.py") 
            print("cd shablon_spec && python api/main.py")
            return self.results
        
        # Тест функций Tula Spec
        self.test_tula_spec_functions()
        
        # Тест шаблонов Shablon Spec
        self.test_shablon_spec_templates()
        
        # Тест выполнения в Core Runner
        self.test_core_runner_execution()
        
        # Тест интеграции
        self.test_integration()
        
        # Итоговый отчет
        self._print_summary()
        
        return self.results
    
    def _print_summary(self):
        """Вывод итогового отчета"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
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
                print("  🎉 ОТЛИЧНО! JALM Full Stack работает корректно!")
            elif overall_success_rate >= 70:
                print("  ✅ ХОРОШО! Есть небольшие проблемы, но система работает.")
            else:
                print("  ⚠️ ТРЕБУЕТ ВНИМАНИЯ! Есть критические проблемы.")
        else:
            print("  ❌ Нет данных для анализа.")

def main():
    """Основная функция"""
    tester = JALMFullStackTester()
    results = tester.run_all_tests()
    
    # Сохранение результатов в файл
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Результаты сохранены в test_results.json")

if __name__ == "__main__":
    main() 