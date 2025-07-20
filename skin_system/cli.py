#!/usr/bin/env python3
"""
CLI для управления Skin-As-Code системой
Команда: npm run create-skin -- client=acme color=2f7cff
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from template_registry import TemplateRegistry
from skin_assembler import SkinAssembler
from skin_store import SkinStore

class SkinCLI:
    def __init__(self):
        self.registry = TemplateRegistry()
        self.assembler = SkinAssembler()
        self.store = SkinStore()
    
    def create_skin(self, args):
        """
        Создание нового скина
        npm run create-skin -- client=acme color=2f7cff
        """
        print("🎨 Создание нового скина...")
        
        # Парсим аргументы
        client_name = args.get('client', 'default')
        color = args.get('color', '2a5298')
        layout = args.get('layout', 'booking_page')
        theme = args.get('theme', 'default')
        
        print(f"📋 Параметры:")
        print(f"   - Клиент: {client_name}")
        print(f"   - Цвет: #{color}")
        print(f"   - Макет: {layout}")
        print(f"   - Тема: {theme}")
        
        # Создаем кастомную тему с указанным цветом
        custom_theme = {
            "description": f"Кастомная тема для {client_name}",
            "colors": {
                "primary": f"#{color}",
                "secondary": self._adjust_color(color, -20),
                "accent": "#28a745",
                "background": "#f5f5f5",
                "text": "#333333"
            },
            "fonts": {
                "heading": "Inter, sans-serif",
                "body": "Inter, sans-serif"
            }
        }
        
        # Добавляем тему в реестр
        theme_name = f"{client_name}_theme"
        self.registry.add_widget(theme_name, custom_theme)
        
        # Конфигурация скина
        skin_config = {
            "name": f"{client_name.title()} Skin",
            "description": f"Кастомный скин для {client_name}",
            "layout": layout,
            "theme": theme_name,
            "version": "1.0.0",
            "author": "Skin CLI",
            "custom_css": f"""
            /* Кастомные стили для {client_name} */
            .btn {{
                background: #{color} !important;
            }}
            .btn:hover {{
                background: {self._adjust_color(color, -20)} !important;
            }}
            """,
            "custom_js": f"""
            // Кастомный JavaScript для {client_name}
            console.log('{client_name} skin loaded');
            """
        }
        
        # Данные для скина
        data = {
            "app_name": f"{client_name.title()} Application",
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
                "email": f"info@{client_name}.com",
                "address": f"ул. {client_name.title()}, 1"
            },
            "api_url": "http://localhost:8080"
        }
        
        # Создаем скин
        skin_path = self.store.create_skin(client_name, skin_config, data)
        
        print(f"✅ Скин создан: {skin_path}")
        print(f"🌐 URL: {self.store.get_skin_url(client_name)}")
        
        return skin_path
    
    def list_skins(self, args):
        """Список всех скинов"""
        skins = self.store.list_skins()
        
        print("📚 Доступные скины:")
        for skin in skins:
            print(f"   - {skin['name']}")
            print(f"     Путь: {skin['path']}")
            print(f"     Хеш: {skin['metadata'].get('skin_hash', 'unknown')}")
            print()
    
    def validate_skin(self, args):
        """Валидация скина"""
        client_name = args.get('client', 'default')
        
        print(f"🔍 Валидация скина: {client_name}")
        validation = self.store.validate_skin(client_name)
        
        if validation['valid']:
            print("✅ Скин валиден")
        else:
            print("❌ Скин невалиден")
            print("Ошибки:", validation['errors'])
        
        if validation['warnings']:
            print("⚠️ Предупреждения:", validation['warnings'])
    
    def delete_skin(self, args):
        """Удаление скина"""
        client_name = args.get('client')
        
        if not client_name:
            print("❌ Укажите имя клиента: --client=name")
            return
        
        print(f"🗑️ Удаление скина: {client_name}")
        
        if self.store.delete_skin(client_name):
            print("✅ Скин удален")
        else:
            print("❌ Ошибка удаления скина")
    
    def copy_skin(self, args):
        """Копирование скина"""
        source = args.get('source')
        target = args.get('target')
        
        if not source or not target:
            print("❌ Укажите source и target: --source=name --target=name")
            return
        
        print(f"📋 Копирование скина: {source} → {target}")
        
        if self.store.copy_skin(source, target):
            print("✅ Скин скопирован")
        else:
            print("❌ Ошибка копирования скина")
    
    def export_skin(self, args):
        """Экспорт скина"""
        client_name = args.get('client')
        export_path = args.get('path', f"{client_name}_skin.zip")
        
        if not client_name:
            print("❌ Укажите имя клиента: --client=name")
            return
        
        print(f"📦 Экспорт скина: {client_name} → {export_path}")
        
        if self.store.export_skin(client_name, export_path):
            print("✅ Скин экспортирован")
        else:
            print("❌ Ошибка экспорта скина")
    
    def _adjust_color(self, color: str, adjustment: int) -> str:
        """Корректировка цвета"""
        # Простая корректировка яркости
        try:
            r = int(color[:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            r = max(0, min(255, r + adjustment))
            g = max(0, min(255, g + adjustment))
            b = max(0, min(255, b + adjustment))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return f"#{color}"
    
    def run(self):
        """Основной метод CLI"""
        parser = argparse.ArgumentParser(description='Skin-As-Code CLI')
        subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
        
        # Команда create-skin
        create_parser = subparsers.add_parser('create-skin', help='Создание нового скина')
        create_parser.add_argument('--client', default='default', help='Имя клиента')
        create_parser.add_argument('--color', default='2a5298', help='Основной цвет (hex)')
        create_parser.add_argument('--layout', default='booking_page', help='Макет')
        create_parser.add_argument('--theme', default='default', help='Тема')
        
        # Команда list
        list_parser = subparsers.add_parser('list', help='Список скинов')
        
        # Команда validate
        validate_parser = subparsers.add_parser('validate', help='Валидация скина')
        validate_parser.add_argument('--client', default='default', help='Имя клиента')
        
        # Команда delete
        delete_parser = subparsers.add_parser('delete', help='Удаление скина')
        delete_parser.add_argument('--client', required=True, help='Имя клиента')
        
        # Команда copy
        copy_parser = subparsers.add_parser('copy', help='Копирование скина')
        copy_parser.add_argument('--source', required=True, help='Исходный клиент')
        copy_parser.add_argument('--target', required=True, help='Целевой клиент')
        
        # Команда export
        export_parser = subparsers.add_parser('export', help='Экспорт скина')
        export_parser.add_argument('--client', required=True, help='Имя клиента')
        export_parser.add_argument('--path', help='Путь для экспорта')
        
        args = parser.parse_args()
        
        if args.command == 'create-skin':
            self.create_skin(vars(args))
        elif args.command == 'list':
            self.list_skins(vars(args))
        elif args.command == 'validate':
            self.validate_skin(vars(args))
        elif args.command == 'delete':
            self.delete_skin(vars(args))
        elif args.command == 'copy':
            self.copy_skin(vars(args))
        elif args.command == 'export':
            self.export_skin(vars(args))
        else:
            parser.print_help()

# Создание package.json для npm команд
def create_package_json():
    """Создание package.json с npm командами"""
    package_json = {
        "name": "skin-system",
        "version": "1.0.0",
        "description": "Skin-As-Code система для JALM Full Stack",
        "main": "cli.py",
        "scripts": {
            "create-skin": "python skin_system/cli.py create-skin",
            "list-skins": "python skin_system/cli.py list",
            "validate-skin": "python skin_system/cli.py validate",
            "delete-skin": "python skin_system/cli.py delete",
            "copy-skin": "python skin_system/cli.py copy",
            "export-skin": "python skin_system/cli.py export"
        },
        "keywords": ["skin", "ui", "jalm", "template"],
        "author": "JALM Foundation",
        "license": "MIT"
    }
    
    with open("package.json", 'w', encoding='utf-8') as f:
        json.dump(package_json, f, indent=2)

if __name__ == "__main__":
    # Создаем package.json если его нет
    if not Path("package.json").exists():
        create_package_json()
    
    cli = SkinCLI()
    cli.run() 