# 🏭 Toolifier — Фабрика JALM-Агентов

`toolifier/` — это инфраструктурный модуль, предназначенный для **генерации агентов** и **обёрток API** в формате [JALM](https://github.com/your-org/jalm-spec). Он не используется в боевом исполнении, а только на этапе сборки.

---

## 📦 Назначение

`toolifier/` выполняет следующие функции:

- Генерация `tool_api_catalog/*.api.json` из схем (`input_schema`, `output_schema`)
- Автоматическое обновление `tool_api_catalog.jalm.json`
- Генерация `.jalm.json` манифестов агентов
- Используется в `toolify_everything.py` как CLI-интерфейс

---

## 🧩 Состав

| Файл                            | Назначение                                                  |
|---------------------------------|-------------------------------------------------------------|
| `toolify_everything.py`         | Главный генератор API + JALM                                |
| `tool_api_catalog_gen.py`       | Формирует структуру `tool_api` по интенту                   |
| `jalm_manifest_gen.py`          | Создаёт `.jalm.json` для агента                             |

---

## 📌 Когда использовать

- При добавлении нового `tool_api` (действия)
- При создании нового агента
- При автосборке `.jalm.json` и каталога разрешённых API

---

## 🚫 Когда НЕ использовать

- В боевом сервере
- При исполнении JALM-интентов
- Для прямой обработки запросов

---

## 📎 Пример использования

```bash
python toolifier/toolify_everything.py \
  --agent client_bot \
  --intent отправить_напоминание \
  --url /send_reminder \
  --method POST \
  --input_schema '{"client_id": "string", "message": "string", "channel": "string"}' \
  --output_schema '{"status": "string", "sent_at": "ISO8601"}'
```

---

## 🔐 Безопасность

Никакие ключи и .env в `toolifier/` не используются — только структура, схемы и манифесты.

---