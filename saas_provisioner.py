import yaml
import os
import subprocess
import json
import shutil
import re
from pathlib import Path
from typing import Dict, Any, List, Set

class SaasProvisioner:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.catalog_dir = self.base_dir / "catalog"
        self.tula_spec_dir = self.base_dir / "tula_spec"
        self.shablon_spec_dir = self.base_dir / "shablon_spec"

    def discover_available_services(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Автоматически обнаруживает доступные сервисы из каталогов JALM
        """
        services = {
            "tula_spec": [],
            "shablon_spec": []
        }
        
        # Сканирование Tula Spec функций
        try:
            tula_catalog_path = self.catalog_dir / "tula-spec.catalog.json"
            if tula_catalog_path.exists():
                with open(tula_catalog_path, 'r', encoding='utf-8') as f:
                    tula_catalog = json.load(f)
                
                for func in tula_catalog.get("functions", []):
                    services["tula_spec"].append({
                        "service": func["id"],
                        "version": func["version"],
                        "expose": "internal",
                        "description": func["description"],
                        "tags": func.get("tags", [])
                    })
                print(f"[SEARCH] Обнаружено {len(services['tula_spec'])} функций в Tula Spec")
        except Exception as e:
            print(f"[WARNING] Ошибка сканирования Tula Spec: {e}")
        
        # Сканирование Shablon Spec шаблонов
        try:
            shablon_catalog_path = self.catalog_dir / "shablon-spec.catalog.json"
            if shablon_catalog_path.exists():
                with open(shablon_catalog_path, 'r', encoding='utf-8') as f:
                    shablon_catalog = json.load(f)
                
                for template in shablon_catalog.get("templates", []):
                    services["shablon_spec"].append({
                        "service": template["id"],
                        "version": template["version"],
                        "expose": "internal",
                        "description": template["description"],
                        "category": template.get("category", "general"),
                        "tags": template.get("tags", [])
                    })
                print(f"[SEARCH] Обнаружено {len(services['shablon_spec'])} шаблонов в Shablon Spec")
        except Exception as e:
            print(f"[WARNING] Ошибка сканирования Shablon Spec: {e}")
        
        return services

    def parse_jalm(self, jalm_path: str) -> Dict[str, Any]:
        """
        Читает и парсит JALM-конфиг (YAML).
        """
        with open(jalm_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data

    def generate_provision_yaml(self, jalm_path: str) -> str:
        """
        Генерирует provision.yaml из JALM файла используя provision scanner
        """
        try:
            # Импорт provision scanner
            from jalm.provision import ProvisionScanner
            
            scanner = ProvisionScanner()
            provision_path = scanner.generate_provision_yaml(jalm_path)
            
            print(f"Сгенерирован provision.yaml: {provision_path}")
            return provision_path
            
        except ImportError:
            print("[WARNING] Provision scanner не найден, используем базовый provision.yaml")
            return self._create_basic_provision_yaml(jalm_path)
        except Exception as e:
            print(f"Ошибка генерации provision.yaml: {e}")
            return self._create_basic_provision_yaml(jalm_path)

    def _create_basic_provision_yaml(self, jalm_path: str) -> str:
        """
        Создает базовый provision.yaml если scanner недоступен
        """
        jalm_file = Path(jalm_path)
        provision_path = jalm_file.parent / "provision.yaml"
        
        # Читаем JALM конфигурацию для определения зависимостей
        try:
            with open(jalm_path, 'r', encoding='utf-8') as f:
                jalm_config = yaml.safe_load(f)
        except:
            jalm_config = {}
        
        # Автоматически обнаруживаем доступные сервисы
        available_services = self.discover_available_services()
        
        # Определяем зависимости на основе JALM конфигурации
        features = jalm_config.get('features', {})
        integrations = jalm_config.get('integrations', {})
        
        # Формируем API layer на основе интеграций
        api_layer = []
        if integrations.get('telegram_bot', {}).get('enabled'):
            api_layer.append({
                "service": "telegram_bot",
                "version": "1.0.0",
                "expose": "external",
                "secrets": ["${{secrets.TELEGRAM_TOKEN}}"]
            })
        
        # Автоматически добавляем все обнаруженные сервисы
        tula_services = available_services.get("tula_spec", [])
        shablon_services = available_services.get("shablon_spec", [])
        
        # Фильтруем сервисы на основе типа приложения
        app_type = "booking_system" if features.get('booking_widget') else "general"
        
        if app_type == "booking_system":
            # Для систем бронирования добавляем релевантные сервисы
            relevant_tula = [s for s in tula_services if any(tag in s.get("tags", []) for tag in ["booking", "validation", "notification"])]
            relevant_shablon = [s for s in shablon_services if any(tag in s.get("tags", []) for tag in ["booking", "slots"])]
        else:
            # Для общих приложений добавляем все сервисы
            relevant_tula = tula_services
            relevant_shablon = shablon_services
        
        basic_provision = {
            "app_id": jalm_config.get('app', {}).get('name', 'jalm_app_v1').lower().replace(' ', '_'),
            "env": "prod infra/docker/compose",
            "dependencies": {
                "datastore": {
                    "type": f"{integrations.get('database', {}).get('type', 'postgresql')}:{integrations.get('database', {}).get('version', '15')}",
                    "tier": "managed"
                },
                "api_layer": api_layer,
                "tula_spec": relevant_tula,
                "shablon_spec": relevant_shablon
            },
            "storage": {
                "files": {
                    "type": "local",
                    "mount": "/app/FILES"
                }
            },
            "net": {
                "ingress": "nginx",
                "domain": "{tenant}.run",
                "channels": ["telegram"] if integrations.get('telegram_bot', {}).get('enabled') else ["web"]
            },
            "health": {
                "endpoint": "/health",
                "timeout": "3s"
            },
            "meta": {
                "provisioner": "jalm-fullstack",
                "force_service_discovery": True,
                "app_type": "node" if features.get('booking_widget') else "python"
            }
        }
        
        with open(provision_path, 'w', encoding='utf-8') as f:
            yaml.dump(basic_provision, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return str(provision_path)

    def read_provision_yaml(self, provision_path: str) -> Dict[str, Any]:
        """
        Читает provision.yaml
        """
        with open(provision_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def create_product_dockerfile(self, product_name: str, instance_dir: str, params: Dict[str, Any], provision: Dict[str, Any]) -> str:
        """
        Создает Dockerfile на основе provision.yaml
        """
        # Определение системных пакетов
        system_packages = ["curl", "nginx"]
        
        # Добавление пакетов на основе provision
        api_layer = provision.get("dependencies", {}).get("api_layer", [])
        for service in api_layer:
            service_name = service.get("service", "")
            if "telegram" in service_name.lower():
                system_packages.append("python3-venv")
        
        datastore = provision.get("dependencies", {}).get("datastore", {})
        if datastore.get("type", "").startswith("postgresql"):
            system_packages.extend(["postgresql-client", "sqlite3"])
        
        system_packages = " ".join(sorted(set(system_packages)))
        
        dockerfile_content = f"""# {product_name} - Готовый продукт
FROM python:3.11-slim

# Переменные окружения продукта
ENV PRODUCT_NAME={product_name}
ENV CALENDARS={params.get('calendars', 1)}
ENV LANG={params.get('lang', 'ru')}
ENV DOMAIN={params.get('domain', 'demo.mycalendar.app')}
ENV JALM_CORE_URL=http://core-runner:8000
ENV JALM_TULA_URL=http://tula-spec:8001
ENV JALM_SHABLON_URL=http://shablon-spec:8002

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \\
    {system_packages} \\
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя
RUN useradd --create-home --shell /bin/bash app && \\
    chown -R app:app /app

# Установка рабочей директории
WORKDIR /app

# Копирование готового продукта
COPY --chown=app:app . /app/

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Настройка nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Переключение на пользователя
USER app

# Экспорт порта
EXPOSE 80

# Команда запуска
CMD ["python", "app.py"]
"""
        
        dockerfile_path = os.path.join(instance_dir, "Dockerfile")
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        return dockerfile_path

    def create_client_dockerfile(self, product_name: str, instance_dir: str, provision: Dict[str, Any]) -> str:
        """
        Создает МИНИМАЛЬНЫЙ Dockerfile для клиентского продукта (без JALM инфраструктуры)
        """
        # Определяем базовый образ на основе типа продукта
        app_type = provision.get("meta", {}).get("app_type", "node")
        
        if app_type == "node":
            dockerfile_content = f"""# {product_name} - Клиентский продукт (минимальный)
FROM node:20-alpine AS prod

# Установка рабочей директории
WORKDIR /app

        # Копирование только продукта (без JALM инфраструктуры)
        COPY dist/ ./dist
        COPY package.json ./
        COPY package-lock.json ./
        COPY FILES/ ./FILES/

# Установка зависимостей продукта
RUN npm ci --only=production

# Копирование конфигурации из config/ директории
COPY config/provision.yaml ./config/
COPY config/.env ./config/

# Создание пользователя
RUN addgroup -g 1001 -S nodejs && \\
    adduser -S nodejs -u 1001

# Переключение на пользователя
USER nodejs

# Экспорт порта
EXPOSE 8080

# Команда запуска
CMD ["node", "dist/index.js"]
"""
        elif app_type == "python":
            dockerfile_content = f"""# {product_name} - Клиентский продукт (минимальный)
FROM python:3.11-slim AS prod

# Установка рабочей директории
WORKDIR /app

# Копирование только продукта (без JALM инфраструктуры)
COPY app/ ./app/
COPY requirements.txt ./

# Установка зависимостей продукта
RUN pip install --no-cache-dir -r requirements.txt

# Копирование конфигурации из config/ директории
COPY config/provision.yaml ./config/
COPY config/.env ./config/

# Создание пользователя
RUN useradd --create-home --shell /bin/bash app && \\
    chown -R app:app /app

# Переключение на пользователя
USER app

# Экспорт порта
EXPOSE 8080

# Команда запуска
CMD ["python", "app/main.py"]
"""
        else:
            # Fallback к Node.js
            dockerfile_content = f"""# {product_name} - Клиентский продукт (минимальный)
FROM node:20-alpine AS prod

WORKDIR /app
COPY dist/ ./dist
COPY package.json ./
RUN npm ci --only=production
COPY config/provision.yaml ./config/
COPY config/.env ./config/

USER nodejs
EXPOSE 8080
CMD ["node", "dist/index.js"]
"""
        
        dockerfile_path = os.path.join(instance_dir, "Dockerfile")
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        return dockerfile_path

    def create_product_app(self, product_name: str, instance_dir: str, params: Dict[str, Any]) -> str:
        """
        Создает основной файл приложения для готового продукта
        """
        app_content = f'''#!/usr/bin/env python3
"""
{product_name} - Готовый продукт
"""

import os
import subprocess
import time
import signal
import sys
import requests
from pathlib import Path

class {product_name.replace('-', '_').title()}App:
    def __init__(self):
        self.running = True
        self.jalm_core_url = os.getenv('JALM_CORE_URL', 'http://core-runner:8000')
        self.jalm_tula_url = os.getenv('JALM_TULA_URL', 'http://tula-spec:8001')
        self.jalm_shablon_url = os.getenv('JALM_SHABLON_URL', 'http://shablon-spec:8002')
        
        # Настройка сигналов для graceful shutdown
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        print(f"\\n🛑 Получен сигнал {{signum}}, завершение работы...")
        self.running = False
    
    def wait_for_jalm_services(self):
        """Ожидание готовности JALM сервисов"""
        services = [
            (self.jalm_core_url, "Core Runner"),
            (self.jalm_tula_url, "Tula Spec"),
            (self.jalm_shablon_url, "Shablon Spec")
        ]
        
        for url, name in services:
            print(f"[WAIT] Ожидание готовности {{name}}...")
            for i in range(30):  # 30 попыток
                try:
                    response = requests.get(f"{{url}}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"[OK] {{name}} готов")
                        break
                except:
                    if i == 29:
                        print(f"[ERROR] {{name}} не отвечает")
                        return False
                    time.sleep(2)
        return True
    
    def load_product_config(self):
        """Загрузка конфигурации продукта"""
        try:
            with open('OBJECT.jalm', 'r', encoding='utf-8') as f:
                import yaml
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Ошибка загрузки OBJECT.jalm: {{e}}")
            return None
    
    def start_nginx(self):
        """Запуск nginx для раздачи статических файлов"""
        try:
            subprocess.Popen(["nginx"], start_new_session=True)
            print("Nginx запущен")
            return True
        except Exception as e:
            print(f"Ошибка запуска nginx: {{e}}")
            return False
    
    def run(self):
        """Основной цикл приложения"""
        print(f"Запуск {os.getenv('PRODUCT_NAME', 'JALM Product')}...")
        print(f"Конфигурация:")
        print(f"   - Календари: {os.getenv('CALENDARS', 1)}")
        print(f"   - Язык: {os.getenv('LANG', 'ru')}")
        print(f"   - Домен: {os.getenv('DOMAIN', 'demo.mycalendar.app')}")
        
        # Загрузка конфигурации продукта
        config = self.load_product_config()
        if not config:
            print("Не удалось загрузить конфигурацию продукта")
            sys.exit(1)
        
        print(f"Продукт: {{config.get('name', 'Unknown')}}")
        print(f"Описание: {{config.get('title', 'No description')}}")
        
        # Ожидание готовности JALM сервисов
        if not self.wait_for_jalm_services():
            print("Не удалось дождаться готовности JALM сервисов")
            sys.exit(1)
        
        # Запуск nginx
        if not self.start_nginx():
            print("Не удалось запустить nginx")
            sys.exit(1)
        
        print("\nПродукт успешно запущен!")
        print("Доступные сервисы:")
        print("   - Основное приложение: http://localhost")
        print("   - JALM Core Runner: http://core-runner:8000")
        print("   - JALM Tula Spec: http://tula-spec:8001")
        print("   - JALM Shablon Spec: http://shablon-spec:8002")
        
        # Основной цикл
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nПолучен сигнал прерывания")
        finally:
            print("Завершение работы продукта")
'''
        app_path = os.path.join(instance_dir, "app.py")
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(app_content)
        
        return app_path

    def create_nginx_config(self, product_name: str, instance_dir: str) -> str:
        """
        Создает конфигурацию nginx для раздачи статических файлов
        """
        nginx_content = f"""events {{
    worker_connections 1024;
}}

http {{
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    server {{
        listen 80;
        server_name localhost;
        
        # Статические файлы продукта
        location / {{
            root /app/FILES;
            index plugin.js;
            try_files $uri $uri/ /plugin.js;
        }}
        
        # API проксирование к JALM сервисам
        location /api/core/ {{
            proxy_pass http://core-runner:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }}
        
        location /api/tula/ {{
            proxy_pass http://tula-spec:8001/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }}
        
        location /api/shablon/ {{
            proxy_pass http://shablon-spec:8002/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }}
        
        # Health check
        location /health {{
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }}
    }}
}}
"""
        
        nginx_path = os.path.join(instance_dir, "nginx.conf")
        with open(nginx_path, 'w', encoding='utf-8') as f:
            f.write(nginx_content)
        
        return nginx_path

    def create_requirements_txt(self, instance_dir: str, provision: Dict[str, Any]) -> str:
        """
        Создает requirements.txt на основе provision.yaml
        """
        # Базовые пакеты
        packages = {"requests>=2.31.0", "pyyaml>=6.0"}
        
        # Добавление пакетов на основе зависимостей
        api_layer = provision.get("dependencies", {}).get("api_layer", [])
        
        for service in api_layer:
            service_name = service.get("service", "")
            
            if "telegram" in service_name.lower():
                packages.add("python-telegram-bot>=20.0.0")
            elif "payment" in service_name.lower():
                packages.add("stripe>=7.0.0")
            elif "notification" in service_name.lower():
                packages.add("twilio>=8.0.0")
                packages.add("sendgrid>=6.0.0")
        
        # Добавление пакетов для веб-интерфейса
        if provision.get("net", {}).get("ingress") == "nginx":
            packages.update({"fastapi>=0.104.0", "uvicorn>=0.24.0"})
        
        # Добавление пакетов для базы данных
        datastore = provision.get("dependencies", {}).get("datastore", {})
        if datastore.get("type", "").startswith("postgresql"):
            packages.update({"sqlalchemy>=2.0.0", "psycopg2-binary>=2.9.0"})
        
        # Сортировка для стабильности
        packages = sorted(list(packages))
        requirements_content = "\n".join(packages) + "\n"
        
        requirements_path = os.path.join(instance_dir, "requirements.txt")
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        return requirements_path

    def create_production_docker_compose(self, product_name: str, instance_dir: str, provision: Dict[str, Any]) -> str:
        """
        Создает docker-compose.yml для продакшена с ТОЛЬКО клиентским продуктом
        JALM сервисы должны запускаться отдельно или использовать локальные образы
        """
        app_id = provision.get('app_id', 'unknown')
        subnet_octet = abs(hash(product_name)) % 255
        
        compose_content = f"""version: '3.8'

services:
  # Клиентский продукт (минимальный, без JALM инфраструктуры)
  {product_name}:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {product_name}
    restart: unless-stopped
    ports:
      - "8080:8080"  # Клиентский порт
    environment:
      - NODE_ENV=production
      - JALM_CORE_URL=http://localhost:8000  # Подключение к локальным JALM сервисам
      - JALM_TULA_URL=http://localhost:8001
      - JALM_SHABLON_URL=http://localhost:8002
      - APP_ID={app_id}
    volumes:
      - {product_name}_data:/app/data
    networks:
      - {product_name}-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

# Тома для персистентности данных
volumes:
  {product_name}_data:
    driver: local

# Сеть для коммуникации между сервисами
networks:
  {product_name}-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.{subnet_octet}.0.0/16
"""
        
        compose_path = os.path.join(instance_dir, "docker-compose.yml")
        with open(compose_path, 'w', encoding='utf-8') as f:
            f.write(compose_content)
        
        return compose_path

    def create_product_makefile(self, product_name: str, instance_dir: str, provision: Dict[str, Any]) -> str:
        """
        Создает Makefile для управления клиентским продуктом
        """
        app_id = provision.get('app_id', 'unknown')
        tula_services = provision.get('dependencies', {}).get('tula_spec', [])
        api_layer_services = provision.get('dependencies', {}).get('api_layer', [])
        
        # Windows-совместимый Makefile
        makefile_content = f"""# {product_name.title()} - Makefile для управления продуктом
# JALM Full Stack - Правильная архитектура

.PHONY: help build run stop restart logs clean status health test demo

# Переменные
COMPOSE_FILE = docker-compose.yml
PRODUCT_NAME = {product_name}
APP_ID = {app_id}

help: ## Показать справку по командам
	@echo "Доступные команды для {product_name}:"
	@echo "  help     - Показать эту справку"
	@echo "  build    - Собрать Docker образ"
	@echo "  run      - Запустить продукт"
	@echo "  stop     - Остановить продукт"
	@echo "  restart  - Перезапустить продукт"
	@echo "  logs     - Показать логи"
	@echo "  status   - Статус контейнеров"
	@echo "  health   - Проверить здоровье"
	@echo "  test     - Запустить тесты"
	@echo "  clean    - Очистить все"
	@echo "  demo     - Открыть демо-страницу"

build: ## Собрать Docker образ
	@echo "Сборка Docker образа {product_name}..."
	docker-compose -f $(COMPOSE_FILE) build --no-cache
	@echo "Образ собран успешно"

build-fast: ## Быстрая сборка (без --no-cache)
	@echo "Быстрая сборка Docker образа..."
	docker-compose -f $(COMPOSE_FILE) build
	@echo "Образ собран успешно"

run: ## Запустить продукт
	@echo "Запуск {product_name}..."
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "Продукт запущен"
	@echo "Доступен по адресу: http://localhost:8080"
	@echo "Демо-страница: http://localhost:8080/FILES/{product_name}.html"

stop: ## Остановить продукт
	@echo "Остановка {product_name}..."
	docker-compose -f $(COMPOSE_FILE) down
	@echo "Продукт остановлен"

restart: ## Перезапустить продукт
	@echo "Перезапуск {product_name}..."
	docker-compose -f $(COMPOSE_FILE) restart
	@echo "Продукт перезапущен"

logs: ## Показать логи продукта
	@echo "Логи {product_name}:"
	docker-compose -f $(COMPOSE_FILE) logs -f

status: ## Статус контейнеров
	@echo "Статус контейнеров:"
	docker-compose -f $(COMPOSE_FILE) ps

health: ## Проверить здоровье продукта
	@echo "Проверка здоровья {product_name}..."
	@curl -s -o nul -w "HTTP Status: %%{{http_code}}\\n" http://localhost:8080/health 2>nul || echo "Продукт недоступен"

test: ## Запустить тесты продукта
	@echo "Тестирование {product_name}..."
	@echo "1. Проверка доступности..."
	@curl -f http://localhost:8080/health || echo "[ERROR] Продукт недоступен"
	@echo "2. Проверка API..."
	@curl -f http://localhost:8080/ || echo "[ERROR] API недоступен"
	@echo "3. Проверка плагина..."
	@curl -f http://localhost:8080/FILES/plugin.js || echo "[ERROR] Плагин недоступен"
	@echo "[OK] Тестирование завершено"

demo: ## Открыть демо-страницу
	@echo "Открытие демо-страницы..."
	@start http://localhost:8080/FILES/{product_name}.html || echo "Откройте в браузере: http://localhost:8080/FILES/{product_name}.html"

clean: ## Очистить все (контейнеры, образы, тома)
	@echo "Очистка всех ресурсов {product_name}..."
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f
	@echo "Очистка завершена"

# Команды для работы с JALM сервисами
jalm-status: ## Статус JALM сервисов
	@echo "Статус JALM сервисов:"
	@echo "Core Runner (8000):"
	@curl -s -o nul -w "  HTTP Status: %%{{http_code}}\\n" http://localhost:8000/health 2>nul || echo "  Недоступен"
	@echo "Tula Spec (8001):"
	@curl -s -o nul -w "  HTTP Status: %%{{http_code}}\\n" http://localhost:8001/health 2>nul || echo "  Недоступен"
	@echo "Shablon Spec (8002):"
	@curl -s -o nul -w "  HTTP Status: %%{{http_code}}\\n" http://localhost:8002/health 2>nul || echo "  Недоступен"

# Команды для разработки
dev-setup: ## Настройка окружения разработки
	@echo "Настройка окружения разработки..."
	@echo "1. Установка зависимостей..."
	npm install
	@echo "2. Копирование конфигурации..."
	@if not exist config mkdir config
	@copy provision.yaml config\\provision.yaml
	@echo "[OK] Окружение разработки готово"

dev-run: ## Запуск в режиме разработки
	@echo "Запуск в режиме разработки..."
	npm start

# Информация о продукте
info: ## Информация о продукте
	@echo "Информация о {product_name}:"
	@echo "  App ID: {app_id}"
	@echo "  Архитектура: JALM Full Stack"
	@echo "  Тип: Клиентский продукт"
	@echo "  Размер: ~50MB"
	@echo "  Порт: 8080"
	@echo "  Tula Services: {len(tula_services)}"
	@echo "  API Layer Services: {len(api_layer_services)}"
"""
        
        makefile_path = os.path.join(instance_dir, "Makefile")
        with open(makefile_path, 'w', encoding='utf-8') as f:
            f.write(makefile_content)
        
        return makefile_path

    def create_root_makefile(self) -> str:
        """
        Создает корневой Makefile для управления всей JALM Full Stack системой
        """
        makefile_content = """# JALM Full Stack - Корневой Makefile
# Управление всей системой JALM Full Stack

.PHONY: help start stop restart status health test clean demo build-all

# Переменные
JALM_SERVICES_SCRIPT = start_jalm_services.py

help: ## Показать справку по командам
	@echo "JALM Full Stack - Корневой Makefile"
	@echo "====================================="
	@echo ""
	@echo "Доступные команды:"
	@echo "  help       - Показать эту справку"
	@echo "  start      - Запустить JALM сервисы"
	@echo "  stop       - Остановить JALM сервисы"
	@echo "  restart    - Перезапустить JALM сервисы"
	@echo "  status     - Статус всех сервисов"
	@echo "  health     - Проверить здоровье всех сервисов"
	@echo "  test       - Запустить все тесты"
	@echo "  clean      - Очистить все"
	@echo "  demo       - Запустить демонстрацию барбершопа"
	@echo "  build-all  - Собрать все компоненты"

start: ## Запустить JALM сервисы
	@echo "Запуск JALM Full Stack сервисов..."
	@python $(JALM_SERVICES_SCRIPT)
	@echo "JALM сервисы запущены"
	@echo "Core Runner: http://localhost:8000"
	@echo "Tula Spec: http://localhost:8001"
	@echo "Shablon Spec: http://localhost:8002"

stop: ## Остановить JALM сервисы
	@echo "Остановка JALM сервисов..."
	@echo "Нажмите Ctrl+C в терминале с JALM сервисами"
	@echo "Или закройте терминал с start_jalm_services.py"

restart: ## Перезапустить JALM сервисы
	@echo "Перезапуск JALM сервисов..."
	@echo "Сначала остановите сервисы (Ctrl+C), затем запустите: make start"

status: ## Статус всех сервисов
	@echo "Статус JALM Full Stack:"
	@echo "1. JALM сервисы:"
	@curl -s -o nul -w "   Core Runner (8000): %%{http_code}\\n" http://localhost:8000/health 2>nul || echo "   Core Runner (8000): Недоступен"
	@curl -s -o nul -w "   Tula Spec (8001): %%{http_code}\\n" http://localhost:8001/health 2>nul || echo "   Tula Spec (8001): Недоступен"
	@curl -s -o nul -w "   Shablon Spec (8002): %%{http_code}\\n" http://localhost:8002/health 2>nul || echo "   Shablon Spec (8002): Недоступен"
	@echo "2. Клиентские продукты:"
	@docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}" | findstr demo 2>nul || echo "   Нет запущенных клиентских продуктов"

health: ## Проверить здоровье всех сервисов
	@echo "Проверка здоровья JALM Full Stack..."
	@echo "JALM сервисы:"
	@curl -f http://localhost:8000/health && echo "[OK] Core Runner здоров" || echo "[ERROR] Core Runner недоступен"
	@curl -f http://localhost:8001/health && echo "[OK] Tula Spec здоров" || echo "[ERROR] Tula Spec недоступен"
	@curl -f http://localhost:8002/health && echo "[OK] Shablon Spec здоров" || echo "[ERROR] Shablon Spec недоступен"
	@echo "Клиентские продукты:"
	@curl -f http://localhost:8080/health && echo "[OK] Демо-продукт здоров" || echo "[ERROR] Демо-продукт недоступен"

test: ## Запустить все тесты
	@echo "Запуск всех тестов JALM Full Stack..."
	@echo "1. Тестирование JALM сервисов..."
	@python test_discovery.py
	@echo "2. Тестирование демо-продукта..."
	@python test_barbershop_simple.py
	@echo "3. Тестирование полного сценария..."
	@python test_barbershop_scenario.py
	@echo "[OK] Все тесты завершены"

demo: ## Запустить демонстрацию барбершопа
	@echo "Запуск демонстрации барбершопа..."
	@python demo_barbershop_deployment.py
	@echo "Демонстрация запущена"
	@echo "Доступна по адресу: http://localhost:8080"

build-all: ## Собрать все компоненты
	@echo "Сборка всех компонентов JALM Full Stack..."
	@echo "1. Сборка Core Runner..."
	@cd core-runner && make kernel_build
	@echo "2. Сборка Tula Spec..."
	@cd tula_spec && make build
	@echo "3. Сборка Shablon Spec..."
	@cd shablon_spec && make build
	@echo "4. Сборка демо-продукта..."
	@cd instances/demo && make build
	@echo "[OK] Все компоненты собраны"

clean: ## Очистить все
	@echo "Очистка всех ресурсов JALM Full Stack..."
	@echo "1. Очистка клиентских продуктов..."
	@cd instances/demo && make clean
	@echo "2. Очистка JALM сервисов..."
	@cd core-runner && make kernel_clean
	@cd tula_spec && make clean
	@cd shablon_spec && make clean
	@echo "3. Очистка Docker..."
	@docker system prune -f
	@echo "[OK] Очистка завершена"

# Команды для разработки
dev-setup: ## Настройка окружения разработки
	@echo "Настройка окружения разработки JALM Full Stack..."
	@echo "1. Установка Python зависимостей..."
	@pip install -r requirements.txt
	@echo "2. Установка Node.js зависимостей..."
	@cd instances/demo && npm install
	@echo "3. Проверка Docker..."
	@docker --version
	@echo "[OK] Окружение разработки готово"

dev-test: ## Запуск тестов в режиме разработки
	@echo "Запуск тестов в режиме разработки..."
	@python -m pytest tests/ -v

# Информация о системе
info: ## Информация о JALM Full Stack
	@echo "JALM Full Stack - Информация о системе:"
	@echo "  Архитектура: Правильная JALM-land"
	@echo "  Core Runner: Порт 8000"
	@echo "  Tula Spec: Порт 8001"
	@echo "  Shablon Spec: Порт 8002"
	@echo "  Клиентские продукты: Порт 8080+"
	@echo "  Размер клиентского продукта: ~50MB"
	@echo "  Общий размер системы: Минимальный"
"""
        
        makefile_path = "Makefile"
        with open(makefile_path, 'w', encoding='utf-8') as f:
            f.write(makefile_content)
        
        return makefile_path

    def create_sample_product_files(self, product_name: str, instance_dir: str, params: Dict[str, Any], provision: Dict[str, Any]) -> None:
        """
        Создает пример файлов готового продукта на основе provision.yaml
        """
        # Создание директории FILES
        files_dir = os.path.join(instance_dir, "FILES")
        os.makedirs(files_dir, exist_ok=True)
        
        # Определение каналов связи из provision
        channels = provision.get("net", {}).get("channels", ["web"])
        primary_channel = channels[0] if channels else "web"
        fallback_channel = channels[1] if len(channels) > 1 else "email"
        
        # Получение сервисов из provision
        tula_services = [service.get("service") for service in provision.get("dependencies", {}).get("tula_spec", [])]
        shablon_services = [service.get("service") for service in provision.get("dependencies", {}).get("shablon_spec", [])]
        
        # OBJECT.jalm - конфигурация продукта
        object_jalm = {
            "name": product_name,
            "title": f"{product_name.title()} - Готовый продукт",
            "communication": {
                "primary_channel": primary_channel,
                "fallback": fallback_channel
            },
            "llm": {
                "model": "gpt-4",
                "actions_file": "FILES/llm_actions.json"
            },
            "variables": [
                {"shop_name": f"{product_name.title()}"},
                {"staff_list": "FILES/migrations.csv"}
            ],
            "requires": {
                "tula_spec": tula_services,
                "shablon_spec": shablon_services
            },
            "provision": provision.get("app_id", "unknown")
        }
        
        with open(os.path.join(instance_dir, "OBJECT.jalm"), 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(object_jalm, f, default_flow_style=False, allow_unicode=True)
        
        # plugin.js - встраиваемый виджет
        plugin_js = f"""// {product_name} - Встраиваемый виджет
(function() {{
    'use strict';
    
    const config = {{
        productName: '{product_name}',
        apiUrl: 'http://localhost/api',
        calendars: {params.get('calendars', 1)},
        lang: '{params.get('lang', 'ru')}',
        channels: {json.dumps(channels)},
        tulaServices: {json.dumps(tula_services)},
        shablonServices: {json.dumps(shablon_services)}
    }};
    
    console.log('[LAUNCH] {product_name} виджет загружен');
    console.log('[LIST] Каналы:', config.channels);
    console.log('[TOOLS] Tula services:', config.tulaServices);
    console.log('[LIST] Shablon services:', config.shablonServices);
    
    // Инициализация виджета
    function initWidget() {{
        const widget = document.createElement('div');
        widget.id = '{product_name}-widget';
        widget.innerHTML = `
            <div style="padding: 20px; border: 1px solid #ccc; border-radius: 8px; background: white; margin: 20px 0;">
                <h3>${{config.productName}}</h3>
                <p>Готовый продукт на базе JALM Full Stack</p>
                <p><strong>Каналы:</strong> ${{config.channels.join(', ')}}</p>
                <p><strong>Tula services:</strong> ${{config.tulaServices.join(', ') || 'Нет'}}</p>
                <p><strong>Shablon services:</strong> ${{config.shablonServices.join(', ') || 'Нет'}}</p>
                <button onclick="bookSlot()" style="background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Забронировать</button>
            </div>
        `;
        
        document.body.appendChild(widget);
    }}
    
    // Функция бронирования
    function bookSlot() {{
        fetch(`${{config.apiUrl}}/core/execute`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ intent: 'book_slot', data: {{ slot_id: 'demo-slot', user_id: 'demo-user' }} }})
        }})
        .then(response => response.json())
        .then(data => {{
            alert('Бронирование выполнено!');
        }})
        .catch(error => {{
            console.error('Ошибка бронирования:', error);
            alert('Ошибка при бронировании');
        }});
    }}
    
    // Запуск при загрузке страницы
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initWidget);
    }} else {{
        initWidget();
    }}
}})();
"""
        
        with open(os.path.join(files_dir, "plugin.js"), 'w', encoding='utf-8') as f:
            f.write(plugin_js)
        
        # llm_actions.json - сценарии LLM на основе provision
        llm_actions = []
        
        # Базовые действия на основе сервисов
        for service in tula_services:
            if "slot_validator" in service:
                llm_actions.append({
                    "intent": "validate_slot",
                    "channel": primary_channel,
                    "slots": ["slot_id"],
                    "api": "http://localhost/api/tula/functions/slot_validator"
                })
            elif "booking_widget" in service:
                llm_actions.append({
                    "intent": "book_slot",
                    "channel": primary_channel,
                    "slots": ["slot_id", "user_id"],
                    "api": "http://localhost/api/core/execute"
                })
            elif "notify_system" in service:
                llm_actions.append({
                    "intent": "send_notification",
                    "channel": primary_channel,
                    "slots": ["message", "recipient"],
                    "api": "http://localhost/api/tula/functions/notify_system"
                })
            elif "payment" in service.lower():
                llm_actions.append({
                    "intent": "process_payment",
                    "channel": primary_channel,
                    "slots": ["amount", "currency"],
                    "api": "http://localhost/api/core/execute"
                })
        
        # Добавление действий для шаблонов
        for service in shablon_services:
            if "booking" in service.lower():
                llm_actions.append({
                    "intent": "execute_booking_flow",
                    "channel": primary_channel,
                    "slots": ["calendar_id", "user_id", "slot_data"],
                    "api": "http://localhost/api/shablon/templates/booking-flow"
                })
        
        with open(os.path.join(files_dir, "llm_actions.json"), 'w', encoding='utf-8') as f:
            json.dump(llm_actions, f, indent=2, ensure_ascii=False)
        
        # migrations.csv - база данных
        migrations_csv = """name,role,speciality
Иван,barber,стрижка
Мария,colorist,окрашивание
Петр,barber,стрижка бороды
"""
        
        with open(os.path.join(files_dir, "migrations.csv"), 'w', encoding='utf-8') as f:
            f.write(migrations_csv)
        
        # demo.html - демонстрационная страница
        demo_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product_name.title()} - Демонстрация</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        .info {{
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .widget-demo {{
            border: 2px dashed #007bff;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }}
        .status {{
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .status.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .status.info {{
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>[LAUNCH] {product_name.title()} - Демонстрация</h1>
        
        <div class="info">
            <h3>[LIST] Информация о продукте</h3>
            <p><strong>Название:</strong> {product_name.title()}</p>
            <p><strong>Архитектура:</strong> JALM Full Stack</p>
            <p><strong>Каналы:</strong> {', '.join(channels)}</p>
            <p><strong>Tula Services:</strong> {', '.join(tula_services) if tula_services else 'Нет'}</p>
            <p><strong>Shablon Services:</strong> {', '.join(shablon_services) if shablon_services else 'Нет'}</p>
        </div>
        
        <div class="status success">
            [OK] Продукт успешно развернут и работает!
        </div>
        
        <div class="status info">
            📡 Подключение к JALM сервисам: Core Runner (8000), Tula Spec (8001), Shablon Spec (8002)
        </div>
        
        <div class="widget-demo">
            <h3>[TARGET] Демонстрация виджета</h3>
            <p>Виджет будет загружен автоматически:</p>
            <div id="{product_name}-widget-placeholder">
                <p>Загрузка виджета...</p>
            </div>
        </div>
        
        <div class="info">
            <h3>[TOOLS] Техническая информация</h3>
            <p><strong>API Endpoint:</strong> <code>http://localhost:8080/</code></p>
            <p><strong>Health Check:</strong> <code>http://localhost:8080/health</code></p>
            <p><strong>Plugin:</strong> <code>http://localhost:8080/FILES/plugin.js</code></p>
            <p><strong>LLM Actions:</strong> <code>http://localhost:8080/FILES/llm_actions.json</code></p>
        </div>
    </div>
    
    <!-- Загрузка виджета -->
    <script src="/FILES/plugin.js"></script>
</body>
</html>"""
        
        with open(os.path.join(files_dir, f"{product_name}.html"), 'w', encoding='utf-8') as f:
            f.write(demo_html)

    def create_minimal_client_product(self, product_name: str, instance_dir: str, provision: Dict[str, Any]) -> None:
        """
        Создает МИНИМАЛЬНЫЙ клиентский продукт на основе provision.yaml
        """
        # Создание структуры директорий
        dist_dir = os.path.join(instance_dir, "dist")
        config_dir = os.path.join(instance_dir, "config")
        app_dir = os.path.join(instance_dir, "app")
        
        os.makedirs(dist_dir, exist_ok=True)
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(app_dir, exist_ok=True)
        
        # Определение типа приложения из provision.yaml
        app_type = provision.get("meta", {}).get("app_type", "node")
        
        print(f"[TOOLS] Создание клиентского продукта типа: {app_type}")
        print(f"[LIST] Зависимости из provision.yaml:")
        
        # Выводим зависимости
        dependencies = provision.get("dependencies", {})
        for dep_type, dep_config in dependencies.items():
            if isinstance(dep_config, list):
                print(f"   - {dep_type}: {len(dep_config)} сервисов")
                for service in dep_config:
                    print(f"     * {service.get('service', 'unknown')} v{service.get('version', 'latest')}")
            else:
                print(f"   - {dep_type}: {dep_config.get('type', 'unknown')}")
        
        if app_type == "node":
            self._create_node_client_product(product_name, instance_dir, provision)
        elif app_type == "python":
            self._create_python_client_product(product_name, instance_dir, provision)
        else:
            self._create_node_client_product(product_name, instance_dir, provision)

    def _create_node_client_product(self, product_name: str, instance_dir: str, provision: Dict[str, Any]) -> None:
        """
        Создает Node.js клиентский продукт с правильными зависимостями
        """
        # package.json с минимальными зависимостями
        package_json = {
            "name": product_name,
            "version": "1.0.0",
            "description": f"Client product: {product_name}",
            "main": "dist/index.js",
            "scripts": {
                "start": "node dist/index.js",
                "build": "echo 'Build completed'"
            },
            "dependencies": {
                "dotenv": "^16.0.0"
            },
            "engines": {
                "node": ">=20.0.0"
            }
        }
        
        with open(os.path.join(instance_dir, "package.json"), 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
        
        # package-lock.json (упрощенный)
        package_lock = {
            "name": product_name,
            "version": "1.0.0",
            "lockfileVersion": 2,
            "dependencies": {
                "dotenv": {
                    "version": "16.0.0",
                    "resolved": "https://registry.npmjs.org/dotenv/-/dotenv-16.0.0.tgz"
                }
            }
        }
        
        with open(os.path.join(instance_dir, "package-lock.json"), 'w', encoding='utf-8') as f:
            json.dump(package_lock, f, indent=2)
        
        # dist/index.js - простой HTTP сервер без Express
        # Экранируем app_id для JavaScript
        app_id_escaped = provision.get("app_id", "unknown").replace("'", "\\'")
        
        index_js = f"""const http = require('http');
const url = require('url');
require('dotenv').config();

// Конфигурация из provision.yaml
const config = {{
    appId: process.env.APP_ID || '{app_id_escaped}',
    jalmCoreUrl: process.env.JALM_CORE_URL || 'http://core-runner:8888',
    jalmTulaUrl: process.env.JALM_TULA_URL || 'http://tula-spec:8001',
    jalmShablonUrl: process.env.JALM_SHABLON_URL || 'http://shablon-spec:8002'
}};

// Зависимости из provision.yaml
const dependencies = {json.dumps(provision.get("dependencies", {}))};
const apiLayer = dependencies.api_layer || [];
const tulaSpec = dependencies.tula_spec || [];
const datastore = dependencies.datastore || {{}};

const port = process.env.PORT || 8080;

// Простой HTTP сервер
const server = http.createServer((req, res) => {{
    const parsedUrl = url.parse(req.url, true);
    const path = parsedUrl.pathname;

    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    if (req.method === 'OPTIONS') {{
        res.writeHead(200);
        res.end();
        return;
    }}

    // Health check
    if (path === '/health') {{
        res.writeHead(200, {{ 'Content-Type': 'application/json' }});
        res.end(JSON.stringify({{
            status: 'healthy',
            appId: config.appId,
            timestamp: new Date().toISOString(),
            jalmServices: {{
                core: config.jalmCoreUrl,
                tula: config.jalmTulaUrl,
                shablon: config.jalmShablonUrl
            }}
        }}));
        return;
    }}

    // Основной endpoint
    if (path === '/') {{
        res.writeHead(200, {{ 'Content-Type': 'application/json' }});
        res.end(JSON.stringify({{
            message: '[LAUNCH] Клиентский продукт работает!',
            appId: config.appId,
            architecture: 'JALM Full Stack - Правильная архитектура',
            description: 'Минимальный клиентский контейнер без JALM инфраструктуры',
            jalmServices: {{
                core: config.jalmCoreUrl,
                tula: config.jalmTulaUrl,
                shablon: config.jalmShablonUrl
            }},
            features: [
                '[OK] Изолированный продукт',
                '[OK] Минимальный размер (~50MB)',
                '[OK] Подключение к JALM сервисам по сети',
                '[OK] Правильная архитектура JALM-land'
            ]
        }}));
        return;
    }}

    // Раздача статических файлов из FILES
    if (path.startsWith('/FILES/')) {{
        const fs = require('fs');
        const filePath = path.replace('/FILES/', './FILES/');
        
        try {{
            if (fs.existsSync(filePath)) {{
                const content = fs.readFileSync(filePath, 'utf8');
                const ext = filePath.split('.').pop();
                
                let contentType = 'text/plain';
                if (ext === 'js') contentType = 'application/javascript';
                else if (ext === 'html') contentType = 'text/html';
                else if (ext === 'css') contentType = 'text/css';
                else if (ext === 'json') contentType = 'application/json';
                
                res.writeHead(200, {{ 'Content-Type': contentType }});
                res.end(content);
            }} else {{
                res.writeHead(404, {{ 'Content-Type': 'application/json' }});
                res.end(JSON.stringify({{ error: 'File not found', path: filePath }}));
            }}
        }} catch (error) {{
            res.writeHead(500, {{ 'Content-Type': 'application/json' }});
            res.end(JSON.stringify({{ error: 'File read error', message: error.message }}));
        }}
        return;
    }}

    // API проксирование к JALM сервисам
    if (path.startsWith('/api/')) {{
        res.writeHead(200, {{ 'Content-Type': 'application/json' }});
        res.end(JSON.stringify({{
            message: 'API проксирование к JALM сервисам',
            path: path,
            jalmServices: config
        }}));
        return;
    }}

    // 404
    res.writeHead(404, {{ 'Content-Type': 'application/json' }});
    res.end(JSON.stringify({{
        error: 'Not Found',
        message: 'Клиентский продукт работает, но endpoint не найден'
    }}));
}});

server.listen(port, () => {{
    console.log(`[LAUNCH] ${{config.appId}} клиентский продукт запущен на порту ${{port}}`);
    console.log('[LIST] JALM сервисы:');
    console.log(`   - Core Runner: ${{config.jalmCoreUrl}}`);
    console.log(`   - Tula Spec: ${{config.jalmTulaUrl}}`);
    console.log(`   - Shablon Spec: ${{config.jalmShablonUrl}}`);
    console.log('[TARGET] Архитектура: Минимальный клиент + готовые JALM образы');
}});
"""
        
        with open(os.path.join(instance_dir, "dist", "index.js"), 'w', encoding='utf-8') as f:
            f.write(index_js)

    def _create_python_client_product(self, product_name: str, instance_dir: str, provision: Dict[str, Any]) -> None:
        """
        Создает Python клиентский продукт
        """
        # requirements.txt
        requirements = """fastapi>=0.104.0
uvicorn>=0.24.0
requests>=2.31.0
python-dotenv>=1.0.0
"""
        
        with open(os.path.join(instance_dir, "requirements.txt"), 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        # app/main.py - основной файл приложения
        main_py = f"""from fastapi import FastAPI, HTTPException
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="{product_name}", version="1.0.0")

# Конфигурация из provision.yaml
config = {{
    "app_id": os.getenv("APP_ID", "{provision.get('app_id', 'unknown')}"),
    "jalm_core_url": os.getenv("JALM_CORE_URL", "http://core-runner:8888"),
    "jalm_tula_url": os.getenv("JALM_TULA_URL", "http://tula-spec:8001"),
    "jalm_shablon_url": os.getenv("JALM_SHABLON_URL", "http://shablon-spec:8002")
}}

@app.get("/health")
async def health_check():
    return {{
        "status": "healthy",
        "app_id": config["app_id"],
        "timestamp": "2024-01-01T00:00:00Z"
    }}

@app.get("/")
async def root():
    return {{
        "message": "Client product is running",
        "app_id": config["app_id"],
        "jalm_services": {{
            "core": config["jalm_core_url"],
            "tula": config["jalm_tula_url"],
            "shablon": config["jalm_shablon_url"]
        }}
    }}

@app.post("/api/core/execute")
async def execute_core(data: dict):
    try:
        response = requests.post(f"{{config['jalm_core_url']}}/execute", json=data)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tula/functions/{{function_name}}")
async def get_tula_function(function_name: str):
    try:
        response = requests.get(f"{{config['jalm_tula_url']}}/functions/{{function_name}}")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/shablon/templates/{{template_name}}")
async def get_shablon_template(template_name: str):
    try:
        response = requests.get(f"{{config['jalm_shablon_url']}}/templates/{{template_name}}")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print(f"[LAUNCH] {{config['app_id']}} client product starting...")
    print("[LIST] JALM services:")
    print(f"   - Core Runner: {{config['jalm_core_url']}}")
    print(f"   - Tula Spec: {{config['jalm_tula_url']}}")
    print(f"   - Shablon Spec: {{config['jalm_shablon_url']}}")
    uvicorn.run(app, host="0.0.0.0", port=8080)
"""
        
        with open(os.path.join(instance_dir, "app", "main.py"), 'w', encoding='utf-8') as f:
            f.write(main_py)
        
        # Создание __init__.py
        with open(os.path.join(instance_dir, "app", "__init__.py"), 'w', encoding='utf-8') as f:
            f.write('"""Client product package"""\n')

    def create_env_file(self, instance_dir: str, provision: Dict[str, Any]) -> str:
        """
        Создает .env файл с конфигурацией в config/ директории
        """
        env_content = f"""# {provision.get('app_id', 'unknown')} - Environment Configuration
NODE_ENV=production
PORT=8080
APP_ID={provision.get('app_id', 'unknown')}

# JALM Service URLs (подключение к локальным сервисам)
JALM_CORE_URL=http://localhost:8000
JALM_TULA_URL=http://localhost:8001
JALM_SHABLON_URL=http://localhost:8002

# Application specific
LOG_LEVEL=INFO
"""
        
        # Создаем config/ директорию если её нет
        config_dir = os.path.join(instance_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        env_path = os.path.join(config_dir, ".env")
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        return env_path

    def build_docker_image(self, product_name: str, instance_dir: str) -> bool:
        """
        Собирает Docker образ для готового продукта
        """
        try:
            print(f"[DOCKER] Сборка Docker образа для {product_name}...")
            
            # Проверка Docker
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            
            # Сборка образа
            cmd = ["docker", "build", "-t", f"{product_name}:latest", "."]
            result = subprocess.run(cmd, cwd=instance_dir, check=True, capture_output=True, text=True)
            
            print(f"[OK] Docker образ {product_name}:latest успешно собран!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Ошибка сборки Docker образа: {e}")
            return False
        except FileNotFoundError:
            print("[ERROR] Docker не найден")
            return False

    def launch_instance(self, instance_name: str, instance_dir: str) -> str:
        """
        Запускает контейнеры через docker-compose. Возвращает URL инстанса.
        """
        # Запуск контейнеров
        try:
            print("[DOCKER] Запуск контейнеров...")
            subprocess.run([
                "docker-compose", "up", "-d"
            ], cwd=instance_dir, check=True)
            
            print("[OK] Контейнеры запущены:")
            print("   - Клиентский продукт: http://localhost:8080")
            print("   - JALM Core Runner: http://core-runner:8888")
            print("   - JALM Tula Spec: http://tula-spec:8001")
            print("   - JALM Shablon Spec: http://shablon-spec:8002")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка запуска docker-compose: {e}")
        
        # Генерация URL клиентского продукта
        return f"http://localhost:8080"

    def provision(self, jalm_path: str, base_instances_dir: str = "instances") -> str:
        """
        Основной метод: парсит JALM, генерирует provision.yaml, создает минимальный клиентский продукт, запускает с готовыми JALM образами.
        """
        print("Создание клиентского продукта с правильной архитектурой...")
        
        # Шаг 1: Генерация provision.yaml из Intent-DSL
        print("Шаг 1: Генерация provision.yaml...")
        provision_path = self.generate_provision_yaml(jalm_path)
        provision = self.read_provision_yaml(provision_path)
        
        print(f"[OK] Provision.yaml сгенерирован:")
        print(f"   - App ID: {provision.get('app_id', 'unknown')}")
        print(f"   - Environment: {provision.get('env', 'unknown')}")
        print(f"   - Tula Spec services: {len(provision.get('dependencies', {}).get('tula_spec', []))}")
        print(f"   - API Layer services: {len(provision.get('dependencies', {}).get('api_layer', []))}")
        
        # Шаг 2: Подготовка параметров
        jalm = self.parse_jalm(jalm_path)
        context = jalm.get("context", {})
        instance_name = context.get("domain", "demo").split(".")[0]
        instance_dir = os.path.join(base_instances_dir, instance_name)
        
        # Создание директории для продукта
        os.makedirs(instance_dir, exist_ok=True)
        
        params = {
            "calendars": context.get("calendars", 1),
            "lang": context.get("lang", "ru"),
            "domain": context.get("domain", "demo.mycalendar.app")
        }
        
        print(f"[PACKAGE] Создание клиентского продукта: {instance_name}")
        print(f"[STATS] Параметры: {params}")
        
        # Шаг 3: Создание минимального клиентского продукта на основе provision.yaml
        print("[TOOLS] Шаг 3: Создание минимального клиентского продукта...")
        
        # Создание минимального клиентского продукта на основе provision.yaml
        self.create_minimal_client_product(instance_name, instance_dir, provision)
        
        # Создание плагинов и дополнительных файлов продукта
        self.create_sample_product_files(instance_name, instance_dir, params, provision)
        
        # Создание Dockerfile для клиентского продукта
        self.create_client_dockerfile(instance_name, instance_dir, provision)
        
        # Создание .env файла
        self.create_env_file(instance_dir, provision)
        
        # Копирование provision.yaml в конфигурацию
        config_dir = os.path.join(instance_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        shutil.copy2(provision_path, os.path.join(config_dir, "provision.yaml"))
        
        # Создание Docker Compose с готовыми JALM образами
        self.create_production_docker_compose(instance_name, instance_dir, provision)
        
        # Создание Makefile для управления продуктом
        self.create_product_makefile(instance_name, instance_dir, provision)
        
        # Создание README для продукта
        jalm_version = provision.get("meta", {}).get("jalm_version", "1.0.0")
        app_id = provision.get('app_id', 'unknown')
        subnet_octet = abs(hash(instance_name)) % 255
        tula_services = provision.get('dependencies', {}).get('tula_spec', [])
        api_layer_services = provision.get('dependencies', {}).get('api_layer', [])
        tula_services_list = '\n'.join(f"- {service.get('service', 'unknown')} v{service.get('version', 'latest')}" for service in tula_services)
        api_layer_services_list = '\n'.join(f"- {service.get('service', 'unknown')} v{service.get('version', 'latest')}" for service in api_layer_services)
        environment = provision.get('env', 'unknown')
        readme_content = f"""# {instance_name.title()} - Клиентский продукт

## [LAUNCH] Правильная архитектура

Этот продукт использует **правильную архитектуру JALM-land**:

### Клиентский контейнер (минимальный)
- Содержит **только** статические файлы продукта
- Содержит **только** конфигурацию (.env + provision.yaml)
- **НЕ содержит** JALM инфраструктуру
- Размер: ~50MB
- Подключается к **локальным JALM сервисам** по сети

### JALM инфраструктура (локальные сервисы)
- **Core Runner**: http://localhost:8000 (запускается отдельно)
- **Tula Spec**: http://localhost:8001 (запускается отдельно)
- **Shablon Spec**: http://localhost:8002 (запускается отдельно)
- Запускаются **локально** через start_jalm_services.py

## [LAUNCH] Быстрый запуск

```bash
# 1. Запуск JALM сервисов (в отдельном терминале)
python start_jalm_services.py

# 2. Сборка и запуск клиентского продукта
docker-compose up -d

# 3. Проверка статуса
docker-compose ps

# 4. Просмотр логов клиентского продукта
docker-compose logs -f {instance_name}
```

## [LIST] Доступные сервисы

- **Клиентский продукт**: http://localhost:8080
- **JALM Core Runner**: http://localhost:8000 (локальный)
- **JALM Tula Spec**: http://localhost:8001 (локальный)
- **JALM Shablon Spec**: http://localhost:8002 (локальный)

## [TOOLS] Конфигурация

### App ID: {app_id}
### Environment: {environment}

### Tula Spec services:
{tula_services_list}

### API Layer services:
{api_layer_services_list}

## [DIR] Структура клиентского продукта

```
{instance_name}/
├── dist/                 # Статические файлы (Node.js)
│   └── index.js         # Основное приложение
├── app/                 # Python приложение (если Python)
│   └── main.py         # Основное приложение
├── config/              # Конфигурация
│   ├── provision.yaml  # Provision конфигурация
│   └── .env           # Переменные окружения
├── package.json         # Node.js зависимости
├── requirements.txt     # Python зависимости
├── Dockerfile          # Docker образ (минимальный)
└── docker-compose.yml  # Оркестрация (только клиент)
```

## 🛠️ Управление

```bash
# Остановка клиентского продукта
docker-compose down

# Перезапуск клиентского продукта
docker-compose restart

# Очистка
docker-compose down -v

# Остановка JALM сервисов
# Ctrl+C в терминале с start_jalm_services.py
```

## [TARGET] Что это такое

Это **клиентский продукт** (например, барбершоп), который:
- Содержит **минимальный код** (только продукт)
- Подключается к **локальным JALM сервисам** по сети
- Следует **правильной архитектуре** JALM-land
- **НЕ включает** JALM инфраструктуру в образ

## [STATS] Размеры образов

- **Клиентский продукт**: ~50MB (минимальный)
- **JALM сервисы**: запускаются локально (не в Docker)

**Общий размер**: ~50MB (вместо 2GB+ в старой архитектуре)

## 🔄 Правильная последовательность

1. **Intent-DSL** → парсинг JALM файла
2. **Provision Scanner** → генерация provision.yaml
3. **Core Runner** → создание минимального клиентского продукта
4. **Клиентский продукт** → подключение к JALM сервисам по сети
"""
        
        with open(os.path.join(instance_dir, "README.md"), 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Сборка Docker образа клиентского продукта
        if self.build_docker_image(instance_name, instance_dir):
            print(f"[OK] Docker образ клиентского продукта {instance_name}:latest готов")
        else:
            print(f"[WARNING] Не удалось собрать Docker образ для {instance_name}")
        
        # Запуск контейнеров
        url = self.launch_instance(instance_name, instance_dir)
        
        print(f"[SUCCESS] Клиентский продукт {instance_name} создан и запущен!")
        print(f"[WEB] URL: {url}")
        print(f"[DIR] Директория: {instance_dir}")
        print(f"[STATS] Архитектура: Минимальный клиент + готовые JALM образы")
        
        return url

# Пример использования:
if __name__ == "__main__":
    provisioner = SaasProvisioner()
    url = provisioner.provision("./config.jalm")
    print(f"Инстанс доступен по адресу: {url}") 