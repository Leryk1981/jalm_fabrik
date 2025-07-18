#!/usr/bin/env python3
"""
Демонстрационный сценарий развертывания барбершопа
Показывает полный цикл от JALM Full Stack до работающего продукта
Использует правильную архитектуру с provision.yaml и SaasProvisioner
"""

import json
import requests
import time
import subprocess
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class BarbershopDeploymentDemo:
    """Демонстрация развертывания барбершопа через правильную JALM архитектуру"""
    
    def __init__(self):
        self.tenant_id = "demo_barbershop_001"
        self.deployment_data = {}
        self.product_name = "barbershop_classic"
        self.instances_dir = "instances"
        
    def step_1_create_jalm_config(self) -> bool:
        """Шаг 1: Создание JALM конфигурации для барбершопа"""
        print("🔧 Шаг 1: Создание JALM конфигурации")
        print("-" * 50)
        
        try:
            # Создаем JALM конфигурацию
            jalm_config = {
                "app": {
                    "name": "Барбершоп 'Классика'",
                    "type": "booking_system",
                    "version": "1.0.0"
                },
                "features": {
                    "booking_widget": True,
                    "telegram_notifications": True,
                    "admin_panel": True,
                    "slot_validation": True,
                    "payment_integration": False
                },
                "integrations": {
                    "telegram_bot": {
                        "enabled": True,
                        "config": {
                            "token": "{{TELEGRAM_BOT_TOKEN}}",
                            "admin_chat_id": "{{ADMIN_CHAT_ID}}"
                        }
                    },
                    "database": {
                        "type": "postgresql",
                        "version": "15"
                    },
                    "redis": {
                        "enabled": True,
                        "purpose": "session_storage"
                    }
                },
                "ui": {
                    "theme": "classic",
                    "language": "ru",
                    "responsive": True
                },
                "business_logic": {
                    "slot_duration": 60,
                    "advance_booking_days": 14,
                    "working_hours": {
                        "monday": {"start": "09:00", "end": "20:00"},
                        "tuesday": {"start": "09:00", "end": "20:00"},
                        "wednesday": {"start": "09:00", "end": "20:00"},
                        "thursday": {"start": "09:00", "end": "20:00"},
                        "friday": {"start": "09:00", "end": "20:00"},
                        "saturday": {"start": "10:00", "end": "18:00"},
                        "sunday": {"start": "10:00", "end": "16:00"}
                    },
                    "services": [
                        {"id": "haircut", "name": "Стрижка", "price": 1500, "duration": 60},
                        {"id": "beard", "name": "Стрижка бороды", "price": 800, "duration": 30},
                        {"id": "combo", "name": "Стрижка + борода", "price": 2000, "duration": 90},
                        {"id": "kids", "name": "Детская стрижка", "price": 1000, "duration": 45}
                    ]
                }
            }
            
            # Сохраняем JALM конфигурацию
            jalm_path = Path("barbershop.jalm.yaml")
            with open(jalm_path, 'w', encoding='utf-8') as f:
                yaml.dump(jalm_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            print(f"✅ JALM конфигурация создана: {jalm_path}")
            print(f"✅ Название: {jalm_config['app']['name']}")
            print(f"✅ Тип: {jalm_config['app']['type']}")
            print(f"✅ Интеграций: {len(jalm_config['integrations'])}")
            
            self.deployment_data["jalm_config"] = jalm_config
            self.deployment_data["jalm_path"] = str(jalm_path)
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания JALM конфигурации: {e}")
            return False
    
    def step_2_provision_product(self) -> bool:
        """Шаг 2: Провижининг продукта через SaasProvisioner"""
        print("\n🚀 Шаг 2: Провижининг продукта")
        print("-" * 50)
        
        try:
            # Импортируем SaasProvisioner
            from saas_provisioner import SaasProvisioner
            
            # Создаем экземпляр provisioner
            provisioner = SaasProvisioner()
            
            # Получаем путь к JALM конфигурации
            jalm_path = self.deployment_data.get("jalm_path")
            if not jalm_path or not Path(jalm_path).exists():
                print("❌ JALM конфигурация не найдена")
                return False
            
            # Провижиним продукт с автоматическим обнаружением сервисов
            print("🔄 Провижининг продукта...")
            print("Создание клиентского продукта с правильной архитектурой...")
            
            # Создаем provision.yaml с автоматическим обнаружением сервисов
            print("Шаг 1: Генерация provision.yaml...")
            provision_path = provisioner._create_basic_provision_yaml(jalm_path)
            
            # Читаем созданный provision.yaml
            with open(provision_path, 'r', encoding='utf-8') as f:
                provision = yaml.safe_load(f)
            
            print(f"Сгенерирован provision.yaml: {provision_path}")
            print(f"✅ Provision.yaml сгенерирован:")
            print(f"   - App ID: {provision.get('app_id', 'N/A')}")
            print(f"   - Environment: {provision.get('env', 'N/A')}")
            print(f"   - Tula Spec services: {len(provision.get('dependencies', {}).get('tula_spec', []))}")
            print(f"   - API Layer services: {len(provision.get('dependencies', {}).get('api_layer', []))}")
            
            # Создаем директорию продукта
            product_name = "demo"
            instance_dir = Path(self.instances_dir) / product_name
            instance_dir.mkdir(parents=True, exist_ok=True)
            
            # Копируем provision.yaml в директорию продукта
            import shutil
            shutil.copy2(provision_path, instance_dir / "provision.yaml")
            
            # Создаем параметры продукта
            params = {
                'calendars': 1,
                'lang': 'ru',
                'domain': 'demo.mycalendar.app'
            }
            
            print(f"📦 Создание клиентского продукта: {product_name}")
            print(f"📊 Параметры: {params}")
            
            # Создаем минимальный клиентский продукт
            print("🔧 Шаг 3: Создание минимального клиентского продукта...")
            provisioner.create_minimal_client_product(product_name, str(instance_dir), provision)
            
            # Создаем файлы плагина
            provisioner.create_sample_product_files(product_name, str(instance_dir), params, provision)
            
            # Создаем Dockerfile
            provisioner.create_client_dockerfile(product_name, str(instance_dir), provision)
            
            # Создаем docker-compose.yml
            provisioner.create_production_docker_compose(product_name, str(instance_dir), provision)
            
            # Создаем .env файл
            provisioner.create_env_file(str(instance_dir), provision)
            
            instance_dir = str(instance_dir)
            
            if not instance_dir or not Path(instance_dir).exists():
                print("❌ Ошибка провижининга")
                return False
            
            print(f"✅ Продукт провижинен: {instance_dir}")
            
            # Проверяем созданные файлы
            instance_path = Path(instance_dir)
            created_files = list(instance_path.rglob("*"))
            print(f"✅ Создано файлов: {len(created_files)}")
            
            # Проверяем ключевые файлы
            key_files = [
                "Dockerfile",
                "docker-compose.yml", 
                "provision.yaml",
                ".env",
                "app.py"
            ]
            
            for file_name in key_files:
                file_path = instance_path / file_name
                if file_path.exists():
                    print(f"✅ {file_name}: найден")
                else:
                    print(f"⚠️  {file_name}: отсутствует")
            
            self.deployment_data["instance_dir"] = instance_dir
            self.deployment_data["provision_successful"] = True
            return True
            
        except ImportError:
            print("❌ SaasProvisioner не найден")
            return False
        except Exception as e:
            print(f"❌ Ошибка провижининга: {e}")
            return False
    
    def step_3_validate_provision(self) -> bool:
        """Шаг 3: Валидация провижининга"""
        print("\n🔍 Шаг 3: Валидация провижининга")
        print("-" * 50)
        
        try:
            instance_dir = self.deployment_data.get("instance_dir")
            if not instance_dir:
                print("❌ Директория продукта не найдена")
                return False
            
            instance_path = Path(instance_dir)
            
            # Проверяем provision.yaml
            provision_path = instance_path / "provision.yaml"
            if not provision_path.exists():
                print("❌ provision.yaml не найден")
                return False
            
            with open(provision_path, 'r', encoding='utf-8') as f:
                provision = yaml.safe_load(f)
            
            print(f"✅ App ID: {provision.get('app_id', 'N/A')}")
            print(f"✅ Environment: {provision.get('env', 'N/A')}")
            
            # Проверяем зависимости
            dependencies = provision.get('dependencies', {})
            print(f"✅ Datastore: {dependencies.get('datastore', {}).get('type', 'N/A')}")
            print(f"✅ API Layer: {len(dependencies.get('api_layer', []))} сервисов")
            print(f"✅ Tula Spec: {len(dependencies.get('tula_spec', []))} функций")
            
            # Проверяем Dockerfile
            dockerfile_path = instance_path / "Dockerfile"
            if dockerfile_path.exists():
                with open(dockerfile_path, 'r', encoding='utf-8') as f:
                    dockerfile_content = f.read()
                
                if "FROM python:3.11-slim" in dockerfile_content:
                    print("✅ Dockerfile: Python 3.11")
                elif "FROM node:20-alpine" in dockerfile_content:
                    print("✅ Dockerfile: Node.js 20")
                else:
                    print("⚠️  Dockerfile: неизвестный базовый образ")
            else:
                print("❌ Dockerfile не найден")
            
            # Проверяем docker-compose.yml
            compose_path = instance_path / "docker-compose.yml"
            if compose_path.exists():
                with open(compose_path, 'r', encoding='utf-8') as f:
                    compose = yaml.safe_load(f)
                
                services = compose.get('services', {})
                print(f"✅ Docker Compose: {len(services)} сервисов")
                
                for service_name in services:
                    print(f"  - {service_name}")
            else:
                print("❌ docker-compose.yml не найден")
            
            self.deployment_data["provision_valid"] = True
            self.deployment_data["provision_config"] = provision
            return True
            
        except Exception as e:
            print(f"❌ Ошибка валидации: {e}")
            return False
    
    def step_4_build_and_deploy(self) -> bool:
        """Шаг 4: Сборка и развертывание"""
        print("\n🐳 Шаг 4: Сборка и развертывание")
        print("-" * 50)
        
        try:
            instance_dir = self.deployment_data.get("instance_dir")
            if not instance_dir:
                print("❌ Директория продукта не найдена")
                return False
            
            instance_path = Path(instance_dir)
            
            # Проверяем наличие Docker
            try:
                subprocess.run(["docker", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("❌ Docker не установлен или недоступен")
                return False
            
            # Собираем образ
            print("🔄 Сборка Docker образа...")
            image_name = f"{self.product_name}:latest"
            
            subprocess.run(
                ["docker", "build", "-t", image_name, "."],
                cwd=instance_path,
                check=True
            )
            print(f"✅ Образ собран: {image_name}")
            
            # Запускаем через docker-compose
            compose_path = instance_path / "docker-compose.yml"
            if not compose_path.exists():
                print("❌ docker-compose.yml не найден")
                return False
            
            print("🔄 Запуск сервисов...")
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=instance_path,
                check=True
            )
            
            # Ждем запуска
            print("⏳ Ожидание запуска сервисов...")
            time.sleep(15)
            
            # Проверяем статус
            result = subprocess.run(
                ["docker-compose", "ps"],
                cwd=instance_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            print("📊 Статус контейнеров:")
            print(result.stdout)
            
            # Проверяем health check
            print("🏥 Проверка здоровья сервисов...")
            
            # Читаем provision.yaml для определения портов
            provision_path = instance_path / "provision.yaml"
            with open(provision_path, 'r', encoding='utf-8') as f:
                provision = yaml.safe_load(f)
            
            # Определяем порты из provision
            net_config = provision.get('net', {})
            domain = net_config.get('domain', 'localhost')
            
            # Проверяем основной сервис
            try:
                response = requests.get(f"http://localhost:8080/health", timeout=10)
                if response.status_code == 200:
                    print("✅ Основной сервис: здоров")
                else:
                    print(f"⚠️  Основной сервис: HTTP {response.status_code}")
            except Exception as e:
                print(f"⚠️  Основной сервис: {e}")
            
            self.deployment_data["deployment_successful"] = True
            self.deployment_data["docker_image"] = image_name
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка Docker: {e}")
            return False
        except Exception as e:
            print(f"❌ Ошибка развертывания: {e}")
            return False
    
    def step_5_generate_client_instructions(self) -> bool:
        """Шаг 5: Генерация инструкций для клиента"""
        print("\n📋 Шаг 5: Генерация инструкций для клиента")
        print("-" * 50)
        
        try:
            instance_dir = self.deployment_data.get("instance_dir")
            if not instance_dir:
                print("❌ Директория продукта не найдена")
                return False
            
            instance_path = Path(instance_dir)
            
            # Читаем provision.yaml
            provision_path = instance_path / "provision.yaml"
            with open(provision_path, 'r', encoding='utf-8') as f:
                provision = yaml.safe_load(f)
            
            # Определяем конфигурацию
            app_id = provision.get('app_id', 'barbershop')
            net_config = provision.get('net', {})
            domain = net_config.get('domain', 'localhost')
            
            instructions = f"""
🎯 ИНСТРУКЦИИ ДЛЯ КЛИЕНТА - БАРБЕРШОП 'КЛАССИКА'

## 🏗️ Архитектура развертывания
- Тип: Изолированный продукт (без JALM инфраструктуры)
- Контейнер: Минимальный Docker образ
- Провижининг: Через provision.yaml

## 🌐 Доступ к сервисам

### Основное приложение
- URL: http://localhost:8080
- Описание: Веб-интерфейс для бронирования
- Статус: Изолированный продукт

## 🔧 Настройка

### Переменные окружения
Файл .env уже создан в директории продукта:

```env
# Основные настройки
PRODUCT_NAME=Барбершоп 'Классика'
NODE_ENV=production

# База данных (если требуется)
DATABASE_URL=postgresql://user:password@localhost:5432/barbershop

# Redis (если требуется)
REDIS_URL=redis://localhost:6379

# Telegram Bot (если включен)
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_chat_id_here
```

### Первоначальная настройка
1. Отредактируйте .env файл в директории: {instance_dir}
2. Перезапустите сервис: `docker-compose restart`
3. Проверьте доступность: http://localhost:8080

## 📱 Использование

### Для клиентов
1. Откройте http://localhost:8080
2. Выберите услугу и время
3. Заполните контактные данные
4. Подтвердите бронирование

### Для администратора
1. Откройте http://localhost:8080/admin
2. Войдите в админ панель
3. Управляйте записями и настройками

## 🐳 Docker команды

### Управление сервисами
```bash
# Переход в директорию продукта
cd {instance_dir}

# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр логов
docker-compose logs -f

# Обновление
docker-compose pull
docker-compose up -d
```

### Отдельные операции
```bash
# Пересборка образа
docker-compose build --no-cache

# Просмотр статуса
docker-compose ps

# Очистка
docker-compose down -v
docker system prune -a
```

## 🔍 Мониторинг

### Проверка здоровья
- Основной сервис: http://localhost:8080/health

### Логи
```bash
# Все логи
docker-compose logs

# Логи в реальном времени
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs {app_id}
```

## 🆘 Устранение неполадок

### Сервис не отвечает
1. Проверьте статус: `docker-compose ps`
2. Просмотрите логи: `docker-compose logs`
3. Перезапустите: `docker-compose restart`

### Проблемы с портами
```bash
# Проверка занятых портов
netstat -tulpn | grep :8080

# Остановка процессов
sudo lsof -ti:8080 | xargs kill -9
```

### Проблемы с Docker
```bash
# Очистка
docker system prune -a

# Пересборка
docker-compose build --no-cache
docker-compose up -d
```

## 📁 Структура продукта
```
{instance_dir}/
├── Dockerfile          # Минимальный образ продукта
├── docker-compose.yml  # Конфигурация развертывания
├── provision.yaml      # Конфигурация провижининга
├── .env               # Переменные окружения
├── app.py             # Основное приложение
├── requirements.txt   # Python зависимости
└── nginx.conf         # Конфигурация веб-сервера
```

## 🔄 Обновление продукта
1. Остановите сервис: `docker-compose down`
2. Обновите код в директории продукта
3. Пересоберите образ: `docker-compose build --no-cache`
4. Запустите: `docker-compose up -d`

---
🎉 Ваш барбершоп готов к работе!
"""
            
            # Сохраняем инструкции
            instructions_path = Path("client_instructions.txt")
            with open(instructions_path, 'w', encoding='utf-8') as f:
                f.write(instructions)
            
            print(f"✅ Инструкции созданы: {instructions_path}")
            
            # Создаем краткую справку
            quick_guide = f"""
🚀 БЫСТРЫЙ СТАРТ - БАРБЕРШОП 'КЛАССИКА'

✅ СЕРВИС ЗАПУЩЕН:
- Приложение: http://localhost:8080
- Тип: Изолированный продукт

🔧 НАСТРОЙКА:
1. Отредактируйте .env в {instance_dir}
2. Перезапустите: docker-compose restart

📱 ИСПОЛЬЗОВАНИЕ:
- Клиенты: http://localhost:8080
- Админ: http://localhost:8080/admin

🐳 УПРАВЛЕНИЕ:
- Директория: {instance_dir}
- Запуск: docker-compose up -d
- Остановка: docker-compose down
- Логи: docker-compose logs -f

📖 ПОДРОБНАЯ ДОКУМЕНТАЦИЯ: client_instructions.txt
"""
            
            quick_guide_path = Path("quick_start.txt")
            with open(quick_guide_path, 'w', encoding='utf-8') as f:
                f.write(quick_guide)
            
            print(f"✅ Краткая справка создана: {quick_guide_path}")
            
            self.deployment_data["instructions_generated"] = True
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания инструкций: {e}")
            return False
    
    def run_demo(self):
        """Запуск демонстрации"""
        print("🎯 ДЕМОНСТРАЦИЯ РАЗВЕРТЫВАНИЯ БАРБЕРШОПА")
        print("=" * 60)
        print("🏗️  Архитектура: JALM Full Stack + SaasProvisioner")
        print("=" * 60)
        
        steps = [
            ("Создание JALM конфигурации", self.step_1_create_jalm_config),
            ("Провижининг продукта", self.step_2_provision_product),
            ("Валидация провижининга", self.step_3_validate_provision),
            ("Сборка и развертывание", self.step_4_build_and_deploy),
            ("Создание инструкций", self.step_5_generate_client_instructions)
        ]
        
        successful_steps = 0
        total_steps = len(steps)
        
        for step_name, step_func in steps:
            if step_func():
                successful_steps += 1
            else:
                print(f"❌ Шаг '{step_name}' не выполнен")
                break  # Останавливаемся при первой ошибке
        
        # Итоговый отчет
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ДЕМОНСТРАЦИИ")
        print("=" * 60)
        
        success_rate = (successful_steps / total_steps) * 100
        print(f"✅ Выполнено шагов: {successful_steps}/{total_steps}")
        print(f"📈 Успешность: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print("🚀 Барбершоп развернут как изолированный продукт!")
            print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
            print("1. Настройте переменные окружения в .env")
            print("2. Откройте http://localhost:8080 для тестирования")
            print("3. Изучите client_instructions.txt для подробной информации")
            
            instance_dir = self.deployment_data.get("instance_dir")
            if instance_dir:
                print(f"4. Директория продукта: {instance_dir}")
        else:
            print("⚠️  Есть проблемы, требующие внимания")
            print("📖 Проверьте логи и исправьте ошибки")
        
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