#!/usr/bin/env python3
"""
Unit тесты для SkinAssembler
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

from skin_assembler import SkinAssembler
from template_registry import TemplateRegistry


class TestSkinAssembler:
    """Тесты для SkinAssembler"""
    
    @pytest.fixture
    def temp_dir(self):
        """Временная директория для тестов"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def assembler(self, temp_dir):
        """Экземпляр SkinAssembler для тестов"""
        return SkinAssembler(skins_path=temp_dir)
    
    @pytest.fixture
    def sample_skin_config(self):
        """Пример конфигурации скина"""
        return {
            "name": "Test Skin",
            "description": "Тестовый скин",
            "layout": "booking_page",
            "theme": "default",
            "version": "1.0.0",
            "author": "Test",
            "custom_css": "",
            "custom_js": ""
        }
    
    @pytest.fixture
    def sample_data(self):
        """Пример данных для скина"""
        return {
            "app_name": "Test App",
            "services": [
                {"id": "service1", "name": "Услуга 1", "price": 1000, "duration": 60},
                {"id": "service2", "name": "Услуга 2", "price": 1500, "duration": 90}
            ],
            "working_hours": {
                "понедельник": {"start": "09:00", "end": "18:00"},
                "вторник": {"start": "09:00", "end": "18:00"}
            },
            "contact_info": {
                "phone": "+7 (999) 123-45-67",
                "email": "test@example.com"
            },
            "api_url": "http://localhost:8080"
        }
    
    def test_init_creates_directory(self, temp_dir):
        """Тест создания директории при инициализации"""
        assembler = SkinAssembler(skins_path=temp_dir)
        assert Path(temp_dir).exists()
    
    def test_init_creates_registry(self, assembler):
        """Тест создания реестра при инициализации"""
        assert assembler.registry is not None
        assert isinstance(assembler.registry, TemplateRegistry)
    
    def test_cdn_links_exist(self, assembler):
        """Тест наличия CDN ссылок"""
        assert "three_js" in assembler.cdn_links
        assert "font_awesome" in assembler.cdn_links
        assert "google_fonts" in assembler.cdn_links
        
        # Проверяем, что ссылки валидные
        for name, url in assembler.cdn_links.items():
            assert url.startswith("http")
            assert len(url) > 0
    
    def test_assemble_skin_creates_files(self, assembler, sample_skin_config, sample_data):
        """Тест создания файлов при сборке скина"""
        client_name = "test_client"
        
        result = assembler.assemble_skin(client_name, sample_skin_config, sample_data)
        
        assert result is not None
        assert Path(result).exists()
        
        # Проверяем создание файлов
        client_dir = Path(result)
        assert (client_dir / "index.html").exists()
        assert (client_dir / "skin.json").exists()
        assert (client_dir / "data.json").exists()
    
    def test_assemble_skin_with_nonexistent_layout(self, assembler, sample_data):
        """Тест сборки скина с несуществующим макетом"""
        skin_config = {
            "name": "Test Skin",
            "layout": "nonexistent_layout",
            "theme": "default",
            "custom_css": "",
            "custom_js": ""
        }
        
        result = assembler.assemble_skin("test_client", skin_config, sample_data)
        assert result is None
    
    def test_assemble_skin_with_nonexistent_theme(self, assembler, sample_data):
        """Тест сборки скина с несуществующей темой"""
        skin_config = {
            "name": "Test Skin",
            "layout": "booking_page",
            "theme": "nonexistent_theme",
            "custom_css": "",
            "custom_js": ""
        }
        
        result = assembler.assemble_skin("test_client", skin_config, sample_data)
        assert result is None
    
    def test_prepare_widget_data(self, assembler):
        """Тест подготовки данных для виджетов"""
        input_data = {
            "app_name": "Test App",
            "services": [{"id": "1", "name": "Service"}],
            "working_hours": {"monday": {"start": "09:00"}},
            "contact_info": {"phone": "123"},
            "products": [{"id": "1", "name": "Product"}],
            "api_url": "http://localhost:8080"
        }
        
        result = assembler._prepare_widget_data(input_data)
        
        assert result["app_name"] == "Test App"
        assert result["api_url"] == "http://localhost:8080"
        assert "services" in result
        assert "working_hours" in result
        assert "contact_info" in result
        assert "products" in result
    
    def test_prepare_widget_data_minimal(self, assembler):
        """Тест подготовки минимальных данных"""
        input_data = {"app_name": "Test App"}
        
        result = assembler._prepare_widget_data(input_data)
        
        assert result["app_name"] == "Test App"
        assert result["api_url"] == "http://localhost:8080"
    
    def test_generate_css(self, assembler):
        """Тест генерации CSS"""
        theme = {
            "colors": {
                "primary": "#2a5298",
                "secondary": "#1e3c72",
                "accent": "#28a745",
                "background": "#f5f5f5",
                "text": "#333333"
            },
            "fonts": {
                "heading": "Segoe UI, sans-serif",
                "body": "Segoe UI, sans-serif"
            }
        }
        custom_css = "/* Custom styles */"
        
        result = assembler._generate_css(theme, custom_css)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "/* Основные стили */" in result
        assert "/* Пользовательские стили */" in result
        assert custom_css in result
        assert "#2a5298" in result  # primary color
        assert "Segoe UI" in result  # font
    
    def test_generate_js(self, assembler):
        """Тест генерации JavaScript"""
        widget_data = {
            "app_name": "Test App",
            "api_url": "http://localhost:8080"
        }
        custom_js = "console.log('test');"
        
        result = assembler._generate_js(widget_data, custom_js)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "appConfig" in result
        assert "Test App" in result
        assert "http://localhost:8080" in result
        assert custom_js in result
        assert "Three.js" in result or "THREE" in result
    
    def test_generate_html_structure(self, assembler):
        """Тест генерации HTML структуры"""
        client_name = "test_client"
        layout = {
            "sections": [
                {"widget": "header", "position": "top"},
                {"widget": "booking_form", "position": "main"},
                {"widget": "footer", "position": "bottom"}
            ]
        }
        widget_data = {"app_name": "Test App"}
        
        result = assembler._generate_html_structure(client_name, layout, widget_data)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "header-section" in result
        assert "main-section" in result
        assert "footer-section" in result
        assert "three-container" in result
    
    def test_generate_widget_html_header(self, assembler):
        """Тест генерации HTML для виджета header"""
        data = {"app_name": "Test App"}
        
        result = assembler._generate_widget_html("header", data)
        
        assert isinstance(result, str)
        assert "Test App" in result
        assert "fas fa-rocket" in result
        assert "JALM Full Stack" in result
    
    def test_generate_widget_html_booking_form(self, assembler):
        """Тест генерации HTML для виджета booking_form"""
        data = {
            "services": [
                {"id": "service1", "name": "Услуга 1", "price": 1000, "duration": 60},
                {"id": "service2", "name": "Услуга 2", "price": 1500, "duration": 90}
            ]
        }
        
        result = assembler._generate_widget_html("booking_form", data)
        
        assert isinstance(result, str)
        assert "Забронировать услугу" in result
        assert "Услуга 1" in result
        assert "Услуга 2" in result
        assert "1000 ₽" in result
        assert "1500 ₽" in result
    
    def test_generate_widget_html_service_card(self, assembler):
        """Тест генерации HTML для виджета service_card"""
        data = {
            "services": [
                {"id": "service1", "name": "Услуга 1", "price": 1000, "duration": 60}
            ]
        }
        
        result = assembler._generate_widget_html("service_card", data)
        
        assert isinstance(result, str)
        assert "Услуга 1" in result
        assert "1000 ₽" in result
        assert "60 минут" in result
    
    def test_generate_widget_html_service_card_repeat(self, assembler):
        """Тест генерации HTML для виджета service_card с повторением"""
        data = {
            "services": [
                {"id": "service1", "name": "Услуга 1", "price": 1000, "duration": 60},
                {"id": "service2", "name": "Услуга 2", "price": 1500, "duration": 90}
            ]
        }
        
        result = assembler._generate_widget_html("service_card", data, repeat="services")
        
        assert isinstance(result, str)
        assert "services-grid" in result
        assert "Услуга 1" in result
        assert "Услуга 2" in result
    
    def test_generate_widget_html_time_slot_picker(self, assembler):
        """Тест генерации HTML для виджета time_slot_picker"""
        data = {}
        
        result = assembler._generate_widget_html("time_slot_picker", data)
        
        assert isinstance(result, str)
        assert "Выберите время" in result
        assert "time-slot-picker" in result
        assert "time-slots" in result
    
    def test_generate_widget_html_product_grid(self, assembler):
        """Тест генерации HTML для виджета product_grid"""
        data = {
            "products": [
                {"id": "product1", "name": "Товар 1", "price": 1000, "description": "Описание 1"},
                {"id": "product2", "name": "Товар 2", "price": 2000, "description": "Описание 2"}
            ]
        }
        
        result = assembler._generate_widget_html("product_grid", data)
        
        assert isinstance(result, str)
        assert "products-grid" in result
        assert "Товар 1" in result
        assert "Товар 2" in result
        assert "1000 ₽" in result
        assert "2000 ₽" in result
    
    def test_generate_widget_html_contact_form(self, assembler):
        """Тест генерации HTML для виджета contact_form"""
        data = {}
        
        result = assembler._generate_widget_html("contact_form", data)
        
        assert isinstance(result, str)
        assert "Свяжитесь с нами" in result
        assert "contact-form" in result
        assert "name" in result
        assert "email" in result
        assert "message" in result
    
    def test_generate_widget_html_working_hours(self, assembler):
        """Тест генерации HTML для виджета working_hours"""
        data = {
            "working_hours": {
                "понедельник": {"start": "09:00", "end": "18:00"},
                "вторник": {"start": "09:00", "end": "18:00"}
            }
        }
        
        result = assembler._generate_widget_html("working_hours", data)
        
        assert isinstance(result, str)
        assert "Часы работы" in result
        assert "working-hours" in result
        assert "понедельник" in result
        assert "вторник" in result
        assert "09:00" in result
        assert "18:00" in result
    
    def test_generate_widget_html_footer(self, assembler):
        """Тест генерации HTML для виджета footer"""
        data = {
            "app_name": "Test App",
            "contact_info": {
                "phone": "+7 (999) 123-45-67",
                "email": "test@example.com"
            }
        }
        
        result = assembler._generate_widget_html("footer", data)
        
        assert isinstance(result, str)
        assert "Test App" in result
        assert "footer" in result
        assert "+7 (999) 123-45-67" in result
        assert "test@example.com" in result
    
    def test_generate_widget_html_unknown(self, assembler):
        """Тест генерации HTML для неизвестного виджета"""
        data = {"test": "data"}
        
        result = assembler._generate_widget_html("unknown_widget", data)
        
        assert isinstance(result, str)
        assert "unknown_widget" in result
        assert "widget-fallback" in result
    
    def test_generate_html_complete(self, assembler, sample_skin_config, sample_data):
        """Тест полной генерации HTML"""
        client_name = "test_client"
        layout = assembler.registry.get_layout("booking_page")
        theme = assembler.registry.get_theme("default")
        custom_css = "/* Custom CSS */"
        custom_js = "console.log('test');"
        
        result = assembler._generate_html(client_name, layout, theme, sample_data, custom_css, custom_js)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "</html>" in result
        assert "Test App" in result
        assert custom_css in result
        assert custom_js in result
        assert "three.js" in result.lower()
        assert "font-awesome" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__]) 