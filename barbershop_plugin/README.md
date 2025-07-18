# 🪒 Barbershop Plugin

**Полнофункциональная система бронирования для барбершопов с Telegram ботом, веб-виджетом и админ панелью**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-orange.svg)](https://core.telegram.org/bots)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-yellow.svg)](https://firebase.google.com)
[![AWS](https://img.shields.io/badge/AWS-Lambda-red.svg)](https://aws.amazon.com/lambda)

## 🎯 Возможности

### 🤖 Telegram Bot
- Автоматическое бронирование через чат
- Выбор барбера и услуги
- Подтверждение времени
- Уведомления и напоминания

### 🌐 Веб-виджет
- Встраиваемый календарь
- Выбор услуг и барберов
- Онлайн оплата
- Мобильная адаптация

### 👨‍💼 Админ панель
- Управление барберами
- Настройка услуг и цен
- Просмотр бронирований
- Аналитика и отчеты

### 🔧 API
- RESTful API для интеграций
- Webhook поддержка
- Документация Swagger
- Аутентификация JWT

## 🚀 Быстрый старт

### 1. Установка
```bash
# Распакуйте архив
unzip barbershop_deployment_demo_barbershop_001.zip
cd barbershop_plugin

# Автоматическая установка
python setup.py
```

### 2. Настройка
```bash
# Настройте переменные окружения
cp env.example .env
# Отредактируйте .env файл
```

### 3. Запуск
```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
python scripts/status.py
```

### 4. Тестирование
```bash
# Откройте в браузере
http://localhost:8000
```

## 📁 Структура проекта

```
barbershop_plugin/
├── 📄 manifest.json          # Манифест плагина
├── 🤖 llm_actions.json       # LLM сценарии
├── 🌐 plugin.js              # Веб-виджет
├── 📊 migrations.csv         # Данные барберов
├── 📖 INSTALLATION_GUIDE.md  # Подробное руководство
├── ⚡ QUICK_START.md         # Быстрый старт
├── 🔧 setup.py               # Автоматическая установка
├── 📦 requirements.txt       # Python зависимости
├── 🐳 docker-compose.yml     # Docker конфигурация
├── 📝 env.example            # Пример конфигурации
├── 📁 scripts/               # Вспомогательные скрипты
├── 📁 logs/                  # Логи приложения
├── 📁 data/                  # Данные приложения
└── 📁 backups/               # Резервные копии
```

## 🔧 Конфигурация

### Обязательные настройки:

#### Telegram Bot
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook/telegram
```

#### Firebase
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

#### AWS Lambda
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## 🌐 Интеграция на сайт

### HTML код для вставки:
```html
<!-- Добавьте в <head> -->
<script src="https://your-domain.com/barbershop-widget.js"></script>

<!-- Добавьте в <body> -->
<div id="barbershop-booking-widget"></div>
```

### JavaScript инициализация:
```javascript
BarbershopWidget.init({
    apiEndpoint: 'https://your-api-gateway-url.amazonaws.com',
    theme: 'modern',
    language: 'ru'
});
```

## 📱 Telegram Bot

### Команды бота:
- `/start` - Начать бронирование
- `/services` - Список услуг
- `/barbers` - Список барберов
- `/schedule` - Расписание
- `/cancel` - Отменить бронирование
- `/help` - Помощь

### Пример диалога:
```
👤 Пользователь: /start
🤖 Бот: Добро пожаловать! Выберите услугу:
   1. Стрижка (1500₽)
   2. Борода (800₽)
   3. Стрижка + Борода (2000₽)

👤 Пользователь: 1
🤖 Бот: Выберите барбера:
   1. Иван (специализация: стрижки)
   2. Петр (специализация: все виды)

👤 Пользователь: 1
🤖 Бот: Выберите дату и время:
   15.01.2024: 10:00, 12:00, 14:00
   16.01.2024: 11:00, 13:00, 15:00

👤 Пользователь: 15.01.2024 10:00
🤖 Бот: ✅ Бронирование подтверждено!
   Услуга: Стрижка
   Барбер: Иван
   Дата: 15.01.2024 10:00
   Цена: 1500₽
```

## 🛠️ API Endpoints

### Основные endpoints:
```
GET  /api/barbers          # Список барберов
GET  /api/services         # Список услуг
GET  /api/schedule         # Расписание
POST /api/bookings         # Создать бронирование
GET  /api/bookings/{id}    # Получить бронирование
PUT  /api/bookings/{id}    # Обновить бронирование
DELETE /api/bookings/{id}  # Отменить бронирование
```

### Пример запроса:
```bash
curl -X POST "https://your-api.com/api/bookings" \
  -H "Content-Type: application/json" \
  -d '{
    "barber_id": "barber_1",
    "service_id": "service_1",
    "datetime": "2024-01-15T10:00:00Z",
    "client_name": "Иван",
    "client_phone": "+79991234567"
  }'
```

## 📊 Админ панель

### Возможности:
- 👥 Управление барберами
- 💇‍♂️ Настройка услуг
- 📅 Управление расписанием
- 📊 Просмотр статистики
- 💰 Управление ценами
- 🔔 Настройка уведомлений

### Доступ:
```
URL: http://localhost:8000/admin
Логин: admin
Пароль: admin123
```

## 🧪 Тестирование

### Запуск тестов:
```bash
# Все тесты
python -m pytest tests/

# Конкретный тест
python -m pytest tests/test_booking.py -v

# С покрытием
python -m pytest --cov=app tests/
```

### Проверка здоровья:
```bash
# Проверка API
curl http://localhost:8000/health

# Проверка всех сервисов
python scripts/status.py
```

## 🔧 Управление

### Основные команды:
```bash
# Статус сервисов
python scripts/status.py

# Перезапуск
python scripts/restart.py

# Логи
docker-compose logs -f

# Остановка
docker-compose down

# Резервное копирование
python scripts/backup.py

# Очистка
python scripts/cleanup.py
```

## 📈 Мониторинг

### Метрики:
- Количество бронирований
- Доход по дням/неделям/месяцам
- Популярные услуги
- Занятость барберов
- Отмены и переносы

### Логи:
- Логи приложения: `logs/app.log`
- Логи Docker: `docker-compose logs`
- Логи Lambda: AWS CloudWatch

## 🔒 Безопасность

### Реализованные меры:
- JWT аутентификация
- HTTPS шифрование
- CORS защита
- Rate limiting
- Валидация входных данных
- SQL injection защита

### Рекомендации:
- Регулярно обновляйте зависимости
- Используйте сильные пароли
- Настройте SSL сертификаты
- Включите двухфакторную аутентификацию
- Регулярно делайте резервные копии

## 🚀 Развертывание

### Поддерживаемые платформы:
- **AWS** - Lambda + API Gateway + RDS
- **Google Cloud** - Cloud Functions + Firestore
- **Azure** - Functions + Cosmos DB
- **VPS** - Docker + PostgreSQL
- **Heroku** - Dyno + PostgreSQL

### Автоматическое развертывание:
```bash
# AWS
python scripts/deploy_aws.py

# Google Cloud
python scripts/deploy_gcp.py

# Azure
python scripts/deploy_azure.py
```

## 📞 Поддержка

### Контакты:
- **Email**: support@barbershop-plugin.com
- **Telegram**: @barbershop_support
- **Документация**: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)

### Полезные ссылки:
- [Firebase Documentation](https://firebase.google.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Вклад в проект

### Как помочь:
1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

### Стандарты кода:
- Python: PEP 8
- JavaScript: ESLint
- Git: Conventional Commits
- Документация: Markdown

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🙏 Благодарности

- [JALM Full Stack](https://github.com/jalm-full-stack) - основа системы
- [FastAPI](https://fastapi.tiangolo.com/) - веб-фреймворк
- [Telegram Bot API](https://core.telegram.org/bots) - мессенджер интеграция
- [Firebase](https://firebase.google.com/) - база данных
- [AWS Lambda](https://aws.amazon.com/lambda/) - серверные функции

---

**🎉 Спасибо за использование Barbershop Plugin!**

Если вам понравился проект, поставьте ⭐ на GitHub! 