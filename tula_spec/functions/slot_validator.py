"""
Slot Validator - Валидатор слотов бронирования
JALM Tula Function

Использование в JALM:
IMPORT slot_validator tula:hash~ab12fe
RUN slot_uuid := slot_validator.create(slot)
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def create(slot_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создает и валидирует слот бронирования
    
    Args:
        slot_data: Словарь с данными слота или обертка {"slot": {...}}
            - datetime: строка в формате ISO
            - duration: длительность в минутах (15-480)
            - service_id: UUID услуги
    
    Returns:
        Словарь с результатом:
            - slot_uuid: UUID созданного слота
            - status: "valid", "invalid" или "conflict"
            - message: описание результата
    """
    try:
        # Извлекаем данные слота из обертки если нужно
        if "slot" in slot_data:
            slot = slot_data["slot"]
        else:
            slot = slot_data
        
        # Валидация входных данных
        if not _validate_input(slot):
            return {
                "slot_uuid": str(uuid.uuid4()),
                "status": "invalid",
                "message": "Неверные входные данные"
            }
        
        # Проверка конфликтов (имитация)
        if _check_conflicts(slot):
            return {
                "slot_uuid": str(uuid.uuid4()),
                "status": "conflict",
                "message": "Слот уже занят"
            }
        
        # Создание слота
        slot_uuid = str(uuid.uuid4())
        
        return {
            "slot_uuid": slot_uuid,
            "status": "valid",
            "message": "Слот успешно создан"
        }
        
    except Exception as e:
        return {
            "slot_uuid": str(uuid.uuid4()),
            "status": "invalid",
            "message": f"Ошибка валидации: {str(e)}"
        }


def _validate_input(slot: Dict[str, Any]) -> bool:
    """Валидация входных данных"""
    try:
        # Проверка обязательных полей
        required_fields = ["datetime", "duration", "service_id"]
        for field in required_fields:
            if field not in slot:
                return False
        
        # Валидация datetime
        datetime.fromisoformat(slot["datetime"].replace("Z", "+00:00"))
        
        # Валидация duration
        duration = int(slot["duration"])
        if not (15 <= duration <= 480):
            return False
        
        # Валидация service_id (простая проверка UUID)
        uuid.UUID(slot["service_id"])
        
        return True
        
    except (ValueError, TypeError):
        return False


def _check_conflicts(slot: Dict[str, Any]) -> bool:
    """Проверка конфликтов с существующими слотами (имитация)"""
    # В реальной реализации здесь была бы проверка БД
    # Пока возвращаем False (нет конфликтов)
    return False


# Функции для тестирования
def get_info() -> Dict[str, Any]:
    """Возвращает информацию о функции"""
    return {
        "name": "slot_validator",
        "version": "1.3.2",
        "description": "Валидатор слотов бронирования",
        "functions": ["create"]
    }


def validate_schema(data: Dict[str, Any]) -> bool:
    """Валидация схемы данных"""
    return _validate_input(data) 