"""
Модуль интеграции Research Layer с JALM компонентами
"""

import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JALMIntegration:
    """
    Класс для интеграции Research Layer с JALM компонентами
    """
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.cwd()
        self.research_path = self.base_path / "research"
        self.tool_catalog_path = self.base_path / "tool_catalog"
        self.shablon_spec_path = self.base_path / "shablon_spec"
        self.tula_spec_path = self.base_path / "tula_spec"
        
    def integrate_with_tool_catalog(self) -> bool:
        """
        Интеграция с Tool Catalog
        Копирует артефакты в tool_catalog/ директорию
        """
        try:
            logger.info("📚 Интеграция с Tool Catalog...")
            
            # Создаем директорию если не существует
            self.tool_catalog_path.mkdir(exist_ok=True)
            
            # Копируем артефакты
            artifacts_to_copy = [
                ("jalm_templates.json", "templates.json"),
                ("jalm_functions.json", "functions.json"),
                ("pattern_analysis.json", "analysis.json"),
                ("pattern_groups.json", "groups.json")
            ]
            
            for source, target in artifacts_to_copy:
                source_path = self.research_path / "patterns" / source
                target_path = self.tool_catalog_path / target
                
                if source_path.exists():
                    shutil.copy2(source_path, target_path)
                    logger.info(f"   ✅ Скопирован {source} → {target}")
                else:
                    logger.warning(f"   ⚠️ Файл {source} не найден")
            
            # Создаем индексный файл
            self._create_tool_catalog_index()
            
            logger.info("✅ Интеграция с Tool Catalog завершена")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка интеграции с Tool Catalog: {e}")
            return False
    
    def integrate_with_shablon_spec(self) -> bool:
        """
        Интеграция с Shablon Spec
        Добавляет новые шаблоны в shablon_spec/registry/
        """
        try:
            logger.info("📋 Интеграция с Shablon Spec...")
            
            # Проверяем наличие артефактов
            templates_file = self.research_path / "patterns" / "jalm_templates.json"
            if not templates_file.exists():
                logger.error("❌ Файл jalm_templates.json не найден")
                return False
            
            # Загружаем шаблоны
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            # Создаем директорию registry если не существует
            registry_path = self.shablon_spec_path / "registry"
            registry_path.mkdir(parents=True, exist_ok=True)
            
            # Загружаем существующие шаблоны
            existing_templates_file = registry_path / "templates.json"
            existing_templates = []
            
            if existing_templates_file.exists():
                with open(existing_templates_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Убеждаемся что это список
                    if isinstance(loaded_data, list):
                        existing_templates = loaded_data
                    else:
                        logger.warning("   ⚠️ Существующие шаблоны не в формате списка, начинаем с пустого списка")
            
            # Добавляем новые шаблоны
            for template in templates:
                # Проверяем что template это словарь
                if isinstance(template, dict):
                    # Проверяем дубликаты
                    if not any(isinstance(t, dict) and t.get('name') == template.get('name') for t in existing_templates):
                        template['source'] = 'research_layer'
                        template['integrated_at'] = datetime.now().isoformat()
                        existing_templates.append(template)
                        logger.info(f"   ✅ Добавлен шаблон: {template.get('name')}")
                    else:
                        logger.info(f"   ⚠️ Шаблон {template.get('name')} уже существует")
                else:
                    logger.warning(f"   ⚠️ Пропущен невалидный шаблон: {template}")
            
            # Сохраняем обновленные шаблоны
            with open(existing_templates_file, 'w', encoding='utf-8') as f:
                json.dump(existing_templates, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Интеграция с Shablon Spec завершена. Всего шаблонов: {len(existing_templates)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка интеграции с Shablon Spec: {e}")
            return False
    
    def integrate_with_tula_registry(self) -> bool:
        """
        Интеграция с Tula Registry
        Добавляет новые функции в tula_spec/registry/
        """
        try:
            logger.info("🔧 Интеграция с Tula Registry...")
            
            # Проверяем наличие артефактов
            functions_file = self.research_path / "patterns" / "jalm_functions.json"
            if not functions_file.exists():
                logger.error("❌ Файл jalm_functions.json не найден")
                return False
            
            # Загружаем функции
            with open(functions_file, 'r', encoding='utf-8') as f:
                functions = json.load(f)
            
            # Создаем директорию registry если не существует
            registry_path = self.tula_spec_path / "registry"
            registry_path.mkdir(parents=True, exist_ok=True)
            
            # Загружаем существующие функции
            existing_functions_file = registry_path / "functions.json"
            existing_functions = []
            
            if existing_functions_file.exists():
                with open(existing_functions_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Убеждаемся что это список
                    if isinstance(loaded_data, list):
                        existing_functions = loaded_data
                    else:
                        logger.warning("   ⚠️ Существующие функции не в формате списка, начинаем с пустого списка")
            
            # Добавляем новые функции
            for function in functions:
                # Проверяем что function это словарь
                if isinstance(function, dict):
                    # Проверяем дубликаты
                    if not any(isinstance(f, dict) and f.get('name') == function.get('name') for f in existing_functions):
                        function['source'] = 'research_layer'
                        function['integrated_at'] = datetime.now().isoformat()
                        existing_functions.append(function)
                        logger.info(f"   ✅ Добавлена функция: {function.get('name')}")
                    else:
                        logger.info(f"   ⚠️ Функция {function.get('name')} уже существует")
                else:
                    logger.warning(f"   ⚠️ Пропущена невалидная функция: {function}")
            
            # Сохраняем обновленные функции
            with open(existing_functions_file, 'w', encoding='utf-8') as f:
                json.dump(existing_functions, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Интеграция с Tula Registry завершена. Всего функций: {len(existing_functions)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка интеграции с Tula Registry: {e}")
            return False
    
    def _create_tool_catalog_index(self) -> None:
        """Создает индексный файл для Tool Catalog"""
        try:
            index_data = {
                "catalog_info": {
                    "name": "JALM Tool Catalog",
                    "version": "1.0.0",
                    "description": "Каталог инструментов и шаблонов JALM",
                    "last_updated": datetime.now().isoformat(),
                    "source": "research_layer"
                },
                "files": {
                    "templates": "templates.json",
                    "functions": "functions.json", 
                    "analysis": "analysis.json",
                    "groups": "groups.json"
                },
                "statistics": {
                    "total_templates": 0,
                    "total_functions": 0,
                    "total_groups": 0
                }
            }
            
            # Подсчитываем статистику
            for file_name, file_path in index_data["files"].items():
                full_path = self.tool_catalog_path / file_path
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            index_data["statistics"][f"total_{file_name}"] = len(data)
            
            # Сохраняем индекс
            index_file = self.tool_catalog_path / "index.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
            logger.info("   ✅ Создан индексный файл tool_catalog/index.json")
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания индекса: {e}")
    
    def run_full_integration(self) -> Dict[str, bool]:
        """
        Запуск полной интеграции со всеми компонентами
        """
        logger.info("🚀 Запуск полной интеграции Research Layer с JALM...")
        
        results = {
            'tool_catalog': self.integrate_with_tool_catalog(),
            'shablon_spec': self.integrate_with_shablon_spec(),
            'tula_registry': self.integrate_with_tula_registry()
        }
        
        success_count = sum(results.values())
        total_count = len(results)
        
        logger.info(f"📊 Результаты интеграции: {success_count}/{total_count} успешно")
        
        for component, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"   {component}: {status}")
        
        return results
    
    def validate_integration(self) -> Dict[str, bool]:
        """
        Проверка корректности интеграции
        """
        logger.info("🔍 Проверка корректности интеграции...")
        
        validation_results = {}
        
        # Проверяем Tool Catalog
        tool_catalog_files = [
            "templates.json",
            "functions.json", 
            "analysis.json",
            "groups.json",
            "index.json"
        ]
        
        tool_catalog_valid = all(
            (self.tool_catalog_path / file).exists() 
            for file in tool_catalog_files
        )
        validation_results['tool_catalog'] = tool_catalog_valid
        
        # Проверяем Shablon Spec
        shablon_spec_valid = (
            self.shablon_spec_path / "registry" / "templates.json"
        ).exists()
        validation_results['shablon_spec'] = shablon_spec_valid
        
        # Проверяем Tula Registry
        tula_registry_valid = (
            self.tula_spec_path / "registry" / "functions.json"
        ).exists()
        validation_results['tula_registry'] = tula_registry_valid
        
        # Выводим результаты
        for component, valid in validation_results.items():
            status = "✅" if valid else "❌"
            logger.info(f"   {component}: {status}")
        
        return validation_results 