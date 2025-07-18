# Tula Spec - Каталог функций JALM

## Описание
Tula Spec - это каталог функций (tula) для JALM Full Stack. Содержит переиспользуемые функции, валидаторы и утилиты, которые могут быть импортированы в JALM-интенты через директиву `IMPORT`.

## Архитектура

### Структура каталога
```
tula_spec/
├── api/           # FastAPI сервер для управления функциями
├── functions/     # Каталог функций (tula)
├── registry/      # Реестр функций с метаданными
├── tests/         # Тесты функций
└── docs/          # Документация
```

### Спецификация функций (tula)

#### Формат функции
```json
{
  "id": "slot_validator",
  "version": "1.3.2",
  "hash": "ab12fe...",
  "description": "Валидатор слотов бронирования",
  "input_schema": {
    "slot": {
      "type": "object",
      "properties": {
        "datetime": {"type": "string", "format": "datetime"},
        "duration": {"type": "integer", "minimum": 15}
      }
    }
  },
  "output_schema": {
    "slot_uuid": {"type": "string", "format": "uuid"},
    "status": {"type": "string", "enum": ["valid", "invalid"]}
  },
  "implementation": {
    "type": "python",
    "code": "def create(slot): ..."
  }
}
```

#### Импорт в JALM
```jalm
IMPORT slot_validator v1.3.2
IMPORT slot_validator tula:hash~ab12fe
```

#### Выполнение
```jalm
RUN slot_uuid := slot_validator.create(slot)
```

## Компоненты

### 1. API Server (`api/`)
- CRUD операции для функций
- Поиск по хешу/версии
- Валидация функций
- Интеграция с core-runner

### 2. Function Registry (`registry/`)
- Метаданные всех функций
- Версионирование (SemVer)
- Хеши для идентификации
- Зависимости между функциями

### 3. Function Catalog (`functions/`)
- Реализации функций
- Поддержка Python, JavaScript
- Тестирование функций
- Документация

## Интеграция с Core Runner

Core Runner загружает функции из Tula Spec:
1. Поиск функции по хешу или версии
2. Загрузка реализации
3. Выполнение через `RUN` команду
4. Возврат результата в JALM-интент

## Разработка

### Добавление новой функции
1. Создать файл в `functions/`
2. Добавить метаданные в `registry/`
3. Написать тесты в `tests/`
4. Обновить документацию

### Тестирование
```bash
cd tula_spec
python -m pytest tests/
```

### Сборка и публикация
```bash
make build
make publish
```

## Лицензия
MIT / JALM Foundation 