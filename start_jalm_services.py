#!/usr/bin/env python3
"""
Скрипт для запуска всех сервисов JALM Full Stack
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_service(service_name: str, port: int, command: str):
    """Запуск сервиса"""
    print(f"🚀 Запуск {service_name} на порту {port}...")
    
    try:
        # Запуск в фоновом режиме
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем немного для запуска
        time.sleep(3)
        
        # Проверяем, что процесс запущен
        if process.poll() is None:
            print(f"✅ {service_name} запущен (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Ошибка запуска {service_name}:")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запуска {service_name}: {e}")
        return None

def check_service_health(service_name: str, port: int):
    """Проверка здоровья сервиса"""
    import requests
    
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} здоров")
            return True
        else:
            print(f"⚠️ {service_name} отвечает, но статус {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"❌ {service_name} недоступен")
        return False

def main():
    """Основная функция"""
    print("🎯 Запуск JALM Full Stack сервисов")
    print("=" * 50)
    
    # Определяем команды запуска
    services = [
        {
            "name": "Core Runner",
            "port": 8000,
            "command": "cd core-runner && python api/main.py"
        },
        {
            "name": "Tula Spec", 
            "port": 8001,
            "command": "cd tula_spec && python api/main.py"
        },
        {
            "name": "Shablon Spec",
            "port": 8002, 
            "command": "cd shablon_spec && python api/main.py"
        }
    ]
    
    processes = []
    
    # Запускаем все сервисы
    for service in services:
        process = start_service(service["name"], service["port"], service["command"])
        if process:
            processes.append((service["name"], process))
        else:
            print(f"❌ Не удалось запустить {service['name']}")
            return False
    
    print(f"\n⏳ Ожидание запуска сервисов...")
    time.sleep(5)
    
    # Проверяем здоровье всех сервисов
    print(f"\n🏥 Проверка здоровья сервисов:")
    all_healthy = True
    
    for service in services:
        if not check_service_health(service["name"], service["port"]):
            all_healthy = False
    
    if all_healthy:
        print(f"\n🎉 Все сервисы JALM Full Stack запущены и работают!")
        print(f"📊 Статус сервисов:")
        print(f"   Core Runner: http://localhost:8000")
        print(f"   Tula Spec:   http://localhost:8001")
        print(f"   Shablon Spec: http://localhost:8002")
        print(f"\n🧪 Для тестирования запустите: python test_jalm_full_stack.py")
        print(f"⏹️  Для остановки нажмите Ctrl+C")
        
        try:
            # Держим сервисы запущенными
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Остановка сервисов...")
            
            # Останавливаем все процессы
            for service_name, process in processes:
                print(f"   Остановка {service_name}...")
                process.terminate()
                process.wait()
                print(f"   ✅ {service_name} остановлен")
            
            print(f"🎯 Все сервисы остановлены")
    else:
        print(f"\n❌ Не все сервисы здоровы. Проверьте логи выше.")
        return False

if __name__ == "__main__":
    main() 