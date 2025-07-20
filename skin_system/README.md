# Skin-As-Code система

**Skin-As-Code** - это система для создания пользовательских интерфейсов в JALM Full Stack архитектуре.

## Архитектура "Три доски"

### Доска 1: TemplateRegistry
Глобальный магазин шаблонных блоков
- Файл `skin.json` описывает "как выглядит каждый виджет"
- Это не пользователи, а китаец, который присылает pull-request: "один типовой блок — один объект"

### Доска 2: SkinAssembler  
Простой bundler держит Three.js + CSS
- Вход: `skin.json` + `data.json` (то, что возвращает SaaS)
- Выход: `index.html` прямого хита без сторонних фреймворков

### Доска 3: SkinStore
Git-репозиторий `skins/`
- Папка "default" всегда обязательна: если клиент не завёл ничего, берём её как fallback
- Каждая папка = новая *leather*. Делаете директорию → заливаете → включается автоматически через хеш

## Быстрый старт

### Создание скина за 3 минуты:

```bash
npm run create-skin -- client=acme color=2f7cff
```

→ генерируются:
- `acme/skin.json`
- `acme/index.html` (подключённый к CDN версии `core.js`)

Подняли на `/skins/acme/` — визуалка жива/работает, без редактирования кора ядра SaaS.

## Команды CLI

```bash
# Создание скина
npm run create-skin -- client=acme color=2f7cff layout=booking_page

# Список скинов
npm run list-skins

# Валидация скина
npm run validate-skin -- client=acme

# Копирование скина
npm run copy-skin -- source=acme target=beta

# Экспорт скина
npm run export-skin -- client=acme --path=acme_skin.zip

# Удаление скина
npm run delete-skin -- client=acme
```

## Структура скина

```
skins/
├── default/           # Fallback скин
│   ├── index.html
│   ├── skin.json
│   ├── data.json
│   └── metadata.json
├── acme/              # Скин клиента ACME
│   ├── index.html
│   ├── skin.json
│   ├── data.json
│   └── metadata.json
└── beta/              # Скин клиента BETA
    ├── index.html
    ├── skin.json
    ├── data.json
    └── metadata.json
```

## Доступные виджеты

- `header` - Заголовок страницы с логотипом
- `booking_form` - Форма бронирования
- `service_card` - Карточка услуги
- `time_slot_picker` - Выбор временного слота
- `contact_form` - Контактная форма
- `status_message` - Сообщение о статусе
- `working_hours` - Часы работы
- `product_grid` - Сетка товаров
- `navigation` - Навигационное меню
- `footer` - Подвал страницы

## Доступные макеты

- `booking_page` - Страница бронирования
- `ecommerce_page` - Страница магазина
- `contact_page` - Контактная страница

## Доступные темы

- `default` - Стандартная тема
- `modern` - Современная тема
- `classic` - Классическая тема

## Преимущества подхода

• Делает нас не хостером — поставщиком пустого мультибрендового короба
• Отпадает задача "рисовать UI в админке"; клиент делает сам или отдаёт дизайнеру файл-артефакт
• Разделение ответственности: скелет (логика) + шкура (UI)
• Гибкая система скинов с возможностью кастомизации
• Автоматическая сборка из компонентов
• Мультибрендовость - каждый клиент может иметь свой скин

## Интеграция с JALM Full Stack

Skin-As-Code система интегрируется с существующей архитектурой JALM:

1. **SaasProvisioner** создает минимальный клиентский продукт
2. **SkinAssembler** генерирует UI на основе provision.yaml
3. **SkinStore** хранит и управляет скинами
4. **TemplateRegistry** предоставляет виджеты и макеты

## Разработка

### Добавление нового виджета

```python
from skin_system import TemplateRegistry

registry = TemplateRegistry()
registry.add_widget("my_widget", {
    "type": "component",
    "template": "my_widget.html",
    "css": "my_widget.css", 
    "js": "my_widget.js",
    "props": ["title", "content"],
    "description": "Мой новый виджет"
})
```

### Создание кастомного макета

```python
registry.add_layout("my_layout", {
    "description": "Мой кастомный макет",
    "sections": [
        {"widget": "header", "position": "top"},
        {"widget": "my_widget", "position": "main"},
        {"widget": "footer", "position": "bottom"}
    ]
})
```

## Лицензия

MIT License 