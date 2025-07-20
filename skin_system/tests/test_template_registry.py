#!/usr/bin/env python3
"""
Unit тесты для TemplateRegistry
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Добавляем путь к модулю для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from template_registry import TemplateRegistry


class TestTemplateRegistry:
    """Тесты для TemplateRegistry"""
    
    @pytest.fixture
    def temp_dir(self):
        """Временная директория для тестов"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def registry(self, temp_dir):
        """Экземпляр TemplateRegistry для тестов"""
        return TemplateRegistry(registry_path=temp_dir)
    
    def test_init_creates_directory(self, temp_dir):
        """Тест создания директории при инициализации"""
        registry = TemplateRegistry(registry_path=temp_dir)
        assert Path(temp_dir).exists()
        assert (Path(temp_dir) / "skin.json").exists()
    
    def test_init_creates_default_widgets(self, registry):
        """Тест создания базовых виджетов"""
        with open(registry.skin_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "widgets" in data
        assert "layouts" in data
        assert "themes" in data
        
        # Проверяем наличие основных виджетов
        widgets = data["widgets"]
        assert "booking_form" in widgets
        assert "service_card" in widgets
        assert "time_slot_picker" in widgets
        assert "product_grid" in widgets
        assert "contact_form" in widgets
        assert "working_hours" in widgets
        assert "header" in widgets
        assert "footer" in widgets
    
    def test_get_widget_existing(self, registry):
        """Тест получения существующего виджета"""
        widget = registry.get_widget("booking_form")
        assert widget is not None
        assert widget["type"] == "form"
        assert "booking_form.html" in widget["template"]
    
    def test_get_widget_nonexistent(self, registry):
        """Тест получения несуществующего виджета"""
        widget = registry.get_widget("nonexistent_widget")
        assert widget is None
    
    def test_get_layout_existing(self, registry):
        """Тест получения существующего макета"""
        layout = registry.get_layout("booking_page")
        assert layout is not None
        assert layout["description"] == "Страница бронирования"
        assert "sections" in layout
    
    def test_get_layout_nonexistent(self, registry):
        """Тест получения несуществующего макета"""
        layout = registry.get_layout("nonexistent_layout")
        assert layout is None
    
    def test_get_theme_existing(self, registry):
        """Тест получения существующей темы"""
        theme = registry.get_theme("default")
        assert theme is not None
        assert "colors" in theme
        assert "fonts" in theme
    
    def test_get_theme_nonexistent(self, registry):
        """Тест получения несуществующей темы"""
        theme = registry.get_theme("nonexistent_theme")
        assert theme is None
    
    def test_list_widgets(self, registry):
        """Тест списка виджетов"""
        widgets = registry.list_widgets()
        assert isinstance(widgets, list)
        assert len(widgets) >= 8  # Минимум 8 базовых виджетов
        assert "booking_form" in widgets
        assert "service_card" in widgets
    
    def test_list_layouts(self, registry):
        """Тест списка макетов"""
        layouts = registry.list_layouts()
        assert isinstance(layouts, list)
        assert len(layouts) >= 3  # Минимум 3 базовых макета
        assert "booking_page" in layouts
        assert "ecommerce_page" in layouts
        assert "contact_page" in layouts
    
    def test_list_themes(self, registry):
        """Тест списка тем"""
        themes = registry.list_themes()
        assert isinstance(themes, list)
        assert len(themes) >= 2  # Минимум 2 базовых темы
        assert "default" in themes
        assert "modern" in themes
    
    def test_add_widget(self, registry):
        """Тест добавления нового виджета"""
        new_widget = {
            "type": "custom",
            "template": "custom.html",
            "css": "custom.css",
            "js": "custom.js",
            "props": ["param1", "param2"],
            "description": "Кастомный виджет"
        }
        
        result = registry.add_widget("custom_widget", new_widget)
        assert result is True
        
        # Проверяем, что виджет добавлен
        added_widget = registry.get_widget("custom_widget")
        assert added_widget is not None
        assert added_widget["type"] == "custom"
    
    def test_add_widget_invalid_json(self, registry):
        """Тест добавления виджета с неверным JSON"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = Exception("JSON error")
            
            result = registry.add_widget("test_widget", {})
            assert result is False
    
    def test_update_widget(self, registry):
        """Тест обновления существующего виджета"""
        # Сначала добавляем виджет
        original_widget = {
            "type": "original",
            "template": "original.html",
            "description": "Оригинальный виджет"
        }
        registry.add_widget("test_widget", original_widget)
        
        # Обновляем виджет
        updated_widget = {
            "type": "updated",
            "template": "updated.html",
            "description": "Обновленный виджет"
        }
        result = registry.update_widget("test_widget", updated_widget)
        assert result is True
        
        # Проверяем обновление
        widget = registry.get_widget("test_widget")
        assert widget["type"] == "updated"
        assert widget["description"] == "Обновленный виджет"
    
    def test_remove_widget_existing(self, registry):
        """Тест удаления существующего виджета"""
        # Сначала добавляем виджет
        widget = {"type": "test", "template": "test.html"}
        registry.add_widget("test_widget", widget)
        
        # Удаляем виджет
        result = registry.remove_widget("test_widget")
        assert result is True
        
        # Проверяем, что виджет удален
        removed_widget = registry.get_widget("test_widget")
        assert removed_widget is None
    
    def test_remove_widget_nonexistent(self, registry):
        """Тест удаления несуществующего виджета"""
        result = registry.remove_widget("nonexistent_widget")
        assert result is False
    
    def test_remove_widget_error(self, registry):
        """Тест ошибки при удалении виджета"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = Exception("File error")
            
            result = registry.remove_widget("test_widget")
            assert result is False
    
    def test_widget_structure(self, registry):
        """Тест структуры виджета"""
        widget = registry.get_widget("booking_form")
        
        required_fields = ["type", "template", "css", "js", "props", "description"]
        for field in required_fields:
            assert field in widget, f"Поле {field} отсутствует в виджете"
        
        assert widget["type"] == "form"
        assert isinstance(widget["props"], list)
        assert isinstance(widget["description"], str)
    
    def test_layout_structure(self, registry):
        """Тест структуры макета"""
        layout = registry.get_layout("booking_page")
        
        required_fields = ["description", "sections"]
        for field in required_fields:
            assert field in layout, f"Поле {field} отсутствует в макете"
        
        assert isinstance(layout["sections"], list)
        assert len(layout["sections"]) > 0
        
        # Проверяем структуру секций
        for section in layout["sections"]:
            assert "widget" in section
            assert "position" in section
    
    def test_theme_structure(self, registry):
        """Тест структуры темы"""
        theme = registry.get_theme("default")
        
        required_fields = ["description", "colors", "fonts"]
        for field in required_fields:
            assert field in theme, f"Поле {field} отсутствует в теме"
        
        # Проверяем цвета
        colors = theme["colors"]
        required_colors = ["primary", "secondary", "accent", "background", "text"]
        for color in required_colors:
            assert color in colors, f"Цвет {color} отсутствует в теме"
        
        # Проверяем шрифты
        fonts = theme["fonts"]
        required_fonts = ["heading", "body"]
        for font in required_fonts:
            assert font in fonts, f"Шрифт {font} отсутствует в теме"


if __name__ == "__main__":
    pytest.main([__file__]) 