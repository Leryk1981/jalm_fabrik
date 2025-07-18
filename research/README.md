# 🔍 Research Layer

Модуль для сбора и анализа данных в JALM Full Stack. Собирает паттерны использования для создания чистых клиентских контейнеров.

## 📋 Описание

Research Layer отвечает за:
- **Сбор данных** из различных источников (GitHub, StackOverflow, NPM, PyPI, Docker Hub)
- **Анализ паттернов** использования технологий
- **Группировку** по категориям приложений
- **Экспорт** в форматы для интеграции с JALM-стеком

## 🏗️ Архитектура

```
research/
├── __init__.py          # Основной модуль
├── config.py           # Конфигурация
├── collector.py        # Сборщик данных
├── analyzer.py         # Анализатор паттернов
├── patterns/           # Файлы данных
│   ├── raw_actions.csv
│   ├── raw_patterns.csv
│   ├── grouped.json
│   └── template_groups.json
├── tests/              # Тесты
├── requirements.txt    # Зависимости
└── README.md          # Документация
```

## 🚀 Использование

### Базовое использование

```python
from research import DataCollector, PatternAnalyzer, ResearchConfig

# Создание конфигурации
config = ResearchConfig()

# Сбор данных
collector = DataCollector(config)
actions = collector.collect_actions()
patterns = collector.collect_patterns()

# Анализ паттернов
analyzer = PatternAnalyzer(config)
analysis = analyzer.analyze_patterns(patterns)
groups = analyzer.group_patterns(patterns)

# Экспорт результатов
collector.export(actions, "csv", "raw_actions.csv")
analyzer.export_groups(groups, "json", "pattern_groups.json")
```

### Создание артефактов для JALM

```python
# Создание всех артефактов для интеграции
artifacts = analyzer.create_jalm_artifacts(patterns)
print("Созданные артефакты:", artifacts)
```

## 📊 Источники данных

### Поддерживаемые источники:
- **GitHub API** - анализ репозиториев
- **StackOverflow API** - вопросы и ответы
- **NPM Registry** - пакеты JavaScript
- **PyPI** - пакеты Python
- **Docker Hub** - образы контейнеров

### Типы собираемых данных:
- **SPA приложения** (React, Vue, Angular)
- **SSR приложения** (Next.js, Nuxt.js)
- **API сервисы** (FastAPI, Flask, Django)
- **Микросервисы** (Go, Node.js)

## 🎯 Паттерны для JALM

### Категории паттернов:
- **booking_systems** - системы бронирования
- **ecommerce** - электронная коммерция
- **notification_services** - сервисы уведомлений
- **auth_systems** - системы аутентификации
- **api_gateways** - API шлюзы
- **data_processing** - обработка данных
- **file_management** - управление файлами
- **reporting** - отчетность

### Структура паттерна:
```json
{
  "pattern_name": "booking_light",
  "components": ["frontend", "api", "database"],
  "env_vars": ["DB_URL", "API_KEY"],
  "config_structure": {
    "frontend": {"build": "dist"},
    "api": {"port": 8080}
  },
  "frequency": 45,
  "app_type": "spa"
}
```

## 🔧 Конфигурация

### Основные параметры:
```python
config = ResearchConfig(
    min_pattern_frequency=3,      # Минимальная частота паттерна
    max_pattern_length=10,        # Максимальная длина паттерна
    similarity_threshold=0.8,     # Порог схожести
    data_sources=[               # Источники данных
        "github_api",
        "stackoverflow_api",
        "npm_registry",
        "pypi_registry",
        "docker_hub"
    ]
)
```

## 📈 Интеграция с JALM

### Создаваемые артефакты:
1. **pattern_analysis.json** - анализ паттернов
2. **pattern_groups.json** - группировка по категориям
3. **jalm_templates.json** - шаблоны для Shablon Spec
4. **jalm_functions.json** - функции для Tula Registry

### Автоматическая интеграция:
- Экспорт в Tool Catalog
- Создание шаблонов для Provision
- Генерация функций для Registry

## 🧪 Тестирование

```bash
# Запуск тестов
python -m pytest research/tests/

# Тестирование сбора данных
python -c "
from research import DataCollector
collector = DataCollector()
actions = collector.collect_actions()
print(f'Собрано {len(actions)} действий')
"
```

## 📝 Логирование

Модуль использует стандартное логирование Python:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🔒 Безопасность

- Rate limiting для API запросов
- Обработка ошибок и исключений
- Валидация входных данных
- Безопасное хранение конфигурации

## 🚀 Разработка

### Добавление нового источника данных:
1. Создать метод `_collect_from_<source>()` в `DataCollector`
2. Добавить источник в `config.data_sources`
3. Добавить обработку в `collect_actions()`

### Добавление нового типа паттерна:
1. Создать метод `_extract_<type>_patterns()` в `DataCollector`
2. Добавить тип в `collect_patterns()`
3. Обновить `_determine_pattern_group()` в `PatternAnalyzer`

## 📞 Поддержка

Для вопросов и предложений обращайтесь к команде JALM Full Stack.

---

**Версия:** 1.0.0  
**Дата:** 2024-07-18  
**Статус:** ✅ Готов к использованию 