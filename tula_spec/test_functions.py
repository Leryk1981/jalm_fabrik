#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функций Tula Spec
"""

import sys
import json
from pathlib import Path

# Добавляем путь к функциям
sys.path.append(str(Path(__file__).parent / "functions"))

def test_slot_validator():
    """Тест slot_validator"""
    print("=== Тест slot_validator ===")
    
    from slot_validator import create
    
    # Тест 1: Валидный слот
    valid_slot = {
        "slot": {
            "datetime": "2024-06-15T10:00:00Z",
            "duration": 60,
            "service_id": "123e4567-e89b-12d3-a456-426614174000"
        }
    }
    
    result = create(valid_slot)
    print(f"Валидный слот: {result}")
    
    # Тест 2: Неверная длительность
    invalid_slot = {
        "slot": {
            "datetime": "2024-06-15T10:00:00Z",
            "duration": 10,  # Меньше минимальной
            "service_id": "123e4567-e89b-12d3-a456-426614174000"
        }
    }
    
    result = create(invalid_slot)
    print(f"Неверная длительность: {result}")

def test_booking_widget():
    """Тест booking_widget"""
    print("\n=== Тест booking_widget ===")
    
    from booking_widget import create
    
    # Тест создания виджета
    result = create("123e4567-e89b-12d3-a456-426614174000", "user-123")
    print(f"Создание виджета: {result}")

def test_notify_system():
    """Тест notify_system"""
    print("\n=== Тест notify_system ===")
    
    from notify_system import send
    
    # Тест отправки уведомления
    result = send("Ваш слот подтвержден", "web", "user@example.com", "confirmed")
    print(f"Отправка уведомления: {result}")

def test_registry():
    """Тест загрузки реестра"""
    print("\n=== Тест реестра ===")
    
    registry_path = Path(__file__).parent / "registry" / "functions.json"
    
    if registry_path.exists():
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        print(f"Всего функций: {registry['metadata']['total_functions']}")
        for func in registry['functions']:
            print(f"- {func['id']} v{func['version']}: {func['description']}")
    else:
        print("Реестр не найден")

if __name__ == "__main__":
    print("Тестирование Tula Spec функций...\n")
    
    test_registry()
    test_slot_validator()
    test_booking_widget()
    test_notify_system()
    
    print("\nТестирование завершено!") 