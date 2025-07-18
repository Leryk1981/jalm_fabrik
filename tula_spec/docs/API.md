# Tula Spec API Documentation

## Обзор

Tula Spec API предоставляет интерфейс для управления и выполнения функций JALM. API построен на FastAPI и поддерживает все операции CRUD для функций.

## Базовый URL

```
http://localhost:8001
```

## Endpoints

### 1. Корневой endpoint

**GET /** - Информация о сервисе

```bash
curl http://localhost:8001/
```

**Ответ:**
```json
{
  "service": "Tula Spec API",
  "version": "1.0.0",
  "description": "API для управления функциями JALM"
}
```

### 2. Проверка здоровья

**GET /health** - Статус сервиса

```bash
curl http://localhost:8001/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "total_functions": 3,
  "last_updated": "2024-06-12T10:00:00Z"
}
```

### 3. Список функций

**GET /functions** - Получение списка всех функций

**Параметры:**
- `tag` (опционально) - фильтр по тегу
- `author` (опционально) - фильтр по автору

```bash
# Все функции
curl http://localhost:8001/functions

# Фильтр по тегу
curl "http://localhost:8001/functions?tag=booking"

# Фильтр по автору
curl "http://localhost:8001/functions?author=JALM%20Foundation"
```

**Ответ:**
```json
[
  {
    "id": "slot_validator",
    "version": "1.3.2",
    "hash": "ab12fe89c456def0123456789abcdef012345678",
    "description": "Валидатор слотов бронирования",
    "tags": ["booking", "validation", "slots"],
    "author": "JALM Foundation",
    "input_schema": {...},
    "output_schema": {...},
    "implementation": {...},
    "dependencies": [],
    "runtime": {...}
  }
]
```

### 4. Получение функции

**GET /functions/{function_id}** - Получение метаданных функции

**Параметры:**
- `version` (опционально) - версия функции
- `hash` (опционально) - хеш функции

```bash
# Последняя версия
curl http://localhost:8001/functions/slot_validator

# Конкретная версия
curl "http://localhost:8001/functions/slot_validator?version=1.3.2"

# По хешу
curl "http://localhost:8001/functions/slot_validator?hash=ab12fe89c456def0123456789abcdef012345678"
```

### 5. Выполнение функции

**POST /functions/{function_id}/execute** - Выполнение функции

**Тело запроса:**
```json
{
  "function_id": "slot_validator",
  "version": "1.3.2",
  "hash": null,
  "params": {
    "slot": {
      "datetime": "2024-06-15T10:00:00Z",
      "duration": 60,
      "service_id": "123e4567-e89b-12d3-a456-426614174000"
    }
  }
}
```

```bash
curl -X POST http://localhost:8001/functions/slot_validator/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "slot": {
        "datetime": "2024-06-15T10:00:00Z",
        "duration": 60,
        "service_id": "123e4567-e89b-12d3-a456-426614174000"
      }
    }
  }'
```

**Ответ:**
```json
{
  "function_id": "slot_validator",
  "result": {
    "slot_uuid": "7fce9ecb-f6a2-4651-b41e-723384a91adf",
    "status": "valid",
    "message": "Слот успешно создан"
  },
  "execution_time": 0.001234,
  "status": "success"
}
```

### 6. Информация о функции

**GET /functions/{function_id}/info** - Детальная информация о функции

```bash
curl http://localhost:8001/functions/slot_validator/info
```

**Ответ:**
```json
{
  "metadata": {
    "id": "slot_validator",
    "version": "1.3.2",
    ...
  },
  "info": {
    "name": "slot_validator",
    "version": "1.3.2",
    "description": "Валидатор слотов бронирования",
    "functions": ["create"]
  }
}
```

## Коды ошибок

- `404` - Функция не найдена
- `500` - Внутренняя ошибка сервера
- `422` - Ошибка валидации данных

## Примеры использования

### Выполнение slot_validator

```bash
curl -X POST http://localhost:8001/functions/slot_validator/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "slot": {
        "datetime": "2024-06-15T10:00:00Z",
        "duration": 60,
        "service_id": "123e4567-e89b-12d3-a456-426614174000"
      }
    }
  }'
```

### Выполнение booking_widget

```bash
curl -X POST http://localhost:8001/functions/booking_widget/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "calendar_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "user-123"
    }
  }'
```

### Выполнение notify_system

```bash
curl -X POST http://localhost:8001/functions/notify_system/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "message": "Ваш слот подтвержден",
      "channel": "web",
      "recipient": "user@example.com",
      "notification_type": "confirmed"
    }
  }'
```

## Интеграция с JALM

Функции из Tula Spec используются в JALM-интентах:

```jalm
BEGIN booking-flow
  IMPORT slot_validator tula:hash~ab12fe
  IMPORT booking_widget v1.3.2
  IMPORT notify_system v1.0.0
  
  WHEN client REQUESTS slot
    RUN slot_uuid := slot_validator.create(slot)
    IF slot_uuid.status == "valid" THEN
      RUN widget := booking_widget.create(calendar_id, user_id)
      RUN notify_system.send("Слот подтвержден", "web", user_email, "confirmed")
    END
END
``` 