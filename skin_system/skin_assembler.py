#!/usr/bin/env python3
"""
SkinAssembler - Доска 2: Простой bundler держит Three.js + CSS
Вход: skin.json + data.json (то, что возвращает SaaS)
Выход: index.html прямого хита без сторонних фреймворков
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from template_registry import TemplateRegistry

class SkinAssembler:
    def __init__(self, skins_path: str = "skin_system/skins"):
        self.skins_path = Path(skins_path)
        self.skins_path.mkdir(parents=True, exist_ok=True)
        self.registry = TemplateRegistry()
        
        # CDN ссылки для внешних библиотек
        self.cdn_links = {
            "three_js": "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",
            "font_awesome": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
            "google_fonts": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
        }
    
    def assemble_skin(self, client_name: str, skin_config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """
        Сборка скина из конфигурации и данных
        """
        print(f"[ASSEMBLER] Сборка скина для клиента: {client_name}")
        
        # Создаем директорию для клиента
        client_dir = self.skins_path / client_name
        client_dir.mkdir(exist_ok=True)
        
        # Получаем конфигурацию скина
        layout_name = skin_config.get("layout", "basic")
        theme_name = skin_config.get("theme", "default")
        custom_css = skin_config.get("custom_css", "")
        custom_js = skin_config.get("custom_js", "")
        
        # Получаем макет и тему из реестра
        layout = self.registry.get_layout(layout_name)
        theme = self.registry.get_theme(theme_name)
        
        if not layout:
            print(f"[ERROR] Макет {layout_name} не найден в реестре")
            return None
        
        if not theme:
            print(f"[ERROR] Тема {theme_name} не найдена в реестре")
            return None
        
        # Генерируем HTML
        html_content = self._generate_html(client_name, layout, theme, data, custom_css, custom_js)
        
        # Сохраняем файлы
        index_path = client_dir / "index.html"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Создаем skin.json для клиента
        skin_json_path = client_dir / "skin.json"
        with open(skin_json_path, 'w', encoding='utf-8') as f:
            json.dump(skin_config, f, indent=2, ensure_ascii=False)
        
        # Создаем data.json для клиента
        data_json_path = client_dir / "data.json"
        with open(data_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Скин собран: {index_path}")
        return str(client_dir)
    
    def _generate_html(self, client_name: str, layout: Dict[str, Any], theme: Dict[str, Any], 
                      data: Dict[str, Any], custom_css: str, custom_js: str) -> str:
        """Генерация HTML с Three.js и CSS"""
        
        # Подготавливаем данные для виджетов
        widget_data = self._prepare_widget_data(data)
        
        # Генерируем CSS
        css_content = self._generate_css(theme, custom_css)
        
        # Генерируем JavaScript
        js_content = self._generate_js(widget_data, custom_js)
        
        # Генерируем HTML структуру
        html_structure = self._generate_html_structure(client_name, layout, widget_data)
        
        # Собираем финальный HTML
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{client_name.title()} - JALM Skin</title>
    
    <!-- CDN библиотеки -->
    <link rel="stylesheet" href="{self.cdn_links['font_awesome']}">
    <link rel="stylesheet" href="{self.cdn_links['google_fonts']}">
    
    <!-- Three.js -->
    <script src="{self.cdn_links['three_js']}"></script>
    
    <!-- Стили -->
    <style>
        {css_content}
    </style>
</head>
<body>
    {html_structure}
    
    <!-- JavaScript -->
    <script>
        {js_content}
    </script>
</body>
</html>"""
        
        return html
    
    def _prepare_widget_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Подготовка данных для виджетов"""
        widget_data = {
            "app_name": data.get("app_name", "JALM App"),
            "api_url": data.get("api_url", "http://localhost:8080")
        }
        
        # Добавляем данные для конкретных виджетов
        if "services" in data:
            widget_data["services"] = data["services"]
        
        if "working_hours" in data:
            widget_data["working_hours"] = data["working_hours"]
        
        if "contact_info" in data:
            widget_data["contact_info"] = data["contact_info"]
        
        if "products" in data:
            widget_data["products"] = data["products"]
        
        return widget_data
    
    def _generate_css(self, theme: Dict[str, Any], custom_css: str) -> str:
        """Генерация CSS с темой"""
        colors = theme.get("colors", {})
        fonts = theme.get("fonts", {})
        
        css = f"""
        /* Основные стили */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {fonts.get('body', 'Segoe UI, sans-serif')};
            background: {colors.get('background', '#f5f5f5')};
            color: {colors.get('text', '#333333')};
            line-height: 1.6;
        }}
        
        /* Контейнеры */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Текст */
        h1, h2, h3, h4, h5, h6 {{
            font-family: {fonts.get('heading', 'Segoe UI, sans-serif')};
            color: {colors.get('primary', '#2a5298')};
            margin-bottom: 1rem;
        }}
        
        /* Кнопки */
        .btn {{
            background: {colors.get('primary', '#2a5298')};
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .btn:hover {{
            background: {colors.get('secondary', '#1e3c72')};
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        /* Формы */
        .form-group {{
            margin-bottom: 20px;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        .form-group input,
        .form-group select,
        .form-group textarea {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }}
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: {colors.get('primary', '#2a5298')};
        }}
        
        /* Списки */
        .list {{
            list-style: none;
            padding: 0;
        }}
        
        .list li {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        
        /* Адаптивность */
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
        }}
        
        /* Пользовательские стили */
        {custom_css}
        """
        
        return css
    
    def _generate_js(self, widget_data: Dict[str, Any], custom_js: str) -> str:
        """Генерация JavaScript с Three.js"""
        js = f"""
        // Конфигурация приложения
        const appConfig = {json.dumps(widget_data, ensure_ascii=False)};
        
        // Инициализация Three.js сцены
        let scene, camera, renderer;
        
        function initThreeJS() {{
            // Создание сцены
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0xf5f5f5);
            
            // Создание камеры
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 5;
            
            // Создание рендерера
            renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            
            // Добавление рендерера в DOM
            const threeContainer = document.getElementById('three-container');
            if (threeContainer) {{
                threeContainer.appendChild(renderer.domElement);
            }}
            
            // Создание геометрии
            const geometry = new THREE.BoxGeometry();
            const material = new THREE.MeshBasicMaterial({{ color: 0x2a5298 }});
            const cube = new THREE.Mesh(geometry, material);
            scene.add(cube);
            
            // Анимация
            function animate() {{
                requestAnimationFrame(animate);
                cube.rotation.x += 0.01;
                cube.rotation.y += 0.01;
                renderer.render(scene, camera);
            }}
            animate();
        }}
        
        // Инициализация при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('[SKIN] Приложение загружено:', appConfig.app_name);
            
            // Инициализация Three.js
            if (typeof THREE !== 'undefined') {{
                initThreeJS();
            }}
        }});
        
        // Обработка изменения размера окна
        window.addEventListener('resize', function() {{
            if (camera && renderer) {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }}
        }});
        
        // Пользовательский JavaScript
        {custom_js}
        """
        
        return js
    
    def _generate_html_structure(self, client_name: str, layout: Dict[str, Any], widget_data: Dict[str, Any]) -> str:
        """Генерация HTML структуры на основе макета"""
        sections = layout.get("sections", [])
        
        html_parts = []
        
        for section in sections:
            widget_name = section.get("widget")
            position = section.get("position", "main")
            
            if not widget_name:
                continue
            
            widget_html = self._generate_widget_html(widget_name, widget_data)
            
            if position == "top":
                html_parts.append(f'<header class="header-section">{widget_html}</header>')
            elif position == "bottom":
                html_parts.append(f'<footer class="footer-section">{widget_html}</footer>')
            elif position == "sidebar":
                html_parts.append(f'<aside class="sidebar-section">{widget_html}</aside>')
            else:
                html_parts.append(f'<main class="main-section">{widget_html}</main>')
        
        # Добавляем Three.js контейнер
        html_parts.append('<div id="three-container" style="position: fixed; top: 0; left: 0; z-index: -1;"></div>')
        
        return '\n'.join(html_parts)
    
    def _generate_widget_html(self, widget_name: str, data: Dict[str, Any], repeat: Optional[str] = None) -> str:
        """Генерация HTML для конкретного виджета"""
        
        if widget_name == "header":
            return f"""
            <div class="header">
                <h1><i class="fas fa-rocket"></i> {data.get('app_name', 'JALM App')}</h1>
                <p>Современное веб-приложение на базе JALM Full Stack</p>
            </div>
            """
        
        elif widget_name == "booking_form":
            services = data.get("services", [])
            services_html = ""
            for service in services:
                services_html += f"""
                <div class="form-group">
                    <label>
                        <input type="radio" name="service" value="{service['id']}">
                        {service['name']} - {service['price']} ₽ ({service['duration']} мин)
                    </label>
                </div>
                """
            
            return f"""
            <div class="booking-form">
                <h2><i class="fas fa-calendar-alt"></i> Забронировать услугу</h2>
                <form>
                    <div class="form-group">
                        <label>Выберите услугу:</label>
                        {services_html}
                    </div>
                    <div class="form-group">
                        <label for="date">Дата:</label>
                        <input type="date" id="date" name="date" required>
                    </div>
                    <div class="form-group">
                        <label for="time">Время:</label>
                        <input type="time" id="time" name="time" required>
                    </div>
                    <div class="form-group">
                        <label for="name">Имя:</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="phone">Телефон:</label>
                        <input type="tel" id="phone" name="phone" required>
                    </div>
                    <button type="submit" class="btn">
                        <i class="fas fa-check"></i> Забронировать
                    </button>
                </form>
            </div>
            """
        
        elif widget_name == "service_card":
            services = data.get("services", [])
            if repeat == "services":
                cards_html = ""
                for service in services:
                    cards_html += f"""
                    <div class="service-card">
                        <h3><i class="fas fa-star"></i> {service['name']}</h3>
                        <p class="price">{service['price']} ₽</p>
                        <p class="duration">{service['duration']} минут</p>
                        <button class="btn" onclick="selectService('{service['id']}')">
                            <i class="fas fa-plus"></i> Выбрать
                        </button>
                    </div>
                    """
                return f'<div class="services-grid">{cards_html}</div>'
            else:
                service = services[0] if services else {"name": "Услуга", "price": 1000, "duration": 60}
                return f"""
                <div class="service-card">
                    <h3><i class="fas fa-star"></i> {service['name']}</h3>
                    <p class="price">{service['price']} ₽</p>
                    <p class="duration">{service['duration']} минут</p>
                </div>
                """
        
        elif widget_name == "time_slot_picker":
            return f"""
            <div class="time-slot-picker">
                <h2>Выберите время</h2>
                <div class="form-group">
                    <label for="date">Дата:</label>
                    <input type="date" id="date" name="date" required>
                </div>
                <div class="time-slots">
                    <div class="time-slot">09:00</div>
                    <div class="time-slot">10:00</div>
                    <div class="time-slot">11:00</div>
                    <div class="time-slot">12:00</div>
                    <div class="time-slot">13:00</div>
                    <div class="time-slot">14:00</div>
                </div>
            </div>
            """
        
        elif widget_name == "product_grid":
            products = data.get("products", [])
            products_html = ""
            for product in products:
                products_html += f"""
                <div class="product-card">
                    <h3>{product['name']}</h3>
                    <p class="price">{product['price']} ₽</p>
                    <p>{product.get('description', '')}</p>
                    <button class="btn" onclick="addToCart('{product['id']}')">
                        <i class="fas fa-shopping-cart"></i> В корзину
                    </button>
                </div>
                """
            return f'<div class="products-grid">{products_html}</div>'
        
        elif widget_name == "contact_form":
            return f"""
            <div class="contact-form">
                <h2><i class="fas fa-envelope"></i> Свяжитесь с нами</h2>
                <form>
                    <div class="form-group">
                        <label for="name">Имя:</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="message">Сообщение:</label>
                        <textarea id="message" name="message" rows="5" required></textarea>
                    </div>
                    <button type="submit" class="btn">
                        <i class="fas fa-paper-plane"></i> Отправить
                    </button>
                </form>
            </div>
            """
        
        elif widget_name == "working_hours":
            hours = data.get("working_hours", {})
            hours_html = ""
            for day, time in hours.items():
                hours_html += f"""
                <div class="working-day">
                    <strong>{day}:</strong> {time['start']} - {time['end']}
                </div>
                """
            
            return f"""
            <div class="working-hours">
                <h3><i class="fas fa-clock"></i> Часы работы</h3>
                {hours_html}
            </div>
            """
        
        elif widget_name == "footer":
            contact_info = data.get("contact_info", {})
            return f"""
            <div class="footer">
                <p>&copy; 2024 {data.get('app_name', 'JALM App')}. Все права защищены.</p>
                <p>Телефон: {contact_info.get('phone', '+7 (999) 123-45-67')}</p>
                <p>Email: {contact_info.get('email', 'info@example.com')}</p>
            </div>
            """
        
        else:
            # Fallback для неизвестных виджетов
            return f"""
            <div class="widget-fallback">
                <h3>Виджет: {widget_name}</h3>
                <p>Данные: {json.dumps(data, ensure_ascii=False)}</p>
            </div>
            """

# Пример использования
if __name__ == "__main__":
    assembler = SkinAssembler()
    
    # Пример данных
    test_data = {
        "app_name": "Тестовое приложение",
        "content": "Это тестовое содержимое",
        "api_url": "http://localhost:8080"
    }
    
    # Конфигурация скина
    skin_config = {
        "layout": "basic",
        "theme": "default",
        "custom_css": "",
        "custom_js": ""
    }
    
    # Сборка скина
    result = assembler.assemble_skin("test_client", skin_config, test_data)
    print(f"Результат: {result}") 