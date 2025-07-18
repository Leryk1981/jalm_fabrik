"""
Booking Widget - Виджет для бронирования слотов
JALM Tula Function

Использование в JALM:
IMPORT booking_widget v1.3.2
RUN widget_url := booking_widget.create(calendar_id, user_id)
"""

import uuid
import json
from typing import Dict, Any, Optional


def create(calendar_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Создает виджет для бронирования
    
    Args:
        calendar_id: UUID календаря
        user_id: UUID пользователя (опционально)
    
    Returns:
        Словарь с результатом:
            - widget_url: URL виджета
            - widget_id: UUID виджета
    """
    try:
        # Валидация calendar_id
        if not _validate_uuid(calendar_id):
            return {
                "widget_url": "",
                "widget_id": "",
                "error": "Неверный calendar_id"
            }
        
        # Создание виджета
        widget_id = str(uuid.uuid4())
        
        # Генерация URL виджета
        base_url = "https://widget.jalm.dev"
        widget_url = f"{base_url}/booking/{widget_id}?calendar={calendar_id}"
        
        if user_id:
            widget_url += f"&user={user_id}"
        
        return {
            "widget_url": widget_url,
            "widget_id": widget_id
        }
        
    except Exception as e:
        return {
            "widget_url": "",
            "widget_id": "",
            "error": f"Ошибка создания виджета: {str(e)}"
        }


def _validate_uuid(uuid_str: str) -> bool:
    """Валидация UUID"""
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False


def get_info() -> Dict[str, Any]:
    """Возвращает информацию о функции"""
    return {
        "name": "booking_widget",
        "version": "1.3.2",
        "description": "Виджет для бронирования слотов",
        "functions": ["create"]
    } 