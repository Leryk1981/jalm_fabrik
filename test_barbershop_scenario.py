#!/usr/bin/env python3
"""
Тестовый сценарий барбершопа для JALM Full Stack
Тестирует создание готового продукта через saas_provisioner.py
"""

import json
import requests
import csv
import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List

class BarbershopScenarioTester:
    """Тестер сценария барбершопа с правильной архитектурой JALM Full Stack"""
    
    def __init__(self):
        self.base_urls = {
            "core_runner": "http://localhost:8888",
            "tula_spec": "http://localhost:8001", 
            "shablon_spec": "http://localhost:8002"
        }
        self.results = {}
        self.product_name = "barbershop_test"
        self.product_path = f"instances/{self.product_name}"
    
    def test_jalm_services_health(self) -> Dict[str, bool]:
        """Тест здоровья JALM сервисов"""
        print("=== Тест здоровья JALM сервисов ===")
        health_results = {}
        
        for service, url in self.base_urls.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service} здоров")
                    health_results[f"{service}_health"] = True
                else:
                    print(f"❌ {service} не отвечает")
                    health_results[f"{service}_health"] = False
            except Exception as e:
                print(f"❌ {service} недоступен: {e}")
                health_results[f"{service}_health"] = False
        
        self.results["jalm_services_health"] = health_results
        return health_results
    
    def test_tula_spec_functions(self) -> Dict[str, Any]:
        """Тест функций Tula Spec"""
        print("\n=== Тест функций Tula Spec ===")
        functions_results = {}
        
        try:
            response = requests.get(f"{self.base_urls['tula_spec']}/functions")
            if response.status_code == 200:
                functions = response.json()
                print(f"✅ Загружено {len(functions)} функций")
                functions_results["load_success"] = True
                
                # Проверяем ключевые функции барбершопа
                required_functions = ["slot_validator", "booking_widget", "notify_system"]
                for func_name in required_functions:
                    func_found = any(f["id"] == func_name for f in functions)
                    if func_found:
                        print(f"✅ Функция {func_name} доступна")
                        functions_results[f"function_{func_name}"] = True
                    else:
                        print(f"❌ Функция {func_name} недоступна")
                        functions_results[f"function_{func_name}"] = False
                
                # Проверяем метаданные функций
                for func in functions:
                    if func["id"] in required_functions:
                        if "description" in func and "input_schema" in func:
                            print(f"✅ Метаданные функции {func['id']} корректны")
                            functions_results[f"metadata_{func['id']}"] = True
                        else:
                            print(f"❌ Метаданные функции {func['id']} неполные")
                            functions_results[f"metadata_{func['id']}"] = False
            else:
                print(f"❌ Ошибка загрузки функций: {response.status_code}")
                functions_results["load_success"] = False
                
        except Exception as e:
            print(f"❌ Ошибка проверки функций: {e}")
            functions_results["error"] = str(e)
        
        self.results["tula_spec_functions"] = functions_results
        return functions_results
    
    def test_shablon_spec_templates(self) -> Dict[str, Any]:
        """Тест шаблонов Shablon Spec"""
        print("\n=== Тест шаблонов Shablon Spec ===")
        templates_results = {}
        
        try:
            response = requests.get(f"{self.base_urls['shablon_spec']}/templates")
            if response.status_code == 200:
                templates = response.json()
                print(f"✅ Загружено {len(templates)} шаблонов")
                templates_results["load_success"] = True
                
                # Проверяем наличие шаблона барбершопа
                barbershop_template = None
                for template in templates:
                    if template.get("id") == "barbershop_basic":
                        barbershop_template = template
                        break
                
                if barbershop_template:
                    print("✅ Шаблон барбершопа найден")
                    templates_results["barbershop_template"] = True
                    
                    # Проверяем структуру шаблона
                    required_fields = ["name", "description", "files", "config"]
                    for field in required_fields:
                        if field in barbershop_template:
                            print(f"✅ Поле {field} в шаблоне найдено")
                            templates_results[f"template_field_{field}"] = True
                        else:
                            print(f"❌ Поле {field} в шаблоне не найдено")
                            templates_results[f"template_field_{field}"] = False
                else:
                    print("❌ Шаблон барбершопа не найден")
                    templates_results["barbershop_template"] = False
            else:
                print(f"❌ Ошибка загрузки шаблонов: {response.status_code}")
                templates_results["load_success"] = False
                
        except Exception as e:
            print(f"❌ Ошибка проверки шаблонов: {e}")
            templates_results["error"] = str(e)
        
        self.results["shablon_spec_templates"] = templates_results
        return templates_results
    
    def test_product_creation(self) -> Dict[str, Any]:
        """Тест создания продукта через saas_provisioner"""
        print("\n=== Тест создания продукта барбершопа ===")
        creation_results = {}
        
        try:
            # Очищаем предыдущий продукт если есть
            if Path(self.product_path).exists():
                import shutil
                shutil.rmtree(self.product_path)
                print("🗑️ Удален предыдущий продукт")
            
            # Создаем Intent-DSL для барбершопа
            intent_dsl = """
            name: barbershop_test
            description: Тестовый барбершоп для проверки JALM Full Stack
            
            variables:
              shop_name: "Тестовый Барбершоп"
              telegram_bot_token: "test_token_123"
              admin_phone: "+79001234567"
            
            functions:
              - slot_validator
              - booking_widget  
              - notify_system
            
            templates:
              - barbershop_basic
            
            config:
              port: 3000
              database: sqlite
              notifications: telegram
            """
            
            # Сохраняем Intent-DSL
            intent_file = f"{self.product_name}.intent"
            with open(intent_file, 'w', encoding='utf-8') as f:
                f.write(intent_dsl)
            
            print("✅ Intent-DSL создан")
            creation_results["intent_dsl_created"] = True
            
            # Запускаем saas_provisioner
            print("🚀 Запуск saas_provisioner...")
            result = subprocess.run([
                sys.executable, "saas_provisioner.py", 
                "--intent", intent_file,
                "--output", self.product_path
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Продукт создан успешно")
                creation_results["product_created"] = True
                print(result.stdout)
            else:
                print(f"❌ Ошибка создания продукта: {result.stderr}")
                creation_results["product_created"] = False
                creation_results["error"] = result.stderr
            
            # Очищаем временный файл
            Path(intent_file).unlink(missing_ok=True)
            
        except Exception as e:
            print(f"❌ Ошибка теста создания продукта: {e}")
            creation_results["error"] = str(e)
        
        self.results["product_creation"] = creation_results
        return creation_results
    
    def test_product_structure(self) -> Dict[str, bool]:
        """Тест структуры созданного продукта"""
        print("\n=== Тест структуры продукта ===")
        structure_results = {}
        
        if not Path(self.product_path).exists():
            print("❌ Продукт не создан")
            structure_results["product_exists"] = False
            self.results["product_structure"] = structure_results
            return structure_results
        
        print("✅ Продукт существует")
        structure_results["product_exists"] = True
        
        # Проверяем основные файлы
        required_files = [
            "Dockerfile",
            "docker-compose.yml", 
            "requirements.txt",
            "main.py",
            "provision.yaml",
            "README.md"
        ]
        
        for file_name in required_files:
            file_path = Path(self.product_path) / file_name
            if file_path.exists():
                print(f"✅ {file_name} существует")
                structure_results[f"file_{file_name}"] = True
            else:
                print(f"❌ {file_name} не найден")
                structure_results[f"file_{file_name}"] = False
        
        # Проверяем структуру каталогов
        required_dirs = ["api", "static", "templates"]
        for dir_name in required_dirs:
            dir_path = Path(self.product_path) / dir_name
            if dir_path.exists() and dir_path.is_dir():
                print(f"✅ Каталог {dir_name} существует")
                structure_results[f"dir_{dir_name}"] = True
            else:
                print(f"❌ Каталог {dir_name} не найден")
                structure_results[f"dir_{dir_name}"] = False
        
        self.results["product_structure"] = structure_results
        return structure_results
    
    def test_provision_yaml(self) -> Dict[str, Any]:
        """Тест provision.yaml"""
        print("\n=== Тест provision.yaml ===")
        provision_results = {}
        
        provision_file = Path(self.product_path) / "provision.yaml"
        if not provision_file.exists():
            print("❌ provision.yaml не найден")
            provision_results["file_exists"] = False
            self.results["provision_yaml"] = provision_results
            return provision_results
        
        print("✅ provision.yaml найден")
        provision_results["file_exists"] = True
        
        try:
            with open(provision_file, 'r', encoding='utf-8') as f:
                provision = yaml.safe_load(f)
            
            # Проверяем основные секции
            required_sections = ["name", "description", "variables", "functions", "templates"]
            for section in required_sections:
                if section in provision:
                    print(f"✅ Секция {section} найдена")
                    provision_results[f"section_{section}"] = True
                else:
                    print(f"❌ Секция {section} не найдена")
                    provision_results[f"section_{section}"] = False
            
            # Проверяем переменные
            if "variables" in provision:
                vars_count = len(provision["variables"])
                print(f"✅ Найдено {vars_count} переменных")
                provision_results["variables_count"] = vars_count
                
                required_vars = ["shop_name", "telegram_bot_token"]
                for var in required_vars:
                    if var in provision["variables"]:
                        print(f"✅ Переменная {var} найдена")
                        provision_results[f"variable_{var}"] = True
                    else:
                        print(f"❌ Переменная {var} не найдена")
                        provision_results[f"variable_{var}"] = False
            
            # Проверяем функции
            if "functions" in provision:
                funcs_count = len(provision["functions"])
                print(f"✅ Найдено {funcs_count} функций")
                provision_results["functions_count"] = funcs_count
                
                required_funcs = ["slot_validator", "booking_widget", "notify_system"]
                for func in required_funcs:
                    if func in provision["functions"]:
                        print(f"✅ Функция {func} найдена")
                        provision_results[f"function_{func}"] = True
                    else:
                        print(f"❌ Функция {func} не найдена")
                        provision_results[f"function_{func}"] = False
                        
        except Exception as e:
            print(f"❌ Ошибка чтения provision.yaml: {e}")
            provision_results["error"] = str(e)
        
        self.results["provision_yaml"] = provision_results
        return provision_results
    
    def test_docker_configuration(self) -> Dict[str, Any]:
        """Тест Docker конфигурации"""
        print("\n=== Тест Docker конфигурации ===")
        docker_results = {}
        
        # Проверяем Dockerfile
        dockerfile_path = Path(self.product_path) / "Dockerfile"
        if dockerfile_path.exists():
            print("✅ Dockerfile найден")
            docker_results["dockerfile_exists"] = True
            
            try:
                with open(dockerfile_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Проверяем ключевые элементы
                checks = [
                    ("FROM python", "Базовый образ Python"),
                    ("COPY requirements.txt", "Копирование зависимостей"),
                    ("RUN pip install", "Установка зависимостей"),
                    ("COPY .", "Копирование кода"),
                    ("EXPOSE", "Открытие порта"),
                    ("CMD", "Команда запуска")
                ]
                
                for check, description in checks:
                    if check in content:
                        print(f"✅ {description} найдено")
                        docker_results[f"dockerfile_{check.lower().replace(' ', '_')}"] = True
                    else:
                        print(f"❌ {description} не найдено")
                        docker_results[f"dockerfile_{check.lower().replace(' ', '_')}"] = False
                        
            except Exception as e:
                print(f"❌ Ошибка чтения Dockerfile: {e}")
                docker_results["dockerfile_error"] = str(e)
        else:
            print("❌ Dockerfile не найден")
            docker_results["dockerfile_exists"] = False
        
        # Проверяем docker-compose.yml
        compose_path = Path(self.product_path) / "docker-compose.yml"
        if compose_path.exists():
            print("✅ docker-compose.yml найден")
            docker_results["compose_exists"] = True
            
            try:
                with open(compose_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Проверяем ключевые элементы
                checks = [
                    ("version:", "Версия compose"),
                    ("services:", "Секция сервисов"),
                    ("jalm-core-runner:", "Сервис core-runner"),
                    ("jalm-tula-spec:", "Сервис tula-spec"),
                    ("jalm-shablon-spec:", "Сервис shablon-spec"),
                    ("networks:", "Секция сетей")
                ]
                
                for check, description in checks:
                    if check in content:
                        print(f"✅ {description} найдено")
                        docker_results[f"compose_{check.lower().replace(':', '').replace('-', '_')}"] = True
                    else:
                        print(f"❌ {description} не найдено")
                        docker_results[f"compose_{check.lower().replace(':', '').replace('-', '_')}"] = False
                        
            except Exception as e:
                print(f"❌ Ошибка чтения docker-compose.yml: {e}")
                docker_results["compose_error"] = str(e)
        else:
            print("❌ docker-compose.yml не найден")
            docker_results["compose_exists"] = False
        
        self.results["docker_configuration"] = docker_results
        return docker_results
    
    def test_product_api(self) -> Dict[str, Any]:
        """Тест API созданного продукта"""
        print("\n=== Тест API продукта ===")
        api_results = {}
        
        # Проверяем main.py
        main_py_path = Path(self.product_path) / "main.py"
        if not main_py_path.exists():
            print("❌ main.py не найден")
            api_results["main_py_exists"] = False
            self.results["product_api"] = api_results
            return api_results
        
        print("✅ main.py найден")
        api_results["main_py_exists"] = True
        
        try:
            with open(main_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем ключевые элементы API
            checks = [
                ("from fastapi import", "Импорт FastAPI"),
                ("app = FastAPI", "Создание приложения"),
                ("@app.get", "GET эндпоинты"),
                ("@app.post", "POST эндпоинты"),
                ("uvicorn.run", "Запуск сервера")
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✅ {description} найдено")
                    api_results[f"api_{check.lower().replace(' ', '_').replace('=', '')}"] = True
                else:
                    print(f"❌ {description} не найдено")
                    api_results[f"api_{check.lower().replace(' ', '_').replace('=', '')}"] = False
            
            # Проверяем интеграцию с JALM
            jalm_checks = [
                ("JALM_CORE_RUNNER_URL", "URL core-runner"),
                ("JALM_TULA_SPEC_URL", "URL tula-spec"),
                ("JALM_SHABLON_SPEC_URL", "URL shablon-spec")
            ]
            
            for check, description in jalm_checks:
                if check in content:
                    print(f"✅ {description} найдено")
                    api_results[f"jalm_{check.lower()}"] = True
                else:
                    print(f"❌ {description} не найдено")
                    api_results[f"jalm_{check.lower()}"] = False
                    
        except Exception as e:
            print(f"❌ Ошибка чтения main.py: {e}")
            api_results["error"] = str(e)
        
        self.results["product_api"] = api_results
        return api_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🎯 Тестирование сценария барбершопа с JALM Full Stack")
        print("=" * 70)
        
        # Тесты JALM сервисов
        self.test_jalm_services_health()
        self.test_tula_spec_functions()
        self.test_shablon_spec_templates()
        
        # Тесты создания продукта
        self.test_product_creation()
        self.test_product_structure()
        self.test_provision_yaml()
        self.test_docker_configuration()
        self.test_product_api()
        
        # Итоговый отчет
        self._print_summary()
        
        return self.results
    
    def _print_summary(self):
        """Вывод итогового отчета"""
        print("\n" + "=" * 70)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ БАРБЕРШОПА С JALM FULL STACK")
        print("=" * 70)
        
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
                print("  🎉 ОТЛИЧНО! Барбершоп готов к развертыванию с JALM Full Stack!")
            elif overall_success_rate >= 70:
                print("  ✅ ХОРОШО! Барбершоп работает, есть небольшие доработки.")
            else:
                print("  ⚠️ ТРЕБУЕТ ВНИМАНИЯ! Есть критические проблемы.")

def main():
    """Основная функция"""
    # Импортируем yaml для работы с provision.yaml
    global yaml
    try:
        import yaml
    except ImportError:
        print("❌ Требуется установить PyYAML: pip install PyYAML")
        return
    
    tester = BarbershopScenarioTester()
    results = tester.run_all_tests()
    
    # Сохранение результатов
    with open("barbershop_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Результаты сохранены в barbershop_test_results.json")

if __name__ == "__main__":
    main() 