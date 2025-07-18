# JALM Full Stack - SaaS Constructor

Полноценная экосистема для no-code/low-code создания SaaS-приложений с автоматической генерацией JALM-конфигов и деплоем через Docker.

## 🏗️ Архитектура

### Основные компоненты:
- **JALM Full Stack** - 6-слойная архитектура для SaaS-сборки
- **Core Spec** - исполнительное ядро для запуска tula и шаблонов  
- **Tula Spec** - каталог готовых функций (Google Calendar, SMS, Firebase Auth)
- **Shablon Spec** - каталог готовых шаблонов (booking widget, payment modal)

### Текущая реализация:
- **FastAPI-приложение** с генерацией JALM через LLM (OpenRouter)
- **Web-интерфейс** для создания и деплоя SaaS-инстансов
- **Docker-оркестрация** через шаблоны Dockerfile и docker-compose
- **Логирование** всех операций

## 🚀 Быстрый старт

### Предварительные требования:
- Python 3.8+
- Docker и Docker Compose
- OpenRouter API ключ

### Установка:
```bash
# Клонирование репозитория
git clone <repository-url>
cd Saas

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env, добавив ваш OPENROUTER_API_KEY
```

### Запуск:
```bash
# Запуск FastAPI-приложения
uvicorn api:app --reload

# Откройте http://localhost:8000 в браузере
```

## 📋 Использование

### 1. Генерация JALM-конфига
- Опишите нужный SaaS в текстовом поле
- Нажмите "Сгенерировать JALM"
- Система создаст YAML-конфиг через LLM

### 2. Деплой SaaS
- Просмотрите и при необходимости отредактируйте JALM-конфиг
- Нажмите "Развернуть SaaS"
- Система создаст Docker-контейнер и вернёт URL

### 3. API endpoints
- `POST /generate` - генерация JALM через LLM
- `POST /deploy` - деплой SaaS-инстанса
- `POST /provision` - прямой деплой JALM-файла

## 🏛️ Структура проекта

```
Saas/
├── api.py                    # FastAPI-приложение
├── saas_provisioner.py       # Оркестратор деплоя
├── config.jalm              # Пример JALM-конфига
├── Dockerfile.template       # Шаблон Dockerfile
├── docker-compose.template.yml # Шаблон docker-compose
├── templates/
│   └── main.html            # Web-интерфейс
├── toolifier/               # Основа для сбора шаблонов и tula
├── jalm_full_stack          # Спецификация полного стека
├── core_spec                # Спецификация исполнительного ядра
├── tula_spec                # Спецификация каталога tula
├── shablon_spec             # Спецификация каталога шаблонов
├── requirements.txt         # Python-зависимости
├── .env                     # Переменные окружения
├── .gitignore              # Git-исключения
└── .dockerignore           # Docker-исключения
```

## 🔧 Конфигурация

### Переменные окружения (.env):
```env
OPENROUTER_API_KEY=your_openrouter_api_key
```

### JALM-конфиг (config.jalm):
```yaml
intent: calendar_booking
steps:
  - call_tool: create_calendar
    args:
      name: "My Calendar"
context:
  calendars: 1
  lang: "ru"
  domain: "demo.mycalendar.app"
meta:
  stream: false
  retry_on_fail: 1
```

## 🎯 Roadmap

### Текущие возможности:
- ✅ Генерация JALM через LLM
- ✅ Деплой через Docker
- ✅ Web-интерфейс
- ✅ Логирование операций

### Планируемые улучшения:
- 🔄 Интеграция с каталогом tula (Tula Spec)
- 🔄 Интеграция с каталогом шаблонов (Shablon Spec)
- 🔄 Исполнительное ядро (Core Spec)
- 🔄 Registry для готовых компонентов
- 🔄 CLI для быстрого деплоя

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License

## 🔗 Ссылки

- [JALM Full Stack спецификация](jalm_full_stack)
- [Core Spec](core_spec)
- [Tula Spec](tula_spec)
- [Shablon Spec](shablon_spec) 