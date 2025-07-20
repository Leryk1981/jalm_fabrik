#!/usr/bin/env python3
"""
CLI для управления Skin-As-Code системой
Команда: npm run create-skin -- client=acme color=2f7cff
"""

import argparse
import json
import sys
import re
import random
from pathlib import Path
from typing import Dict, Any, Tuple

from template_registry import TemplateRegistry
from skin_assembler import SkinAssembler
from skin_store import SkinStore

class SkinCLI:
    def __init__(self, skins_path: str = "skin_system/skins"):
        self.skins_path = skins_path
        self.registry = TemplateRegistry()
        self.assembler = SkinAssembler(skins_path)
        self.store = SkinStore(skins_path)
    
    def create_skin_command(self, client: str = None, color: str = None, layout: str = None, custom_data: Dict[str, Any] = None) -> bool:
        """
        Команда создания нового скина
        """
        try:
            if not client or not color or not layout:
                client, color, layout = self._get_interactive_input()
            
            # Валидация параметров
            if not self._validate_color(color):
                print("❌ Неверный формат цвета")
                return False
            
            if not self._validate_layout(layout):
                print("❌ Неверный макет")
                return False
            
            # Создаем скин
            args = {
                'client': client,
                'color': color,
                'layout': layout,
                'theme': 'default',
                'custom_data': custom_data
            }
            
            result = self.create_skin(args)
            return result is not None and result != False
            
        except Exception as e:
            print(f"❌ Ошибка создания скина: {e}")
            return False
    
    def list_command(self) -> bool:
        """Команда списка скинов"""
        try:
            self.list_skins({})
            return True
        except Exception as e:
            print(f"❌ Ошибка получения списка скинов: {e}")
            return False
    
    def validate_command(self, client: str = "default") -> bool:
        """Команда валидации скина"""
        try:
            validation = self.store.validate_skin(client)
            if validation['valid']:
                print("✅ Скин валиден")
            else:
                print("❌ Скин невалиден")
                print("Ошибки:", validation['errors'])
            
            if validation['warnings']:
                print("⚠️ Предупреждения:", validation['warnings'])
            
            return validation['valid']
        except Exception as e:
            print(f"❌ Ошибка валидации скина: {e}")
            return False
    
    def copy_command(self, source: str = None, target: str = None) -> bool:
        """Команда копирования скина"""
        try:
            if not source or not target:
                print("❌ Укажите source и target")
                return False
            
            result = self.store.copy_skin(source, target)
            return result
        except Exception as e:
            print(f"❌ Ошибка копирования скина: {e}")
            return False
    
    def export_command(self, client: str = None, path: str = None) -> bool:
        """Команда экспорта скина"""
        try:
            if not client:
                print("❌ Укажите имя клиента")
                return False
            
            if not path:
                path = f"{client}_skin.zip"
            
            result = self.store.export_skin(client, path)
            return result
        except Exception as e:
            print(f"❌ Ошибка экспорта скина: {e}")
            return False
    
    def delete_command(self, client: str = None) -> bool:
        """Команда удаления скина"""
        try:
            if not client:
                print("❌ Укажите имя клиента")
                return False
            
            if client == "default":
                print("❌ Нельзя удалить default скин")
                return False
            
            result = self.store.delete_skin(client)
            return result
        except Exception as e:
            print(f"❌ Ошибка удаления скина: {e}")
            return False
    
    def serve_command(self, host: str = "localhost", port: int = 8080) -> bool:
        """Команда запуска сервера"""
        try:
            import uvicorn
            from fastapi import FastAPI
            from fastapi.staticfiles import StaticFiles
            
            app = FastAPI(title="Skin-As-Code Server")
            
            # Монтируем статические файлы
            app.mount("/", StaticFiles(directory=self.skins_path, html=True), name="static")
            
            print(f"🚀 Запуск сервера на http://{host}:{port}")
            uvicorn.run(app, host=host, port=port)
            return True
        except Exception as e:
            print(f"❌ Ошибка запуска сервера: {e}")
            return False
    
    def _validate_color(self, color: str) -> bool:
        """Валидация цвета"""
        if not color:
            return False
        
        # Убираем # если есть
        color = color.lstrip('#')
        
        # Проверяем формат hex
        if len(color) != 6:
            return False
        
        try:
            int(color, 16)
            return True
        except ValueError:
            return False
    
    def _validate_layout(self, layout: str) -> bool:
        """Валидация макета"""
        valid_layouts = ["booking_page", "ecommerce_page", "contact_page", "basic", "custom_layout"]
        return layout in valid_layouts
    
    def _generate_random_color(self) -> str:
        """Генерация случайного цвета"""
        return f"#{random.randint(0, 0xFFFFFF):06x}"
    
    def _get_interactive_input(self) -> Tuple[str, str, str]:
        """Получение интерактивного ввода"""
        client = input("Введите имя клиента (или Enter для default): ").strip()
        if not client:
            client = "default"
        
        color = input("Введите цвет (hex, например 2f7cff): ").strip()
        if not color:
            color = self._generate_random_color()
        
        layout = input("Введите макет (booking_page/ecommerce_page/contact_page): ").strip()
        if not layout:
            layout = "booking_page"
        
        return client, color, layout

    def create_skin(self, args):
        """
        Создание нового скина
        npm run create-skin -- client=acme color=2f7cff
        """
        print("🎨 Создание нового скина...")
        
        # Парсим аргументы
        client_name = args.get('client', 'default')
        color = args.get('color', '2a5298')
        layout = args.get('layout', 'basic')
        theme = args.get('theme', 'default')
        custom_data = args.get('custom_data', {})
        
        print(f"📋 Параметры:")
        print(f"   - Клиент: {client_name}")
        print(f"   - Цвет: #{color}")
        print(f"   - Макет: {layout}")
        print(f"   - Тема: {theme}")
        print(f"   - Custom Data: {custom_data}")
        
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
        self.registry.add_theme(theme_name, custom_theme)
        
        # Добавляем макет в реестр если его нет
        layout_widget = {
            "description": f"Макет {layout} для {client_name}",
            "sections": [
                {"widget": "header", "position": "top"},
                {"widget": "service_card", "position": "main", "repeat": "services"},
                {"widget": "time_slot_picker", "position": "main"},
                {"widget": "contact_form", "position": "main"},
                {"widget": "footer", "position": "bottom"}
            ]
        }
        self.registry.add_layout(layout, layout_widget)
        
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
            
            .services-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            
            .products-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            
            .time-slots {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
                gap: 10px;
                margin: 20px 0;
            }}
            
            .time-slot {{
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .time-slot:hover {{
                background: #{color};
                color: white;
                border-color: #{color};
            }}
            """,
            "custom_js": f"""
            // Кастомный JavaScript для {client_name}
            console.log('{client_name} skin loaded');
            
            function selectService(serviceId) {{
                console.log('Выбрана услуга:', serviceId);
                // Логика выбора услуги
            }}
            
            function addToCart(productId) {{
                console.log('Добавлен в корзину:', productId);
                // Логика добавления в корзину
            }}
            
            // Обработчики форм
            document.addEventListener('DOMContentLoaded', function() {{
                const forms = document.querySelectorAll('form');
                forms.forEach(form => {{
                    form.addEventListener('submit', function(e) {{
                        e.preventDefault();
                        console.log('Форма отправлена для {client_name}');
                        alert('Форма отправлена!');
                    }});
                }});
            }});
            """
        }
        
        # Данные для скина
        custom_data = args.get('custom_data')
        if custom_data:
            data = custom_data
        else:
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
                "products": [
                    {"id": "product1", "name": "Товар 1", "price": 1000, "description": "Описание товара 1"},
                    {"id": "product2", "name": "Товар 2", "price": 2000, "description": "Описание товара 2"}
                ],
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
        try:
            parser = argparse.ArgumentParser(description='Skin-As-Code CLI')
            subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
            
            # Команда create-skin
            create_parser = subparsers.add_parser('create-skin', help='Создание нового скина')
            create_parser.add_argument('--client', default='default', help='Имя клиента')
            create_parser.add_argument('--color', default='2a5298', help='Основной цвет (hex)')
            create_parser.add_argument('--layout', default='basic', help='Макет')
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
                return self.create_skin_command(
                    client=args.client,
                    color=args.color,
                    layout=args.layout
                )
            elif args.command == 'list':
                return self.list_command()
            elif args.command == 'validate':
                return self.validate_command(client=args.client)
            elif args.command == 'delete':
                return self.delete_command(client=args.client)
            elif args.command == 'copy':
                return self.copy_command(source=args.source, target=args.target)
            elif args.command == 'export':
                return self.export_command(client=args.client, path=args.path)
            else:
                parser.print_help()
                return True
                
        except SystemExit:
            # Обрабатываем SystemExit от argparse
            return True
        except Exception as e:
            print(f"❌ Ошибка CLI: {e}")
            return False

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