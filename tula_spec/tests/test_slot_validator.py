"""
Тесты для slot_validator
"""

import sys
import os
from pathlib import Path

# Добавляем путь к функциям
sys.path.append(str(Path(__file__).parent.parent / "functions"))

import pytest
from slot_validator import create, _validate_input, _check_conflicts


class TestSlotValidator:
    """Тесты для slot_validator"""
    
    def test_create_valid_slot(self):
        """Тест создания валидного слота"""
        slot_data = {
            "datetime": "2024-06-15T10:00:00Z",
            "duration": 60,
            "service_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        result = create({"slot": slot_data})
        
        assert result["status"] == "valid"
        assert "slot_uuid" in result
        assert result["message"] == "Слот успешно создан"
    
    def test_create_invalid_slot_missing_fields(self):
        """Тест создания слота с отсутствующими полями"""
        slot_data = {
            "datetime": "2024-06-15T10:00:00Z"
            # Отсутствуют duration и service_id
        }
        
        result = create({"slot": slot_data})
        
        assert result["status"] == "invalid"
        assert "slot_uuid" in result
        assert "Неверные входные данные" in result["message"]
    
    def test_create_invalid_slot_duration(self):
        """Тест создания слота с неверной длительностью"""
        slot_data = {
            "datetime": "2024-06-15T10:00:00Z",
            "duration": 10,  # Меньше минимальной (15)
            "service_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        result = create({"slot": slot_data})
        
        assert result["status"] == "invalid"
    
    def test_create_invalid_slot_datetime(self):
        """Тест создания слота с неверной датой"""
        slot_data = {
            "datetime": "invalid-datetime",
            "duration": 60,
            "service_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        result = create({"slot": slot_data})
        
        assert result["status"] == "invalid"
    
    def test_validate_input_valid(self):
        """Тест валидации валидных входных данных"""
        slot_data = {
            "datetime": "2024-06-15T10:00:00Z",
            "duration": 60,
            "service_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        assert _validate_input(slot_data) == True
    
    def test_validate_input_invalid_uuid(self):
        """Тест валидации с неверным UUID"""
        slot_data = {
            "datetime": "2024-06-15T10:00:00Z",
            "duration": 60,
            "service_id": "invalid-uuid"
        }
        
        assert _validate_input(slot_data) == False
    
    def test_validate_input_invalid_duration(self):
        """Тест валидации с неверной длительностью"""
        slot_data = {
            "datetime": "2024-06-15T10:00:00Z",
            "duration": 500,  # Больше максимальной (480)
            "service_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        assert _validate_input(slot_data) == False
    
    def test_check_conflicts(self):
        """Тест проверки конфликтов"""
        slot_data = {
            "datetime": "2024-06-15T10:00:00Z",
            "duration": 60,
            "service_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        # Пока функция всегда возвращает False (нет конфликтов)
        assert _check_conflicts(slot_data) == False


if __name__ == "__main__":
    pytest.main([__file__]) 