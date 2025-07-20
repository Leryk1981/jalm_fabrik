#!/usr/bin/env python3
"""
Тесты для CLI Skin-As-Code системы
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Добавляем путь к модулю для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cli import SkinCLI


class TestSkinCLI:
    """Тесты для SkinCLI"""
    
    @pytest.fixture
    def temp_dir(self):
        """Временная директория для тестов"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cli(self, temp_dir):
        """Экземпляр SkinCLI для тестов"""
        return SkinCLI(skins_path=temp_dir)
    
    def test_init_creates_directory(self, temp_dir):
        """Тест создания директории при инициализации"""
        cli = SkinCLI(skins_path=temp_dir)
        assert Path(temp_dir).exists()
    
    def test_init_creates_store_and_assembler(self, cli):
        """Тест создания store и assembler при инициализации"""
        assert cli.store is not None
        assert cli.assembler is not None
    
    def test_create_skin_command_success(self, cli):
        """Тест успешного выполнения команды создания скина"""
        with patch('builtins.input', side_effect=['test_client', '2f7cff', 'booking_page']):
            result = cli.create_skin_command()
            assert result is True
    
    def test_create_skin_command_with_args(self, cli):
        """Тест создания скина с аргументами"""
        result = cli.create_skin_command(client="test_client", color="2f7cff", layout="booking_page")
        assert result is True
        
        # Проверяем создание файлов
        client_path = cli.store.skins_path / "test_client"
        assert client_path.exists()
        assert (client_path / "index.html").exists()
    
    def test_create_skin_command_invalid_color(self, cli):
        """Тест создания скина с неверным цветом"""
        result = cli.create_skin_command(client="test_client", color="invalid_color", layout="booking_page")
        assert result is False
    
    def test_create_skin_command_invalid_layout(self, cli):
        """Тест создания скина с неверным макетом"""
        result = cli.create_skin_command(client="test_client", color="2f7cff", layout="invalid_layout")
        assert result is False
    
    def test_list_command(self, cli):
        """Тест команды списка скинов"""
        # Создаем тестовый скин
        cli.create_skin_command(client="test_client", color="2f7cff", layout="booking_page")
        
        with patch('builtins.print') as mock_print:
            result = cli.list_command()
            assert result is True
            mock_print.assert_called()
    
    def test_validate_command_success(self, cli):
        """Тест успешной валидации скина"""
        # Создаем тестовый скин
        cli.create_skin_command(client="test_client", color="2f7cff", layout="booking_page")
        
        result = cli.validate_command(client="test_client")
        assert result is True
    
    def test_validate_command_nonexistent(self, cli):
        """Тест валидации несуществующего скина"""
        result = cli.validate_command(client="nonexistent_client")
        assert result is False
    
    def test_copy_command_success(self, cli):
        """Тест успешного копирования скина"""
        # Создаем исходный скин
        cli.create_skin_command(client="source_client", color="2f7cff", layout="booking_page")
        
        result = cli.copy_command(source="source_client", target="target_client")
        assert result is True
        
        # Проверяем копирование
        source_path = cli.store.skins_path / "source_client"
        target_path = cli.store.skins_path / "target_client"
        assert target_path.exists()
    
    def test_copy_command_source_nonexistent(self, cli):
        """Тест копирования несуществующего скина"""
        result = cli.copy_command(source="nonexistent_source", target="target_client")
        assert result is False
    
    def test_export_command_success(self, cli):
        """Тест успешного экспорта скина"""
        # Создаем тестовый скин
        cli.create_skin_command(client="test_client", color="2f7cff", layout="booking_page")
        
        export_path = cli.store.skins_path / "test_client_export.zip"
        
        result = cli.export_command(client="test_client", path=str(export_path))
        assert result is True
        assert export_path.exists()
    
    def test_export_command_nonexistent(self, cli):
        """Тест экспорта несуществующего скина"""
        export_path = cli.store.skins_path / "nonexistent_export.zip"
        
        result = cli.export_command(client="nonexistent_client", path=str(export_path))
        assert result is False
    
    def test_delete_command_success(self, cli):
        """Тест успешного удаления скина"""
        # Создаем тестовый скин
        cli.create_skin_command(client="test_client", color="2f7cff", layout="booking_page")
        
        result = cli.delete_command(client="test_client")
        assert result is True
        
        # Проверяем удаление
        client_path = cli.store.skins_path / "test_client"
        assert not client_path.exists()
    
    def test_delete_command_nonexistent(self, cli):
        """Тест удаления несуществующего скина"""
        result = cli.delete_command(client="nonexistent_client")
        assert result is False
    
    def test_delete_command_default(self, cli):
        """Тест попытки удаления default скина"""
        result = cli.delete_command(client="default")
        assert result is False
    
    def test_serve_command(self, cli):
        """Тест команды serve"""
        with patch('uvicorn.run') as mock_run:
            result = cli.serve_command(host="localhost", port=8080)
            assert result is True
            mock_run.assert_called_once()
    
    def test_validate_color_valid(self, cli):
        """Тест валидации корректного цвета"""
        assert cli._validate_color("#2f7cff") is True
        assert cli._validate_color("2f7cff") is True
        assert cli._validate_color("#ff0000") is True
    
    def test_validate_color_invalid(self, cli):
        """Тест валидации неверного цвета"""
        assert cli._validate_color("invalid") is False
        assert cli._validate_color("#invalid") is False
        assert cli._validate_color("12345") is False
        assert cli._validate_color("") is False
    
    def test_validate_layout_valid(self, cli):
        """Тест валидации корректного макета"""
        assert cli._validate_layout("booking_page") is True
        assert cli._validate_layout("ecommerce_page") is True
        assert cli._validate_layout("contact_page") is True
    
    def test_validate_layout_invalid(self, cli):
        """Тест валидации неверного макета"""
        assert cli._validate_layout("invalid_layout") is False
        assert cli._validate_layout("") is False
    
    def test_generate_random_color(self, cli):
        """Тест генерации случайного цвета"""
        color = cli._generate_random_color()
        assert cli._validate_color(color) is True
    
    def test_interactive_input(self, cli):
        """Тест интерактивного ввода"""
        with patch('builtins.input', side_effect=['test_client', '2f7cff', 'booking_page']):
            client, color, layout = cli._get_interactive_input()
            assert client == "test_client"
            assert color == "2f7cff"
            assert layout == "booking_page"
    
    def test_interactive_input_with_defaults(self, cli):
        """Тест интерактивного ввода с пустыми значениями"""
        with patch('builtins.input', side_effect=['', '', '']):
            client, color, layout = cli._get_interactive_input()
            assert client == "default"
            assert cli._validate_color(color) is True
            assert layout == "booking_page"
    
    def test_create_skin_with_custom_data(self, cli):
        """Тест создания скина с кастомными данными"""
        custom_data = {
            "app_name": "Custom App",
            "services": [
                {"id": "custom1", "name": "Custom Service", "price": 2000, "duration": 120}
            ]
        }
        
        with patch.object(cli.store, 'create_skin', return_value=True) as mock_create:
            result = cli.create_skin_command(
                client="custom_client", 
                color="2f7cff", 
                layout="booking_page",
                custom_data=custom_data
            )
            assert result is True
            mock_create.assert_called_once()
    
    def test_error_handling(self, cli):
        """Тест обработки ошибок"""
        with patch.object(cli.store, 'create_skin', side_effect=Exception("Test error")):
            result = cli.create_skin_command(client="test_client", color="2f7cff", layout="booking_page")
            assert result is False
    
    def test_cli_with_arguments(self, cli):
        """Тест CLI с аргументами командной строки"""
        with patch('sys.argv', ['skin_cli.py', 'create-skin', '--client=test', '--color=2f7cff']):
            with patch.object(cli, 'create_skin_command', return_value=True) as mock_create:
                cli.run()
                mock_create.assert_called_once()
    
    def test_cli_help(self, cli):
        """Тест вывода справки"""
        with patch('sys.argv', ['skin_cli.py', '--help']):
            with patch('sys.stderr') as mock_stderr:
                result = cli.run()
                assert result is True
    
    def test_cli_invalid_command(self, cli):
        """Тест неверной команды"""
        with patch('sys.argv', ['skin_cli.py', 'invalid-command']):
            with patch('sys.stderr') as mock_stderr:
                result = cli.run()
                assert result is True


class TestCLIIntegration:
    """Интеграционные тесты для CLI"""
    
    @pytest.fixture
    def temp_dir(self):
        """Временная директория для тестов"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_full_workflow(self, temp_dir):
        """Тест полного рабочего процесса"""
        cli = SkinCLI(skins_path=temp_dir)
        
        # 1. Создание скина
        result1 = cli.create_skin_command(
            client="workflow_test", 
            color="2f7cff", 
            layout="booking_page"
        )
        assert result1 is True
        
        # 2. Валидация скина
        result2 = cli.validate_command(client="workflow_test")
        assert result2 is True
        
        # 3. Копирование скина
        result3 = cli.copy_command(source="workflow_test", target="workflow_copy")
        assert result3 is True
        
        # 4. Экспорт скина
        export_path = Path(temp_dir) / "workflow_export.zip"
        result4 = cli.export_command(client="workflow_test", path=str(export_path))
        assert result4 is True
        assert export_path.exists()
        
        # 5. Список скинов
        with patch('builtins.print') as mock_print:
            result5 = cli.list_command()
            assert result5 is True
        
        # 6. Удаление скина
        result6 = cli.delete_command(client="workflow_test")
        assert result6 is True
    
    def test_multiple_skins_management(self, temp_dir):
        """Тест управления множественными скинами"""
        cli = SkinCLI(skins_path=temp_dir)
        
        # Создаем несколько скинов
        clients = ["client1", "client2", "client3"]
        colors = ["2f7cff", "ff0000", "00ff00"]
        layouts = ["booking_page", "ecommerce_page", "contact_page"]
        
        for client, color, layout in zip(clients, colors, layouts):
            result = cli.create_skin_command(client=client, color=color, layout=layout)
            assert result is True
        
        # Проверяем список
        with patch('builtins.print') as mock_print:
            cli.list_command()
            # Проверяем, что все скины в списке
            calls = mock_print.call_args_list
            output = " ".join([str(call) for call in calls])
            for client in clients:
                assert client in output


if __name__ == "__main__":
    pytest.main([__file__]) 