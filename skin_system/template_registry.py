#!/usr/bin/env python3
"""
TemplateRegistry - Доска 1: Глобальный магазин шаблонных блоков
Файл skin.json описывает "как выглядит каждый виджет"
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class TemplateRegistry:
    def __init__(self, registry_path: str = "skin_system/registry"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.skin_json_path = self.registry_path / "skin.json"
        
        # Инициализация готовых виджетов для конкретных задач
        self._init_ready_widgets()
    
    def _init_ready_widgets(self):
        """Инициализация готовых виджетов для конкретных задач"""
        if not self.skin_json_path.exists():
            ready_widgets = {
                "widgets": {
                    "booking_form": {
                        "type": "form",
                        "template": "booking_form.html", 
                        "css": "booking_form.css",
                        "js": "booking_form.js",
                        "props": ["services", "time_slots", "contact_fields"],
                        "description": "Форма бронирования с выбором услуг и времени"
                    },
                    "service_card": {
                        "type": "card",
                        "template": "service_card.html",
                        "css": "service_card.css", 
                        "js": "service_card.js",
                        "props": ["name", "price", "duration", "description"],
                        "description": "Карточка услуги с ценой и описанием"
                    },
                    "time_slot_picker": {
                        "type": "picker",
                        "template": "time_slot_picker.html",
                        "css": "time_slot_picker.css",
                        "js": "time_slot_picker.js", 
                        "props": ["date", "slots", "selected_time"],
                        "description": "Выбор временного слота"
                    },
                    "product_grid": {
                        "type": "grid",
                        "template": "product_grid.html",
                        "css": "product_grid.css",
                        "js": "product_grid.js",
                        "props": ["products", "columns"],
                        "description": "Сетка товаров/услуг"
                    },
                    "contact_form": {
                        "type": "form",
                        "template": "contact_form.html",
                        "css": "contact_form.css",
                        "js": "contact_form.js",
                        "props": ["fields", "submit_text"],
                        "description": "Контактная форма"
                    },
                    "working_hours": {
                        "type": "info",
                        "template": "working_hours.html",
                        "css": "working_hours.css",
                        "js": "working_hours.js",
                        "props": ["schedule", "timezone"],
                        "description": "Отображение часов работы"
                    },
                    "header": {
                        "type": "component",
                        "template": "header.html",
                        "css": "header.css",
                        "js": "header.js",
                        "props": ["title", "subtitle", "logo"],
                        "description": "Заголовок страницы с логотипом"
                    },
                    "footer": {
                        "type": "component",
                        "template": "footer.html",
                        "css": "footer.css",
                        "js": "footer.js",
                        "props": ["company_info", "links", "social"],
                        "description": "Подвал страницы"
                    }
                },
                "layouts": {
                    "booking_page": {
                        "description": "Страница бронирования",
                        "sections": [
                            {"widget": "header", "position": "top"},
                            {"widget": "service_card", "position": "main", "repeat": "services"},
                            {"widget": "time_slot_picker", "position": "main"},
                            {"widget": "contact_form", "position": "main"},
                            {"widget": "footer", "position": "bottom"}
                        ]
                    },
                    "ecommerce_page": {
                        "description": "Страница магазина",
                        "sections": [
                            {"widget": "header", "position": "top"},
                            {"widget": "product_grid", "position": "main"},
                            {"widget": "footer", "position": "bottom"}
                        ]
                    },
                    "contact_page": {
                        "description": "Контактная страница",
                        "sections": [
                            {"widget": "header", "position": "top"},
                            {"widget": "contact_form", "position": "main"},
                            {"widget": "working_hours", "position": "sidebar"},
                            {"widget": "footer", "position": "bottom"}
                        ]
                    }
                },
                "themes": {
                    "default": {
                        "description": "Стандартная тема",
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
                    },
                    "modern": {
                        "description": "Современная тема",
                        "colors": {
                            "primary": "#6366f1",
                            "secondary": "#4f46e5",
                            "accent": "#10b981",
                            "background": "#ffffff",
                            "text": "#1f2937"
                        },
                        "fonts": {
                            "heading": "Inter, sans-serif",
                            "body": "Inter, sans-serif"
                        }
                    }
                }
            }
            
            with open(self.skin_json_path, 'w', encoding='utf-8') as f:
                json.dump(ready_widgets, f, indent=2, ensure_ascii=False)
    
    def get_widget(self, widget_name: str) -> Optional[Dict[str, Any]]:
        """Получить виджет по имени"""
        with open(self.skin_json_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        return registry.get("widgets", {}).get(widget_name)
    
    def get_layout(self, layout_name: str) -> Optional[Dict[str, Any]]:
        """Получить макет по имени"""
        with open(self.skin_json_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        return registry.get("layouts", {}).get(layout_name)
    
    def get_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Получить тему по имени"""
        with open(self.skin_json_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        return registry.get("themes", {}).get(theme_name)
    
    def list_widgets(self) -> List[str]:
        """Список доступных виджетов"""
        with open(self.skin_json_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        return list(registry.get("widgets", {}).keys())
    
    def list_layouts(self) -> List[str]:
        """Список доступных макетов"""
        with open(self.skin_json_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        return list(registry.get("layouts", {}).keys())
    
    def list_themes(self) -> List[str]:
        """Список доступных тем"""
        with open(self.skin_json_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        return list(registry.get("themes", {}).keys())
    
    def add_widget(self, name: str, widget_config: Dict[str, Any]) -> bool:
        """Добавить новый виджет в реестр"""
        try:
            with open(self.skin_json_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            registry["widgets"][name] = widget_config
            
            with open(self.skin_json_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Ошибка добавления виджета: {e}")
            return False
    
    def add_theme(self, name: str, theme_config: Dict[str, Any]) -> bool:
        """Добавить новую тему в реестр"""
        try:
            with open(self.skin_json_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            registry["themes"][name] = theme_config
            
            with open(self.skin_json_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Ошибка добавления темы: {e}")
            return False
    
    def add_layout(self, name: str, layout_config: Dict[str, Any]) -> bool:
        """Добавить новый макет в реестр"""
        try:
            with open(self.skin_json_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            registry["layouts"][name] = layout_config
            
            with open(self.skin_json_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Ошибка добавления макета: {e}")
            return False
    
    def update_widget(self, name: str, widget_config: Dict[str, Any]) -> bool:
        """Обновить существующий виджет"""
        return self.add_widget(name, widget_config)
    
    def remove_widget(self, name: str) -> bool:
        """Удалить виджет из реестра"""
        try:
            with open(self.skin_json_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            if name in registry.get("widgets", {}):
                del registry["widgets"][name]
                
                with open(self.skin_json_path, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, indent=2, ensure_ascii=False)
                
                return True
            return False
        except Exception as e:
            print(f"Ошибка удаления виджета: {e}")
            return False

# Пример использования
if __name__ == "__main__":
    registry = TemplateRegistry()
    
    print("Доступные виджеты:")
    for widget in registry.list_widgets():
        print(f"  - {widget}")
    
    print("\nДоступные макеты:")
    for layout in registry.list_layouts():
        print(f"  - {layout}")
    
    print("\nДоступные темы:")
    for theme in registry.list_themes():
        print(f"  - {theme}") 