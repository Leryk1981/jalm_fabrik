"""
Notify System - Система уведомлений
JALM Tula Function

Использование в JALM:
IMPORT notify_system v1.0.0
RUN notification_id := notify_system.send(message, channel, recipient, type)
"""

import uuid
import json
from typing import Dict, Any, Optional
from datetime import datetime


def send(message: str, channel: str, recipient: str, 
         notification_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Отправляет уведомление
    
    Args:
        message: Текст сообщения
        channel: Канал доставки ("web", "email", "sms")
        recipient: Получатель
        notification_type: Тип уведомления ("confirmed", "choose_other", "reminder")
    
    Returns:
        Словарь с результатом:
            - notification_id: UUID уведомления
            - status: "sent", "failed" или "pending"
    """
    try:
        # Валидация входных данных
        if not _validate_input(message, channel, recipient):
            return {
                "notification_id": str(uuid.uuid4()),
                "status": "failed",
                "error": "Неверные входные данные"
            }
        
        # Создание уведомления
        notification_id = str(uuid.uuid4())
        
        # Имитация отправки
        status = _send_notification(message, channel, recipient, notification_type)
        
        return {
            "notification_id": notification_id,
            "status": status
        }
        
    except Exception as e:
        return {
            "notification_id": str(uuid.uuid4()),
            "status": "failed",
            "error": f"Ошибка отправки: {str(e)}"
        }


def _validate_input(message: str, channel: str, recipient: str) -> bool:
    """Валидация входных данных"""
    # Проверка сообщения
    if not message or len(message.strip()) == 0:
        return False
    
    # Проверка канала
    valid_channels = ["web", "email", "sms"]
    if channel not in valid_channels:
        return False
    
    # Проверка получателя
    if not recipient or len(recipient.strip()) == 0:
        return False
    
    return True


def _send_notification(message: str, channel: str, recipient: str, 
                      notification_type: Optional[str]) -> str:
    """Имитация отправки уведомления"""
    # В реальной реализации здесь была бы интеграция с сервисами
    # Пока возвращаем "sent" для имитации успешной отправки
    
    # Логирование для отладки
    print(f"[NOTIFY] {channel.upper()}: {recipient} - {message}")
    
    return "sent"


def get_info() -> Dict[str, Any]:
    """Возвращает информацию о функции"""
    return {
        "name": "notify_system",
        "version": "1.0.0",
        "description": "Система уведомлений",
        "functions": ["send"]
    } 