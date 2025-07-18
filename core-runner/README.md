# JALM Core Runner

Исполнительное ядро для JALM Full Stack - безопасная среда выполнения JALM-конфигов с поддержкой 6 слоёв исполнения.

## 🏗️ Архитектура

### Структура проекта:
```
core-runner/
├── kernel/               # Исполнительные модули
│   ├── raw_atomics.csv   # Атомы исполнения
│   ├── layers.json       # Группировка по слоям
│   ├── step_cards/       # Детализированные шаги
│   └── src/main.py       # Основной код ядра
├── cfg/                  # Конфигурация рантайма
├── scheduler/            # Cron / event loop
├── registry-proxy/       # Pull tula на лету
├── api/                  # OpenAPI сервер ядра
├── state-store/          # Inmem KV + PostgreSQL
├── scripts/              # Скрипты сборки
├── dist/                 # Артефакты сборки
├── Dockerfile           # Многостадийная сборка
├── Makefile             # Команды сборки
└── requirements.txt     # Python-зависимости
```

### 6 слоёв исполнения:
- **io-http**: HTTP-запросы и API-вызовы
- **io-db**: Операции с базами данных
- **io-file**: Файловые операции
- **compute-script**: Вычислительные операции
- **render-html**: Рендеринг и генерация контента
- **notify-mq**: Уведомления и очереди сообщений

## 🚀 Быстрый старт

### Предварительные требования:
- Docker 20.10+
- Python 3.11+
- Make

### Сборка и запуск:
```bash
# Клонирование
git clone https://github.com/jalm/core-runner.git
cd core-runner

# Полная сборка ядра
make kernel

# Запуск в режиме разработки
make dev_run

# Развёртывание локально
make deploy_local
```

## 📋 Этапы сборки (Core Spec)

### Этап 1: Вычленение атомов исполнения
```bash
make kernel_raw
```
- Создаёт `kernel/raw_atomics.csv`
- 47 атомарных действий с характеристиками

### Этап 2: Группировка атомов в слои
```bash
make kernel_group
```
- Создаёт `kernel/layers.json`
- 6 слоёв с метаданными

### Этап 3: Детализированные шаги-карточки
```bash
make kernel_cards
```
- Создаёт `kernel/step_cards/*.yml`
- Детальное описание каждого шага

### Этап 4: Поиск готовых движков
```bash
make search_isolate
```
- Запускает `scripts/search_micro_isolates.py`
- Создаёт `candidates/isolates.json`

### Этап 5: Сборка ядра
```bash
make kernel_build
```
- Собирает Docker-образ `jalm/core-runner:VERSION`
- Многостадийная сборка с musl-runtime

### Этап 6: Публикация в registry
```bash
make kernel_push
```
- Публикует в `ghcr.io/jalm/core-runner:latest`
- Создаёт `catalog/core-runner.engine.json`

## 🔧 API Endpoints

### Основные endpoints:
- `GET /` - Информация о сервисе
- `GET /health` - Проверка здоровья
- `POST /exec` - Запуск выполнения JALM
- `GET /exec/{execution_id}` - Статус выполнения
- `GET /exec` - Список выполнений

### Пример использования:
```bash
# Запуск JALM-конфига
curl -X POST http://localhost:8888/exec \
  -H "Content-Type: application/json" \
  -d '{
    "jalm_config": {
      "intent": "test_execution",
      "steps": [
        {
          "id": "http_request",
          "layer": "io-http",
          "input": {
            "method": "GET",
            "url": "https://httpbin.org/json"
          }
        }
      ]
    }
  }'

# Проверка статуса
curl http://localhost:8888/exec/{execution_id}
```

## 🛡️ Безопасность

### Изоляция:
- Контейнерная изоляция с Docker
- Пользователь `jalm:jalm` без привилегий
- Readonly файловая система (кроме /data, /tmp)
- Ограничения ресурсов (CPU, память)

### Мониторинг:
- Structured logging
- Health checks
- Metrics endpoint
- Execution tracing

## 📊 Производительность

### Характеристики:
- **Размер образа**: ~150MB
- **Время запуска**: <2 секунды
- **Память**: 512MB (по умолчанию)
- **CPU**: 1 core (по умолчанию)
- **Поддерживаемые языки**: Python, JavaScript, TypeScript, Go, Rust

### Оптимизации:
- Многостадийная сборка Docker
- Alpine Linux base image
- Musl runtime
- Минимальные зависимости

## 🔄 Жизненный цикл

### Выполнение JALM:
1. **Приём конфига** - Валидация JALM-структуры
2. **Планирование** - Разбор на атомарные шаги
3. **Изоляция** - Запуск в безопасной среде
4. **Исполнение** - Выполнение по слоям
5. **Мониторинг** - Отслеживание прогресса
6. **Результат** - Возврат результатов/ошибок

### Состояния выполнения:
- `pending` - Ожидает запуска
- `running` - Выполняется
- `completed` - Успешно завершено
- `failed` - Завершено с ошибкой

## 🛠️ Разработка

### Настройка окружения:
```bash
make dev_setup
```

### Запуск тестов:
```bash
make dev_test
```

### Локальная сборка:
```bash
make kernel_build
```

### Очистка:
```bash
make kernel_clean
```

## 📚 Документация

- **API Docs**: http://localhost:8888/docs
- **ReDoc**: http://localhost:8888/redoc
- **GitHub**: https://github.com/jalm/core-runner

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 🔗 Ссылки

- [JALM Full Stack](https://github.com/jalm/jalm-stack)
- [Core Spec](../core_spec)
- [Tula Spec](../tula_spec)
- [Shablon Spec](../shablon_spec) 