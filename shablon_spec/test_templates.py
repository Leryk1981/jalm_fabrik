#!/usr/bin/env python3
"""
Тестовый скрипт для проверки шаблонов Shablon Spec
"""

import sys
import json
from pathlib import Path

# Добавляем путь к API
sys.path.append(str(Path(__file__).parent / "api"))

def test_registry():
    """Тест реестра шаблонов"""
    print("=== Тест реестра ===")
    
    from main import load_registry
    
    registry = load_registry()
    print(f"Всего шаблонов: {registry['metadata']['total_templates']}")
    print(f"Категории: {registry['metadata']['categories']}")
    
    for template in registry['templates']:
        print(f"- {template['id']} v{template['version']}: {template['description']}")

def test_template_validation():
    """Тест валидации шаблонов"""
    print("\n=== Тест валидации шаблонов ===")
    
    from main import validate_jalm_syntax
    
    templates_dir = Path(__file__).parent / "templates"
    
    for template_file in templates_dir.glob("*.jalm"):
        print(f"Валидация {template_file.name}:")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation = validate_jalm_syntax(content)
        print(f"  Валиден: {validation.is_valid}")
        
        if validation.errors:
            print(f"  Ошибки: {validation.errors}")
        
        if validation.warnings:
            print(f"  Предупреждения: {validation.warnings}")
        
        print()

def test_template_content():
    """Тест содержимого шаблонов"""
    print("=== Тест содержимого шаблонов ===")
    
    templates_dir = Path(__file__).parent / "templates"
    
    for template_file in templates_dir.glob("*.jalm"):
        print(f"\n{template_file.name}:")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Подсчет ключевых элементов
        begin_count = sum(1 for line in lines if line.strip().startswith('BEGIN'))
        end_count = sum(1 for line in lines if line.strip().startswith('END'))
        import_count = sum(1 for line in lines if line.strip().startswith('IMPORT'))
        run_count = sum(1 for line in lines if line.strip().startswith('RUN'))
        when_count = sum(1 for line in lines if line.strip().startswith('WHEN'))
        
        print(f"  BEGIN: {begin_count}")
        print(f"  END: {end_count}")
        print(f"  IMPORT: {import_count}")
        print(f"  RUN: {run_count}")
        print(f"  WHEN: {when_count}")
        
        # Проверка структуры
        if begin_count == end_count:
            print("  ✓ Структура корректна")
        else:
            print("  ✗ Ошибка структуры")

def test_hash_generation():
    """Тест генерации хешей"""
    print("\n=== Тест генерации хешей ===")
    
    from main import generate_hash
    
    templates_dir = Path(__file__).parent / "templates"
    
    for template_file in templates_dir.glob("*.jalm"):
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        hash_value = generate_hash(content)
        print(f"{template_file.name}: {hash_value}")

def test_api_models():
    """Тест моделей API"""
    print("\n=== Тест моделей API ===")
    
    from main import TemplateMetadata, TemplateExecutionRequest, TemplateValidationRequest
    
    # Тест TemplateMetadata
    metadata = TemplateMetadata(
        id="test-template",
        version="1.0.0",
        hash="test123",
        description="Test template",
        category="test",
        tags=["test"],
        author="Test Author",
        file="test.jalm",
        dependencies={},
        input_schema={},
        output_schema={},
        runtime={}
    )
    print(f"TemplateMetadata создан: {metadata.id}")
    
    # Тест TemplateExecutionRequest
    exec_request = TemplateExecutionRequest(
        template_id="test-template",
        params={"test": "value"}
    )
    print(f"TemplateExecutionRequest создан: {exec_request.template_id}")
    
    # Тест TemplateValidationRequest
    validation_request = TemplateValidationRequest(
        jalm_content="BEGIN test END"
    )
    print(f"TemplateValidationRequest создан")

if __name__ == "__main__":
    print("Тестирование Shablon Spec...\n")
    
    test_registry()
    test_template_validation()
    test_template_content()
    test_hash_generation()
    test_api_models()
    
    print("\nТестирование завершено!") 