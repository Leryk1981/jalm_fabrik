#!/usr/bin/env python3
"""
Unit тесты для SkinStore
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

from skin_store import SkinStore


class TestSkinStore:
    """Тесты для SkinStore"""
    
    @pytest.fixture
    def temp_dir(self):
        """Временная директория для тестов"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def store(self, temp_dir):
        """Экземпляр SkinStore для тестов"""
        return SkinStore(skins_path=temp_dir)
    
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
            "custom_css": "/* Custom CSS */",
            "custom_js": "console.log('test');"
        }
    
    @pytest.fixture
    def sample_data(self):
        """Пример данных для скина"""
        return {
            "app_name": "Test App",
            "services": [
                {"id": "service1", "name": "Услуга 1", "price": 1000, "duration": 60}
            ],
            "api_url": "http://localhost:8080"
        }
    
    def test_init_creates_directory(self, temp_dir):
        """Тест создания директории при инициализации"""
        store = SkinStore(skins_path=temp_dir)
        assert Path(temp_dir).exists()
    
    def test_init_creates_default_skin(self, store):
        """Тест создания default скина при инициализации"""
        default_skin_path = store.skins_path / "default"
        assert default_skin_path.exists()
        assert (default_skin_path / "index.html").exists()
        assert (default_skin_path / "skin.json").exists()
        assert (default_skin_path / "data.json").exists()
        assert (default_skin_path / "metadata.json").exists()
    
    def test_create_skin_success(self, store, sample_skin_config, sample_data):
        """Тест успешного создания скина"""
        client_name = "test_client"
        
        result = store.create_skin(client_name, sample_skin_config, sample_data)
        
        assert result is True
        
        # Проверяем создание файлов
        client_skin_path = store.skins_path / client_name
        assert client_skin_path.exists()
        assert (client_skin_path / "index.html").exists()
        assert (client_skin_path / "skin.json").exists()
        assert (client_skin_path / "data.json").exists()
        assert (client_skin_path / "metadata.json").exists()
    
    def test_create_skin_existing(self, store, sample_skin_config, sample_data):
        """Тест создания скина с существующим именем"""
        client_name = "test_client"
        
        # Создаем скин первый раз
        result1 = store.create_skin(client_name, sample_skin_config, sample_data)
        assert result1 is True
        
        # Пытаемся создать скин с тем же именем
        result2 = store.create_skin(client_name, sample_skin_config, sample_data)
        assert result2 is False
    
    def test_create_skin_invalid_config(self, store, sample_data):
        """Тест создания скина с неверной конфигурацией"""
        client_name = "test_client"
        invalid_config = {"invalid": "config"}
        
        result = store.create_skin(client_name, invalid_config, sample_data)
        assert result is False
    
    def test_create_skin_invalid_data(self, store, sample_skin_config):
        """Тест создания скина с неверными данными"""
        client_name = "test_client"
        invalid_data = {"invalid": "data"}
        
        result = store.create_skin(client_name, sample_skin_config, invalid_data)
        assert result is False
    
    def test_get_skin_existing(self, store, sample_skin_config, sample_data):
        """Тест получения существующего скина"""
        client_name = "test_client"
        store.create_skin(client_name, sample_skin_config, sample_data)
        
        skin = store.get_skin(client_name)
        
        assert skin is not None
        assert skin["name"] == client_name
        assert skin["config"]["name"] == "Test Skin"
        assert skin["data"]["app_name"] == "Test App"
    
    def test_get_skin_nonexistent(self, store):
        """Тест получения несуществующего скина"""
        skin = store.get_skin("nonexistent_client")
        assert skin is None
    
    def test_get_skin_default_fallback(self, store):
        """Тест получения default скина как fallback"""
        skin = store.get_skin("default")
        assert skin is not None
        assert skin["name"] == "default"
    
    def test_list_skins(self, store, sample_skin_config, sample_data):
        """Тест списка скинов"""
        # Создаем несколько скинов
        store.create_skin("client1", sample_skin_config, sample_data)
        store.create_skin("client2", sample_skin_config, sample_data)
        
        skins = store.list_skins()
        
        assert isinstance(skins, list)
        assert len(skins) >= 3  # default + client1 + client2
        
        skin_names = [skin["name"] for skin in skins]
        assert "default" in skin_names
        assert "client1" in skin_names
        assert "client2" in skin_names
    
    def test_update_skin_existing(self, store, sample_skin_config, sample_data):
        """Тест обновления существующего скина"""
        client_name = "test_client"
        store.create_skin(client_name, sample_skin_config, sample_data)
        
        # Обновляем конфигурацию
        updated_config = sample_skin_config.copy()
        updated_config["name"] = "Updated Test Skin"
        
        result = store.update_skin(client_name, updated_config, sample_data)
        assert result is True
        
        # Проверяем обновление
        skin = store.get_skin(client_name)
        assert skin["config"]["name"] == "Updated Test Skin"
    
    def test_update_skin_nonexistent(self, store, sample_skin_config, sample_data):
        """Тест обновления несуществующего скина"""
        result = store.update_skin("nonexistent_client", sample_skin_config, sample_data)
        assert result is False
    
    def test_delete_skin_existing(self, store, sample_skin_config, sample_data):
        """Тест удаления существующего скина"""
        client_name = "test_client"
        store.create_skin(client_name, sample_skin_config, sample_data)
        
        result = store.delete_skin(client_name)
        assert result is True
        
        # Проверяем удаление
        skin = store.get_skin(client_name)
        assert skin is None
    
    def test_delete_skin_nonexistent(self, store):
        """Тест удаления несуществующего скина"""
        result = store.delete_skin("nonexistent_client")
        assert result is False
    
    def test_delete_skin_default(self, store):
        """Тест попытки удаления default скина"""
        result = store.delete_skin("default")
        assert result is False  # default скин нельзя удалить
    
    def test_copy_skin_success(self, store, sample_skin_config, sample_data):
        """Тест успешного копирования скина"""
        source_name = "source_client"
        target_name = "target_client"
        
        # Создаем исходный скин
        store.create_skin(source_name, sample_skin_config, sample_data)
        
        result = store.copy_skin(source_name, target_name)
        assert result is True
        
        # Проверяем копирование
        source_skin = store.get_skin(source_name)
        target_skin = store.get_skin(target_name)
        
        assert target_skin is not None
        assert target_skin["config"]["name"] == source_skin["config"]["name"]
        assert target_skin["data"]["app_name"] == source_skin["data"]["app_name"]
    
    def test_copy_skin_source_nonexistent(self, store):
        """Тест копирования несуществующего скина"""
        result = store.copy_skin("nonexistent_source", "target")
        assert result is False
    
    def test_copy_skin_target_exists(self, store, sample_skin_config, sample_data):
        """Тест копирования в существующий target"""
        source_name = "source_client"
        target_name = "target_client"
        
        # Создаем оба скина
        store.create_skin(source_name, sample_skin_config, sample_data)
        store.create_skin(target_name, sample_skin_config, sample_data)
        
        result = store.copy_skin(source_name, target_name)
        assert result is False  # target уже существует
    
    def test_validate_skin_valid(self, store, sample_skin_config, sample_data):
        """Тест валидации корректного скина"""
        client_name = "test_client"
        store.create_skin(client_name, sample_skin_config, sample_data)

        result = store.validate_skin(client_name)
        assert result["valid"] is True
    
    def test_validate_skin_nonexistent(self, store):
        """Тест валидации несуществующего скина"""
        result = store.validate_skin("nonexistent_client")
        assert result["valid"] is False
    
    def test_validate_skin_missing_files(self, store):
        """Тест валидации скина с отсутствующими файлами"""
        client_name = "test_client"
        client_path = store.skins_path / client_name
        client_path.mkdir(exist_ok=True)

        # Создаем только часть файлов
        (client_path / "skin.json").write_text("{}")

        result = store.validate_skin(client_name)
        assert result["valid"] is False
    
    def test_export_skin_success(self, store, sample_skin_config, sample_data):
        """Тест успешного экспорта скина"""
        client_name = "test_client"
        store.create_skin(client_name, sample_skin_config, sample_data)
        
        export_path = store.skins_path / f"{client_name}_export.zip"
        
        result = store.export_skin(client_name, str(export_path))
        assert result is True
        assert export_path.exists()
    
    def test_export_skin_nonexistent(self, store):
        """Тест экспорта несуществующего скина"""
        export_path = store.skins_path / "nonexistent_export.zip"
        
        result = store.export_skin("nonexistent_client", str(export_path))
        assert result is False
    
    def test_get_skin_path(self, store, sample_skin_config, sample_data):
        """Тест получения пути к скину"""
        client_name = "test_client"
        store.create_skin(client_name, sample_skin_config, sample_data)
        
        path = store.get_skin_path(client_name)
        expected_path = store.skins_path / client_name
        
        assert path == expected_path
        assert path.exists()
    
    def test_get_skin_path_nonexistent(self, store):
        """Тест получения пути к несуществующему скину"""
        path = store.get_skin_path("nonexistent_client")
        expected_path = store.skins_path / "nonexistent_client"
        
        assert path == expected_path
        assert not path.exists()
    
    def test_skin_exists(self, store, sample_skin_config, sample_data):
        """Тест проверки существования скина"""
        client_name = "test_client"
        
        # Скин не существует
        assert store.skin_exists(client_name) is False
        
        # Создаем скин
        store.create_skin(client_name, sample_skin_config, sample_data)
        
        # Скин существует
        assert store.skin_exists(client_name) is True
    
    def test_get_skin_info(self, store, sample_skin_config, sample_data):
        """Тест получения информации о скине"""
        client_name = "test_client"
        store.create_skin(client_name, sample_skin_config, sample_data)
        
        info = store.get_skin_info(client_name)
        
        assert info is not None
        assert "name" in info
        assert "created_at" in info
        assert "updated_at" in info
        assert "version" in info
        assert "author" in info
    
    def test_get_skin_info_nonexistent(self, store):
        """Тест получения информации о несуществующем скине"""
        info = store.get_skin_info("nonexistent_client")
        assert info is None
    
    def test_search_skins(self, store, sample_skin_config, sample_data):
        """Тест поиска скинов"""
        # Создаем скины с разными именами
        config1 = sample_skin_config.copy()
        config1["name"] = "Barber Shop Skin"
        store.create_skin("barber", config1, sample_data)
        
        config2 = sample_skin_config.copy()
        config2["name"] = "Restaurant Skin"
        store.create_skin("restaurant", config2, sample_data)
        
        # Поиск по имени
        results = store.search_skins("barber")
        assert len(results) == 1
        assert results[0]["name"] == "barber"
        
        # Поиск по описанию
        results = store.search_skins("shop")
        assert len(results) >= 1
        
        # Поиск несуществующего
        results = store.search_skins("nonexistent")
        assert len(results) == 0
    
    def test_get_skin_stats(self, store, sample_skin_config, sample_data):
        """Тест получения статистики скинов"""
        # Создаем несколько скинов
        store.create_skin("client1", sample_skin_config, sample_data)
        store.create_skin("client2", sample_skin_config, sample_data)
        
        stats = store.get_skin_stats()
        
        assert isinstance(stats, dict)
        assert "total_skins" in stats
        assert "default_skin" in stats
        assert "custom_skins" in stats
        assert stats["total_skins"] >= 3  # default + client1 + client2
        assert stats["custom_skins"] >= 2  # client1 + client2


if __name__ == "__main__":
    pytest.main([__file__]) 