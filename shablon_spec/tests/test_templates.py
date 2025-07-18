"""
Тесты для шаблонов Shablon Spec
"""

import sys
import json
from pathlib import Path

# Добавляем путь к API
sys.path.append(str(Path(__file__).parent.parent / "api"))

import pytest
from main import validate_jalm_syntax, generate_hash, load_registry


class TestTemplates:
    """Тесты для шаблонов"""
    
    def test_booking_flow_template(self):
        """Тест шаблона booking-flow"""
        template_path = Path(__file__).parent.parent / "templates" / "booking-flow.jalm"
        
        assert template_path.exists(), "Файл booking-flow.jalm не найден"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Валидация синтаксиса
        validation = validate_jalm_syntax(content)
        assert validation.is_valid, f"Ошибки валидации: {validation.errors}"
        
        # Проверка наличия ключевых элементов
        assert "BEGIN booking-flow" in content
        assert "IMPORT slot_validator" in content
        assert "IMPORT booking_widget" in content
        assert "IMPORT notify_system" in content
        assert "WHEN client REQUESTS slot" in content
        assert "RUN slot_uuid :=" in content
        assert "END" in content
    
    def test_ecommerce_order_template(self):
        """Тест шаблона ecommerce-order"""
        template_path = Path(__file__).parent.parent / "templates" / "ecommerce-order.jalm"
        
        assert template_path.exists(), "Файл ecommerce-order.jalm не найден"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Валидация синтаксиса
        validation = validate_jalm_syntax(content)
        assert validation.is_valid, f"Ошибки валидации: {validation.errors}"
        
        # Проверка наличия ключевых элементов
        assert "BEGIN ecommerce-order" in content
        assert "IMPORT notify_system" in content
        assert "WHEN client CREATES order" in content
        assert "RUN payment :=" in content
        assert "END" in content
    
    def test_notification_campaign_template(self):
        """Тест шаблона notification-campaign"""
        template_path = Path(__file__).parent.parent / "templates" / "notification-campaign.jalm"
        
        assert template_path.exists(), "Файл notification-campaign.jalm не найден"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Валидация синтаксиса
        validation = validate_jalm_syntax(content)
        assert validation.is_valid, f"Ошибки валидации: {validation.errors}"
        
        # Проверка наличия ключевых элементов
        assert "BEGIN notification-campaign" in content
        assert "IMPORT notify_system" in content
        assert "FOR EACH recipient" in content
        assert "SCHEDULE campaignReport" in content
        assert "END" in content


class TestJALMValidation:
    """Тесты валидации JALM синтаксиса"""
    
    def test_valid_jalm_syntax(self):
        """Тест валидного JALM синтаксиса"""
        valid_jalm = """
BEGIN test-template
  IMPORT test_function v1.0.0
  
  WHEN event TRIGGERS
    RUN result := test_function.execute(params)
  
  ON ERROR handleError
END
"""
        validation = validate_jalm_syntax(valid_jalm)
        assert validation.is_valid
        assert len(validation.errors) == 0
    
    def test_invalid_jalm_syntax_missing_end(self):
        """Тест невалидного JALM синтаксиса - отсутствует END"""
        invalid_jalm = """
BEGIN test-template
  IMPORT test_function v1.0.0
  
  WHEN event TRIGGERS
    RUN result := test_function.execute(params)
"""
        validation = validate_jalm_syntax(invalid_jalm)
        assert not validation.is_valid
        assert len(validation.errors) > 0
        assert "BEGIN/END" in validation.errors[0]
    
    def test_invalid_jalm_syntax_extra_end(self):
        """Тест невалидного JALM синтаксиса - лишний END"""
        invalid_jalm = """
BEGIN test-template
  IMPORT test_function v1.0.0
  
  WHEN event TRIGGERS
    RUN result := test_function.execute(params)
END
END
"""
        validation = validate_jalm_syntax(invalid_jalm)
        assert not validation.is_valid
        assert len(validation.errors) > 0
        assert "BEGIN/END" in validation.errors[0]
    
    def test_jalm_without_imports(self):
        """Тест JALM без импортов (предупреждение)"""
        jalm_without_imports = """
BEGIN test-template
  WHEN event TRIGGERS
    system.log("event triggered")
END
"""
        validation = validate_jalm_syntax(jalm_without_imports)
        assert validation.is_valid
        assert len(validation.warnings) > 0
        assert "импортов" in validation.warnings[0]
    
    def test_jalm_without_run(self):
        """Тест JALM без команд RUN (предупреждение)"""
        jalm_without_run = """
BEGIN test-template
  IMPORT test_function v1.0.0
  
  WHEN event TRIGGERS
    system.log("event triggered")
END
"""
        validation = validate_jalm_syntax(jalm_without_run)
        assert validation.is_valid
        assert len(validation.warnings) > 0
        assert "RUN" in validation.warnings[0]


class TestRegistry:
    """Тесты реестра шаблонов"""
    
    def test_registry_loading(self):
        """Тест загрузки реестра"""
        registry = load_registry()
        
        assert "templates" in registry
        assert "metadata" in registry
        assert "total_templates" in registry["metadata"]
        assert registry["metadata"]["total_templates"] >= 0
    
    def test_template_metadata(self):
        """Тест метаданных шаблонов"""
        registry = load_registry()
        
        for template in registry["templates"]:
            # Проверка обязательных полей
            assert "id" in template
            assert "version" in template
            assert "hash" in template
            assert "description" in template
            assert "category" in template
            assert "tags" in template
            assert "author" in template
            assert "file" in template
            assert "dependencies" in template
            assert "input_schema" in template
            assert "output_schema" in template
            assert "runtime" in template
            
            # Проверка типов
            assert isinstance(template["id"], str)
            assert isinstance(template["version"], str)
            assert isinstance(template["hash"], str)
            assert isinstance(template["tags"], list)
            assert isinstance(template["dependencies"], dict)
    
    def test_template_files_exist(self):
        """Тест существования файлов шаблонов"""
        registry = load_registry()
        templates_dir = Path(__file__).parent.parent / "templates"
        
        for template in registry["templates"]:
            template_file = templates_dir / template["file"]
            assert template_file.exists(), f"Файл {template['file']} не найден"


class TestHashGeneration:
    """Тесты генерации хешей"""
    
    def test_hash_generation(self):
        """Тест генерации хеша"""
        content = "test content"
        hash1 = generate_hash(content)
        hash2 = generate_hash(content)
        
        assert hash1 == hash2, "Хеши должны быть одинаковыми для одинакового контента"
        assert len(hash1) == 40, "Хеш должен быть 40 символов"
        assert hash1.isalnum(), "Хеш должен содержать только буквы и цифры"
    
    def test_hash_uniqueness(self):
        """Тест уникальности хешей"""
        content1 = "test content 1"
        content2 = "test content 2"
        
        hash1 = generate_hash(content1)
        hash2 = generate_hash(content2)
        
        assert hash1 != hash2, "Хеши должны быть разными для разного контента"


if __name__ == "__main__":
    pytest.main([__file__]) 