#!/usr/bin/env python3
"""
SkinStore - Доска 3: Git-репозиторий skins/
Папка "default" всегда обязательна: если клиент не завёл ничего, берём её как fallback
Каждая папка = новая leather. Делаете директорию → заливаете → включается автоматически через хеш
"""

import json
import os
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from skin_assembler import SkinAssembler

class SkinStore:
    def __init__(self, store_path: str = "skin_system/skins"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.assembler = SkinAssembler(store_path)
        
        # Инициализация default скина
        self._init_default_skin()
    
    def _init_default_skin(self):
        """Инициализация default скина как fallback"""
        default_dir = self.store_path / "default"
        default_dir.mkdir(exist_ok=True)
        
        # Создаем default skin.json
        default_skin = {
            "name": "Default Skin",
            "description": "Стандартный скин по умолчанию",
            "layout": "booking_page",
            "theme": "default",
            "version": "1.0.0",
            "author": "JALM System",
            "custom_css": "",
            "custom_js": "",
            "metadata": {
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
        
        default_skin_path = default_dir / "skin.json"
        if not default_skin_path.exists():
            with open(default_skin_path, 'w', encoding='utf-8') as f:
                json.dump(default_skin, f, indent=2, ensure_ascii=False)
        
        # Создаем default data.json
        default_data = {
            "app_name": "JALM Application",
            "services": [
                {"id": "service1", "name": "Услуга 1", "price": 1000, "duration": 60},
                {"id": "service2", "name": "Услуга 2", "price": 1500, "duration": 90}
            ],
            "working_hours": {
                "понедельник": {"start": "09:00", "end": "18:00"},
                "вторник": {"start": "09:00", "end": "18:00"},
                "среда": {"start": "09:00", "end": "18:00"},
                "четверг": {"start": "09:00", "end": "18:00"},
                "пятница": {"start": "09:00", "end": "18:00"},
                "суббота": {"start": "10:00", "end": "16:00"},
                "воскресенье": {"start": "10:00", "end": "16:00"}
            },
            "contact_info": {
                "phone": "+7 (999) 123-45-67",
                "email": "info@example.com",
                "address": "ул. Примерная, 1"
            },
            "api_url": "http://localhost:8080"
        }
        
        default_data_path = default_dir / "data.json"
        if not default_data_path.exists():
            with open(default_data_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)
        
        # Создаем default index.html
        default_html_path = default_dir / "index.html"
        if not default_html_path.exists():
            self.assembler.assemble_skin("default", default_skin, default_data)
    
    def create_skin(self, client_name: str, skin_config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """
        Создание нового скина для клиента
        """
        print(f"[SKIN STORE] Создание скина для клиента: {client_name}")
        
        # Генерируем хеш для уникальности
        skin_hash = self._generate_skin_hash(client_name, skin_config, data)
        
        # Создаем директорию скина
        skin_dir = self.store_path / client_name
        skin_dir.mkdir(exist_ok=True)
        
        # Добавляем хеш в конфигурацию
        skin_config["hash"] = skin_hash
        skin_config["client_name"] = client_name
        
        # Собираем скин
        index_path = self.assembler.assemble_skin(client_name, skin_config, data)
        
        # Создаем метаданные скина
        metadata = {
            "client_name": client_name,
            "skin_hash": skin_hash,
            "created_at": "2024-01-01T00:00:00Z",
            "files": [
                "index.html",
                "skin.json", 
                "data.json"
            ]
        }
        
        metadata_path = skin_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Скин создан: {skin_dir}")
        print(f"[HASH] Хеш скина: {skin_hash}")
        
        return str(skin_dir)
    
    def get_skin(self, client_name: str) -> Optional[Dict[str, Any]]:
        """
        Получение скина клиента (с fallback на default)
        """
        skin_dir = self.store_path / client_name
        
        if not skin_dir.exists():
            print(f"[WARNING] Скин {client_name} не найден, используем default")
            skin_dir = self.store_path / "default"
        
        if not skin_dir.exists():
            print(f"[ERROR] Default скин не найден")
            return None
        
        # Читаем конфигурацию скина
        skin_json_path = skin_dir / "skin.json"
        data_json_path = skin_dir / "data.json"
        index_html_path = skin_dir / "index.html"
        
        if not all([skin_json_path.exists(), data_json_path.exists(), index_html_path.exists()]):
            print(f"[ERROR] Неполный скин: {client_name}")
            return None
        
        with open(skin_json_path, 'r', encoding='utf-8') as f:
            skin_config = json.load(f)
        
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(index_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return {
            "client_name": client_name,
            "skin_config": skin_config,
            "data": data,
            "html_content": html_content,
            "skin_dir": str(skin_dir)
        }
    
    def update_skin(self, client_name: str, skin_config: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """
        Обновление существующего скина
        """
        try:
            skin_dir = self.store_path / client_name
            
            if not skin_dir.exists():
                print(f"[ERROR] Скин {client_name} не существует")
                return False
            
            # Обновляем скин
            self.assembler.assemble_skin(client_name, skin_config, data)
            
            # Обновляем метаданные
            metadata_path = skin_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            metadata["updated_at"] = "2024-01-01T00:00:00Z"
            metadata["skin_hash"] = self._generate_skin_hash(client_name, skin_config, data)
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] Скин {client_name} обновлен")
            return True
            
        except Exception as e:
            print(f"[ERROR] Ошибка обновления скина: {e}")
            return False
    
    def delete_skin(self, client_name: str) -> bool:
        """
        Удаление скина клиента (нельзя удалить default)
        """
        if client_name == "default":
            print(f"[ERROR] Нельзя удалить default скин")
            return False
        
        try:
            skin_dir = self.store_path / client_name
            
            if not skin_dir.exists():
                print(f"[WARNING] Скин {client_name} не существует")
                return True
            
            shutil.rmtree(skin_dir)
            print(f"[OK] Скин {client_name} удален")
            return True
            
        except Exception as e:
            print(f"[ERROR] Ошибка удаления скина: {e}")
            return False
    
    def list_skins(self) -> List[Dict[str, Any]]:
        """
        Список всех доступных скинов
        """
        skins = []
        
        for skin_dir in self.store_path.iterdir():
            if skin_dir.is_dir():
                metadata_path = skin_dir / "metadata.json"
                
                if metadata_path.exists():
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                else:
                    metadata = {
                        "client_name": skin_dir.name,
                        "skin_hash": "unknown",
                        "created_at": "unknown"
                    }
                
                skins.append({
                    "name": skin_dir.name,
                    "path": str(skin_dir),
                    "metadata": metadata
                })
        
        return skins
    
    def copy_skin(self, source_client: str, target_client: str) -> bool:
        """
        Копирование скина от одного клиента к другому
        """
        try:
            source_dir = self.store_path / source_client
            target_dir = self.store_path / target_client
            
            if not source_dir.exists():
                print(f"[ERROR] Исходный скин {source_client} не существует")
                return False
            
            if target_dir.exists():
                print(f"[WARNING] Целевой скин {target_client} уже существует, перезаписываем")
                shutil.rmtree(target_dir)
            
            shutil.copytree(source_dir, target_dir)
            
            # Обновляем метаданные
            metadata_path = target_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                metadata["client_name"] = target_client
                metadata["copied_from"] = source_client
                metadata["created_at"] = "2024-01-01T00:00:00Z"
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] Скин скопирован: {source_client} → {target_client}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Ошибка копирования скина: {e}")
            return False
    
    def validate_skin(self, client_name: str) -> Dict[str, Any]:
        """
        Валидация скина клиента
        """
        skin_dir = self.store_path / client_name
        
        validation_result = {
            "valid": False,
            "client_name": client_name,
            "errors": [],
            "warnings": []
        }
        
        if not skin_dir.exists():
            validation_result["errors"].append("Директория скина не существует")
            return validation_result
        
        # Проверяем обязательные файлы
        required_files = ["index.html", "skin.json", "data.json"]
        for file_name in required_files:
            file_path = skin_dir / file_name
            if not file_path.exists():
                validation_result["errors"].append(f"Отсутствует файл: {file_name}")
        
        # Проверяем skin.json
        skin_json_path = skin_dir / "skin.json"
        if skin_json_path.exists():
            try:
                with open(skin_json_path, 'r', encoding='utf-8') as f:
                    skin_config = json.load(f)
                
                required_fields = ["layout", "theme"]
                for field in required_fields:
                    if field not in skin_config:
                        validation_result["warnings"].append(f"Отсутствует поле в skin.json: {field}")
                
            except json.JSONDecodeError:
                validation_result["errors"].append("skin.json содержит неверный JSON")
        
        # Проверяем data.json
        data_json_path = skin_dir / "data.json"
        if data_json_path.exists():
            try:
                with open(data_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "app_name" not in data:
                    validation_result["warnings"].append("Отсутствует app_name в data.json")
                
            except json.JSONDecodeError:
                validation_result["errors"].append("data.json содержит неверный JSON")
        
        # Проверяем index.html
        index_html_path = skin_dir / "index.html"
        if index_html_path.exists():
            try:
                with open(index_html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                if len(html_content.strip()) == 0:
                    validation_result["errors"].append("index.html пустой")
                elif "<html" not in html_content.lower():
                    validation_result["warnings"].append("index.html не содержит HTML структуру")
                
            except Exception as e:
                validation_result["errors"].append(f"Ошибка чтения index.html: {e}")
        
        # Определяем результат валидации
        validation_result["valid"] = len(validation_result["errors"]) == 0
        
        return validation_result
    
    def _generate_skin_hash(self, client_name: str, skin_config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """
        Генерация хеша скина для уникальности
        """
        content = f"{client_name}:{json.dumps(skin_config, sort_keys=True)}:{json.dumps(data, sort_keys=True)}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
    
    def get_skin_url(self, client_name: str) -> str:
        """
        Получение URL для доступа к скину
        """
        return f"/skins/{client_name}/index.html"
    
    def export_skin(self, client_name: str, export_path: str) -> bool:
        """
        Экспорт скина в архив
        """
        try:
            skin_dir = self.store_path / client_name
            
            if not skin_dir.exists():
                print(f"[ERROR] Скин {client_name} не существует")
                return False
            
            # Создаем архив
            import zipfile
            zip_path = Path(export_path)
            zip_path.parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in skin_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(skin_dir)
                        zipf.write(file_path, arcname)
            
            print(f"[OK] Скин экспортирован: {zip_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Ошибка экспорта скина: {e}")
            return False

# Пример использования
if __name__ == "__main__":
    store = SkinStore()
    
    # Список скинов
    skins = store.list_skins()
    print("Доступные скины:")
    for skin in skins:
        print(f"  - {skin['name']}: {skin['metadata']}")
    
    # Валидация default скина
    validation = store.validate_skin("default")
    print(f"\nВалидация default скина: {validation['valid']}")
    if validation['errors']:
        print("Ошибки:", validation['errors'])
    if validation['warnings']:
        print("Предупреждения:", validation['warnings']) 