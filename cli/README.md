# JALM CLI 🚀

Командная строка для управления JALM Full Stack экосистемой.

## 📋 Описание

JALM CLI предоставляет удобный интерфейс для управления всеми компонентами JALM Full Stack:

- **Core Runner** - исполнительное ядро
- **Tula Spec** - каталог функций  
- **Shablon Spec** - каталог шаблонов
- **SaaS Provisioner** - автоматическое создание продуктов

## 🚀 Установка

### Из исходного кода

```bash
# Клонируем репозиторий
git clone https://github.com/jalm-foundation/jalm-full-stack.git
cd jalm-full-stack

# Устанавливаем CLI
cd cli
pip install -e .
```

### Проверка установки

```bash
jalm --version
```

## 📖 Использование

### Основные команды

```bash
# Управление сервисами
jalm up core-runner          # Запуск core-runner
jalm up all                  # Запуск всех сервисов
jalm down tula-spec          # Остановка tula-spec
jalm down all                # Остановка всех сервисов

# Мониторинг
jalm status                  # Статус всех сервисов
jalm status --verbose        # Подробный статус
jalm logs core-runner        # Логи core-runner
jalm logs all --follow       # Следование за логами всех сервисов

# Тестирование
jalm test                    # Запуск всех тестов
jalm test shablon-spec --verbose  # Тесты shablon-spec с подробным выводом

# Деплой
jalm deploy booking_light    # Деплой шаблона booking_light
jalm deploy ecommerce --name my-shop  # Деплой с именем
```

### Опции команд

#### `jalm up`
- `--detach, -d` - запуск в фоновом режиме
- `service` - сервис для запуска (all, core-runner, tula-spec, shablon-spec)

#### `jalm down`
- `service` - сервис для остановки (all, core-runner, tula-spec, shablon-spec)

#### `jalm status`
- `--verbose, -v` - подробный вывод

#### `jalm logs`
- `--follow, -f` - следование за логами
- `--lines, -n` - количество строк (по умолчанию 50)
- `service` - сервис для просмотра логов

#### `jalm test`
- `--verbose, -v` - подробный вывод
- `service` - сервис для тестирования

#### `jalm deploy`
- `--name, -n` - имя деплоя
- `--config, -c` - путь к конфигурации
- `template` - название шаблона

### Глобальные опции

- `--version` - версия CLI
- `--debug` - режим отладки
- `--config-file` - путь к файлу конфигурации

## ⚙️ Конфигурация

CLI использует конфигурационный файл `~/.jalm/config.json`:

```json
{
  "services": {
    "core-runner": {
      "port": 8000,
      "path": "./core-runner",
      "docker_image": "jalm/core-runner:latest"
    },
    "tula-spec": {
      "port": 8001,
      "path": "./tula_spec",
      "docker_image": "jalm/tula-spec:latest"
    },
    "shablon-spec": {
      "port": 8002,
      "path": "./shablon_spec",
      "docker_image": "jalm/shablon-spec:latest"
    }
  },
  "docker": {
    "compose_file": "./docker/docker-compose.yml",
    "network": "jalm-network"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

## 🔧 Разработка

### Структура проекта

```
cli/
├── __init__.py
├── main.py                 # Главный модуль CLI
├── setup.py               # Установка
├── requirements.txt       # Зависимости
├── README.md             # Документация
├── commands/             # Команды
│   ├── __init__.py
│   ├── up.py            # jalm up
│   ├── down.py          # jalm down
│   ├── status.py        # jalm status
│   ├── logs.py          # jalm logs
│   ├── test.py          # jalm test
│   └── deploy.py        # jalm deploy
├── core/                 # Основные компоненты
│   ├── __init__.py
│   ├── config.py        # Конфигурация
│   ├── docker.py        # Docker управление
│   └── api.py           # API клиенты
└── utils/               # Утилиты
    ├── __init__.py
    ├── logger.py        # Логирование
    └── helpers.py       # Вспомогательные функции
```

### Добавление новой команды

1. Создайте файл в `commands/`
2. Реализуйте функцию `run()`
3. Добавьте команду в `main.py`

Пример:

```python
# commands/example.py
def run(arg1, arg2, config, logger):
    """Описание команды"""
    logger.info(f"Выполнение команды с {arg1}, {arg2}")
    # Логика команды
    return True
```

### Тестирование

```bash
# Установка зависимостей для разработки
pip install -e .[dev]

# Запуск тестов
pytest

# Проверка кода
black cli/
flake8 cli/
```

## 🐛 Устранение неполадок

### Сервис не запускается

```bash
# Проверьте статус
jalm status

# Посмотрите логи
jalm logs core-runner

# Проверьте Docker
docker ps
```

### Ошибки конфигурации

```bash
# Проверьте конфигурацию
cat ~/.jalm/config.json

# Создайте новую конфигурацию
rm ~/.jalm/config.json
jalm status  # Создаст конфигурацию по умолчанию
```

### Проблемы с Docker

```bash
# Проверьте Docker
docker --version
docker-compose --version

# Очистите контейнеры
docker system prune
```

## 📝 Лицензия

MIT License - см. файл LICENSE для деталей.

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

- **Issues:** https://github.com/jalm-foundation/jalm-full-stack/issues
- **Документация:** https://jalm.org/docs
- **Email:** info@jalm.org 