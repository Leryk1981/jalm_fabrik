#!/usr/bin/env python3
"""
Автоматический скрипт установки Barbershop Plugin
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def print_banner():
    """Вывод баннера установки"""
    print("""
🪒 Barbershop Plugin - Автоматическая установка
==================================================
    """)

def check_requirements():
    """Проверка системных требований"""
    print("🔍 Проверка системных требований...")
    
    requirements = {
        'python': 'python --version',
        'pip': 'pip --version',
        'docker': 'docker --version',
        'docker-compose': 'docker-compose --version',
        'git': 'git --version'
    }
    
    missing = []
    
    for tool, command in requirements.items():
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {tool}: {result.stdout.strip()}")
            else:
                missing.append(tool)
        except FileNotFoundError:
            missing.append(tool)
    
    if missing:
        print(f"❌ Отсутствуют: {', '.join(missing)}")
        print("📋 Установите недостающие компоненты и повторите установку")
        return False
    
    return True

def create_env_file():
    """Создание файла .env из шаблона"""
    print("📝 Создание конфигурационного файла...")
    
    env_template = """# Barbershop Plugin Configuration

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook/telegram

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# AWS Lambda
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
LAMBDA_FUNCTION_NAME=barbershop-booking

# API Configuration
API_BASE_URL=https://your-api-gateway-url.amazonaws.com
CORS_ORIGINS=https://your-domain.com,http://localhost:3000

# Database
DATABASE_URL=firestore://your-project-id

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
"""
    
    env_path = Path('.env')
    if not env_path.exists():
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_template)
        print("✅ Файл .env создан")
    else:
        print("ℹ️  Файл .env уже существует")

def install_dependencies():
    """Установка Python зависимостей"""
    print("📦 Установка зависимостей...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def setup_directories():
    """Создание необходимых директорий"""
    print("📁 Создание директорий...")
    
    directories = [
        'logs',
        'data',
        'uploads',
        'temp',
        'backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Создана директория: {directory}")

def create_scripts():
    """Создание вспомогательных скриптов"""
    print("🔧 Создание вспомогательных скриптов...")
    
    scripts_dir = Path('scripts')
    scripts_dir.mkdir(exist_ok=True)
    
    # Скрипт проверки статуса
    status_script = """#!/usr/bin/env python3
import requests
import json

def check_service_health():
    services = {
        'Core Runner': 'http://localhost:8000/health',
        'Tula Spec': 'http://localhost:8001/health',
        'Shablon Spec': 'http://localhost:8002/health'
    }
    
    print("🏥 Проверка здоровья сервисов:")
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Здоров")
            else:
                print(f"❌ {name}: Ошибка {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Недоступен - {e}")

if __name__ == "__main__":
    check_service_health()
"""
    
    with open(scripts_dir / 'status.py', 'w', encoding='utf-8') as f:
        f.write(status_script)
    
    # Скрипт перезапуска
    restart_script = """#!/usr/bin/env python3
import subprocess
import time

def restart_services():
    print("🔄 Перезапуск сервисов...")
    
    # Остановка
    subprocess.run(['docker-compose', 'down'])
    time.sleep(2)
    
    # Запуск
    subprocess.run(['docker-compose', 'up', '-d'])
    time.sleep(5)
    
    print("✅ Сервисы перезапущены")

if __name__ == "__main__":
    restart_services()
"""
    
    with open(scripts_dir / 'restart.py', 'w', encoding='utf-8') as f:
        f.write(restart_script)
    
    print("✅ Вспомогательные скрипты созданы")

def create_docker_compose():
    """Создание docker-compose.yml"""
    print("🐳 Создание Docker Compose конфигурации...")
    
    docker_compose = """version: '3.8'

services:
  core-runner:
    image: jalm/core-runner:latest
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  tula-spec:
    image: jalm/tula-spec:latest
    ports:
      - "8001:8001"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  shablon-spec:
    image: jalm/shablon-spec:latest
    ports:
      - "8002:8002"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./templates:/app/templates
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - core-runner
      - tula-spec
      - shablon-spec
    restart: unless-stopped

volumes:
  data:
  logs:
"""
    
    with open('docker-compose.yml', 'w', encoding='utf-8') as f:
        f.write(docker_compose)
    
    print("✅ Docker Compose конфигурация создана")

def create_nginx_config():
    """Создание конфигурации Nginx"""
    print("🌐 Создание конфигурации Nginx...")
    
    nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream core_runner {
        server core-runner:8000;
    }
    
    upstream tula_spec {
        server tula-spec:8001;
    }
    
    upstream shablon_spec {
        server shablon-spec:8002;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://core_runner;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /tula/ {
            proxy_pass http://tula_spec/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /shablon/ {
            proxy_pass http://shablon_spec/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /static/ {
            alias /app/static/;
        }
    }
}
"""
    
    with open('nginx.conf', 'w', encoding='utf-8') as f:
        f.write(nginx_config)
    
    print("✅ Конфигурация Nginx создана")

def run_tests():
    """Запуск базовых тестов"""
    print("🧪 Запуск базовых тестов...")
    
    try:
        # Проверка структуры файлов
        required_files = [
            'manifest.json',
            'llm_actions.json',
            'plugin.js',
            'migrations.csv'
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
            return False
        
        print("✅ Базовая проверка пройдена")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def print_next_steps():
    """Вывод следующих шагов"""
    print("""
🎉 Установка завершена!
==================================================

📋 Следующие шаги:

1. 🔧 Настройте переменные окружения в файле .env
2. 🤖 Создайте Telegram бота через @BotFather
3. 🔥 Настройте Firebase проект
4. ☁️ Настройте AWS Lambda
5. 🚀 Запустите сервисы: docker-compose up -d
6. 🧪 Протестируйте: python scripts/status.py

📚 Документация: INSTALLATION_GUIDE.md
🔧 Вспомогательные скрипты: scripts/
📞 Поддержка: support@barbershop-plugin.com

Удачи! 🪒
    """)

def main():
    """Основная функция установки"""
    print_banner()
    
    # Проверка требований
    if not check_requirements():
        sys.exit(1)
    
    # Создание структуры
    setup_directories()
    create_env_file()
    create_scripts()
    create_docker_compose()
    create_nginx_config()
    
    # Установка зависимостей
    if not install_dependencies():
        print("⚠️  Продолжайте без установки зависимостей")
    
    # Тестирование
    if not run_tests():
        print("⚠️  Продолжайте с предупреждениями")
    
    # Завершение
    print_next_steps()

if __name__ == "__main__":
    main() 