#!/usr/bin/env python3
"""
Отладочный тест API функций Tula Spec
"""

import requests
import json

def test_function_api():
    """Тест API функций"""
    print("🔍 Отладочный тест API функций Tula Spec")
    print("=" * 50)
    
    # Тест 1: Получение списка функций
    print("1. Получение списка функций...")
    response = requests.get("http://localhost:8001/functions")
    print(f"   Статус: {response.status_code}")
    if response.status_code == 200:
        functions = response.json()
        print(f"   Функций: {len(functions)}")
        for func in functions:
            print(f"   - {func['id']}: {func['description']}")
    
    # Тест 2: Получение метаданных slot_validator
    print("\n2. Метаданные slot_validator...")
    response = requests.get("http://localhost:8001/functions/slot_validator")
    print(f"   Статус: {response.status_code}")
    if response.status_code == 200:
        metadata = response.json()
        print(f"   Входная схема: {metadata['input_schema']}")
    
    # Тест 3: Выполнение slot_validator
    print("\n3. Выполнение slot_validator...")
    test_data = {
        "params": {
            "slot": {
                "datetime": "2024-06-15T10:00:00Z",
                "duration": 60,
                "service_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    }
    
    print(f"   Отправляем: {json.dumps(test_data, indent=2)}")
    response = requests.post(
        "http://localhost:8001/functions/slot_validator/execute",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Статус: {response.status_code}")
    print(f"   Ответ: {response.text}")
    
    if response.status_code != 200:
        print(f"   Ошибка: {response.json() if response.text else 'Нет деталей'}")

if __name__ == "__main__":
    test_function_api() 