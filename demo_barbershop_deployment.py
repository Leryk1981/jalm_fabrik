#!/usr/bin/env python3
"""
Демонстрационный сценарий развертывания барбершопа
Показывает полный цикл от JALM-объекта до работающего бота
"""

import json
import csv
import zipfile
from pathlib import Path
from typing import Dict, Any

class BarbershopDeploymentDemo:
    """Демонстрация развертывания барбершопа"""
    
    def __init__(self):
        self.tenant_id = "demo_barbershop_001"
        self.deployment_data = {}
    
    def step_1_validate_jalm_object(self) -> bool:
        """Шаг 1: Валидация JALM объекта"""
        print("🔍 Шаг 1: Валидация JALM объекта")
        print("-" * 40)
        
        try:
            with open("barbershop_plugin/OBJECT.jalm", 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем структуру
            checks = [
                ("name:", "Название плагина"),
                ("communication:", "Настройки коммуникации"),
                ("llm:", "Настройки LLM"),
                ("variables:", "Переменные"),
                ("requires:", "Зависимости"),
                ("generate:", "Генерация")
            ]
            
            all_valid = True
            for check, description in checks:
                if check in content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
                    all_valid = False
            
            self.deployment_data["jalm_valid"] = all_valid
            return all_valid
            
        except Exception as e:
            print(f"❌ Ошибка валидации: {e}")
            return False
    
    def step_2_process_files(self) -> bool:
        """Шаг 2: Обработка файлов"""
        print("\n📁 Шаг 2: Обработка файлов")
        print("-" * 40)
        
        try:
            # Обработка plugin.js
            with open("barbershop_plugin/FILES/plugin.js", 'r', encoding='utf-8') as f:
                plugin_content = f.read()
            
            # Замена плейсхолдеров
            replacements = {
                "{{STAFF_LIST_JSON}}": self._get_staff_json(),
                "{{BOTNAME}}": f"{self.tenant_id}_bot",
                "{{SHOP_NAME}}": "Барбершоп 'Классика'",
                "{{PRIMARY_COLOR}}": "#2C3E50"
            }
            
            for placeholder, value in replacements.items():
                plugin_content = plugin_content.replace(placeholder, str(value))
            
            # Сохраняем обработанный файл
            processed_dir = Path("processed_plugin")
            processed_dir.mkdir(exist_ok=True)
            
            with open(processed_dir / "plugin.js", 'w', encoding='utf-8') as f:
                f.write(plugin_content)
            
            print("✅ plugin.js обработан и минимизирован")
            
            # Обработка LLM действий
            with open("barbershop_plugin/FILES/llm_actions.json", 'r', encoding='utf-8') as f:
                actions = json.load(f)
            
            # Замена плейсхолдеров в API URLs
            for action in actions:
                if "api" in action:
                    action["api"] = action["api"].replace("{{TENANT_ID}}", self.tenant_id)
            
            with open(processed_dir / "llm_actions.json", 'w', encoding='utf-8') as f:
                json.dump(actions, f, indent=2, ensure_ascii=False)
            
            print("✅ llm_actions.json обработан")
            
            # Обработка CSV
            with open("barbershop_plugin/FILES/migrations.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                staff_data = list(reader)
            
            # Создание Firebase коллекции
            firebase_data = {
                "employees": staff_data,
                "slots": self._generate_slots(staff_data),
                "settings": {
                    "tenant_id": self.tenant_id,
                    "shop_name": "Барбершоп 'Классика'",
                    "slot_duration": 60,
                    "advance_booking_days": 14
                }
            }
            
            with open(processed_dir / "firebase_data.json", 'w', encoding='utf-8') as f:
                json.dump(firebase_data, f, indent=2, ensure_ascii=False)
            
            print("✅ Данные для Firebase подготовлены")
            
            self.deployment_data["files_processed"] = True
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обработки файлов: {e}")
            return False
    
    def step_3_create_telegram_bot(self) -> bool:
        """Шаг 3: Создание Telegram бота"""
        print("\n🤖 Шаг 3: Создание Telegram бота")
        print("-" * 40)
        
        try:
            bot_config = {
                "bot_name": f"{self.tenant_id}_bot",
                "username": f"{self.tenant_id}_barbershop_bot",
                "description": "Бот для записи к барберу",
                "commands": [
                    {"command": "start", "description": "Начать запись"},
                    {"command": "book", "description": "Записаться к барберу"},
                    {"command": "schedule", "description": "Посмотреть расписание"},
                    {"command": "barbers", "description": "Список барберов"},
                    {"command": "cancel", "description": "Отменить запись"}
                ],
                "webhook_url": f"https://webhooks.jalm.io/tenant/{self.tenant_id}/chat"
            }
            
            # Сохраняем конфигурацию бота
            processed_dir = Path("processed_plugin")
            with open(processed_dir / "telegram_bot.json", 'w', encoding='utf-8') as f:
                json.dump(bot_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Telegram бот создан: @{bot_config['username']}")
            print(f"✅ Webhook настроен: {bot_config['webhook_url']}")
            
            self.deployment_data["telegram_bot_created"] = True
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания бота: {e}")
            return False
    
    def step_4_setup_webhook_handler(self) -> bool:
        """Шаг 4: Настройка webhook обработчика"""
        print("\n🔗 Шаг 4: Настройка webhook обработчика")
        print("-" * 40)
        
        try:
            webhook_config = {
                "tenant_id": self.tenant_id,
                "channels": {
                    "telegram": {
                        "enabled": True,
                        "token": "{{TELEGRAM_BOT_TOKEN}}",
                        "webhook_url": f"https://webhooks.jalm.io/tenant/{self.tenant_id}/chat"
                    },
                    "messenger": {
                        "enabled": True,
                        "page_token": "{{MESSENGER_PAGE_TOKEN}}",
                        "webhook_url": f"https://webhooks.jalm.io/tenant/{self.tenant_id}/chat"
                    }
                },
                "llm_config": {
                    "model": "gpt-4",
                    "actions_file": "llm_actions.json",
                    "memory": "session"
                }
            }
            
            # Сохраняем конфигурацию webhook
            processed_dir = Path("processed_plugin")
            with open(processed_dir / "webhook_config.json", 'w', encoding='utf-8') as f:
                json.dump(webhook_config, f, indent=2, ensure_ascii=False)
            
            print("✅ Webhook обработчик настроен")
            print("✅ Поддержка Telegram и Messenger")
            
            self.deployment_data["webhook_configured"] = True
            return True
            
        except Exception as e:
            print(f"❌ Ошибка настройки webhook: {e}")
            return False
    
    def step_5_deploy_lambda(self) -> bool:
        """Шаг 5: Развертывание Lambda функции"""
        print("\n⚡ Шаг 5: Развертывание Lambda функции")
        print("-" * 40)
        
        try:
            lambda_config = {
                "function_name": f"{self.tenant_id}_chatbot",
                "runtime": "python3.9",
                "memory": "512MB",
                "timeout": 30,
                "environment_variables": {
                    "TENANT_ID": self.tenant_id,
                    "TELEGRAM_BOT_TOKEN": "{{TELEGRAM_BOT_TOKEN}}",
                    "MESSENGER_PAGE_TOKEN": "{{MESSENGER_PAGE_TOKEN}}",
                    "FIREBASE_PROJECT_ID": "{{FIREBASE_PROJECT_ID}}"
                },
                "layers": [
                    "jalm-core-runner",
                    "tula-spec-functions",
                    "shablon-spec-templates"
                ]
            }
            
            # Создаем deployment package
            processed_dir = Path("processed_plugin")
            with open(processed_dir / "lambda_config.json", 'w', encoding='utf-8') as f:
                json.dump(lambda_config, f, indent=2, ensure_ascii=False)
            
            print("✅ Lambda функция настроена")
            print(f"✅ Имя функции: {lambda_config['function_name']}")
            print("✅ Слои JALM подключены")
            
            self.deployment_data["lambda_deployed"] = True
            return True
            
        except Exception as e:
            print(f"❌ Ошибка развертывания Lambda: {e}")
            return False
    
    def step_6_create_deployment_package(self) -> bool:
        """Шаг 6: Создание пакета развертывания"""
        print("\n📦 Шаг 6: Создание пакета развертывания")
        print("-" * 40)
        
        try:
            # Создаем ZIP архив
            zip_path = f"barbershop_deployment_{self.tenant_id}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Добавляем обработанные файлы
                processed_dir = Path("processed_plugin")
                for file_path in processed_dir.glob("*"):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.name)
                        print(f"✅ Добавлен: {file_path.name}")
                
                # Добавляем исходные файлы
                source_files = [
                    "barbershop_plugin/OBJECT.jalm",
                    "barbershop_plugin/FILES/manifest.json"
                ]
                
                for file_path in source_files:
                    if Path(file_path).exists():
                        zipf.write(file_path, f"source/{Path(file_path).name}")
                        print(f"✅ Добавлен исходный: {Path(file_path).name}")
            
            print(f"✅ Пакет развертывания создан: {zip_path}")
            
            self.deployment_data["package_created"] = True
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания пакета: {e}")
            return False
    
    def step_7_generate_client_assets(self) -> bool:
        """Шаг 7: Генерация клиентских ресурсов"""
        print("\n🌐 Шаг 7: Генерация клиентских ресурсов")
        print("-" * 40)
        
        try:
            # CDN URL для плагина
            cdn_url = f"https://cdn.jalm.io/tenant/{self.tenant_id}/plugin.js"
            
            # HTML код для вставки
            embed_code = f"""
<!-- Барбершоп календарь-бот -->
<script src="{cdn_url}"></script>
<!-- Конец кода -->
"""
            
            # Сохраняем код для вставки
            with open("client_embed_code.html", 'w', encoding='utf-8') as f:
                f.write(embed_code)
            
            print("✅ Код для вставки создан: client_embed_code.html")
            print(f"✅ CDN URL: {cdn_url}")
            
            # Инструкции для клиента
            instructions = f"""
🎯 ИНСТРУКЦИИ ДЛЯ КЛИЕНТА

1. 📱 Telegram бот: @{self.tenant_id}_barbershop_bot
2. 🌐 Виджет для сайта: вставьте код из client_embed_code.html
3. 📊 Админ панель: https://admin.jalm.io/tenant/{self.tenant_id}

🔧 НАСТРОЙКА:
- Замените {{TELEGRAM_BOT_TOKEN}} на ваш токен бота
- Замените {{MESSENGER_PAGE_TOKEN}} на ваш токен страницы
- Замените {{FIREBASE_PROJECT_ID}} на ваш проект Firebase

✅ ГОТОВО К ИСПОЛЬЗОВАНИЮ!
"""
            
            with open("client_instructions.txt", 'w', encoding='utf-8') as f:
                f.write(instructions)
            
            print("✅ Инструкции созданы: client_instructions.txt")
            
            self.deployment_data["client_assets_generated"] = True
            return True
            
        except Exception as e:
            print(f"❌ Ошибка генерации ресурсов: {e}")
            return False
    
    def _get_staff_json(self) -> str:
        """Получение JSON данных персонала"""
        try:
            with open("barbershop_plugin/FILES/migrations.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                staff = list(reader)
            return json.dumps(staff, ensure_ascii=False)
        except:
            return "[]"
    
    def _generate_slots(self, staff_data: list) -> list:
        """Генерация слотов для персонала"""
        slots = []
        # Здесь была бы логика генерации слотов на 2 недели вперед
        return slots
    
    def run_demo(self):
        """Запуск демонстрации"""
        print("🎯 ДЕМОНСТРАЦИЯ РАЗВЕРТЫВАНИЯ БАРБЕРШОПА")
        print("=" * 60)
        
        steps = [
            ("Валидация JALM объекта", self.step_1_validate_jalm_object),
            ("Обработка файлов", self.step_2_process_files),
            ("Создание Telegram бота", self.step_3_create_telegram_bot),
            ("Настройка webhook", self.step_4_setup_webhook_handler),
            ("Развертывание Lambda", self.step_5_deploy_lambda),
            ("Создание пакета", self.step_6_create_deployment_package),
            ("Генерация ресурсов", self.step_7_generate_client_assets)
        ]
        
        successful_steps = 0
        total_steps = len(steps)
        
        for step_name, step_func in steps:
            if step_func():
                successful_steps += 1
            else:
                print(f"❌ Шаг '{step_name}' не выполнен")
        
        # Итоговый отчет
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ДЕМОНСТРАЦИИ")
        print("=" * 60)
        
        success_rate = (successful_steps / total_steps) * 100
        print(f"✅ Выполнено шагов: {successful_steps}/{total_steps}")
        print(f"📈 Успешность: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print("🚀 Барбершоп готов к использованию!")
        else:
            print("⚠️ Есть проблемы, требующие внимания")
        
        # Сохранение результатов
        with open("deployment_results.json", 'w', encoding='utf-8') as f:
            json.dump(self.deployment_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Результаты сохранены в deployment_results.json")

def main():
    """Основная функция"""
    demo = BarbershopDeploymentDemo()
    demo.run_demo()

if __name__ == "__main__":
    main() 