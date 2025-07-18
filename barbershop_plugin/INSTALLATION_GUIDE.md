# 🪒 Руководство по установке и запуску Barbershop Plugin

## 📋 Содержание
1. [Предварительные требования](#предварительные-требования)
2. [Быстрая установка](#быстрая-установка)
3. [Пошаговая установка](#пошаговая-установка)
4. [Настройка Telegram бота](#настройка-telegram-бота)
5. [Настройка Firebase](#настройка-firebase)
6. [Настройка AWS Lambda](#настройка-aws-lambda)
7. [Интеграция на сайт](#интеграция-на-сайт)
8. [Тестирование](#тестирование)
9. [Устранение неполадок](#устранение-неполадок)
10. [Поддержка](#поддержка)

## 🔧 Предварительные требования

### Обязательные компоненты:
- **Python 3.8+** с pip
- **Docker** и Docker Compose
- **Git**
- **Node.js 16+** (для сборки фронтенда)

### Обязательные аккаунты:
- **Telegram Bot Token** (от @BotFather)
- **Firebase Project** с Firestore
- **AWS Account** (для Lambda функций)
- **GitHub Account** (для webhook)

## ⚡ Быстрая установка

### 1. Распаковка и запуск
```bash
# Распакуйте ZIP-архив
unzip barbershop_deployment_demo_barbershop_001.zip
cd barbershop_plugin

# Запустите автоматическую установку
python setup.py
```

### 2. Настройка переменных окружения
```bash
# Скопируйте шаблон конфигурации
cp .env.example .env

# Отредактируйте файл .env
nano .env
```

### 3. Запуск сервисов
```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

## 📝 Пошаговая установка

### Шаг 1: Подготовка окружения

```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### Шаг 2: Настройка базы данных

```bash
# Инициализация Firebase
python scripts/init_firebase.py

# Создание коллекций
python scripts/setup_database.py
```

### Шаг 3: Настройка Telegram бота

```bash
# Создание бота через @BotFather
# Получите токен и добавьте в .env

# Настройка webhook
python scripts/setup_telegram_webhook.py
```

### Шаг 4: Развертывание Lambda

```bash
# Настройка AWS credentials
aws configure

# Создание Lambda функции
python scripts/deploy_lambda.py
```

## 🤖 Настройка Telegram бота

### 1. Создание бота
1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

### 2. Настройка webhook
```bash
# Добавьте токен в .env
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Настройте webhook
python scripts/setup_telegram_webhook.py
```

### 3. Тестирование бота
1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Проверьте ответы на команды

## 🔥 Настройка Firebase

### 1. Создание проекта
1. Перейдите на [Firebase Console](https://console.firebase.google.com/)
2. Создайте новый проект
3. Включите Firestore Database
4. Скачайте service account key

### 2. Настройка Firestore
```bash
# Добавьте credentials в .env
FIREBASE_CREDENTIALS_PATH=path/to/serviceAccountKey.json

# Инициализация базы
python scripts/init_firebase.py
```

### 3. Структура данных
```
barbershop/
├── barbers/
│   ├── barber_id_1/
│   │   ├── name: "Иван"
│   │   ├── specialties: ["стрижка", "борода"]
│   │   └── schedule: {...}
├── appointments/
│   ├── appointment_id_1/
│   │   ├── barber_id: "barber_id_1"
│   │   ├── client_name: "Петр"
│   │   ├── service: "стрижка"
│   │   └── datetime: "2024-01-15T10:00:00Z"
└── settings/
    ├── working_hours: {...}
    └── services: [...]
```

## ☁️ Настройка AWS Lambda

### 1. Подготовка AWS
```bash
# Установка AWS CLI
pip install awscli

# Настройка credentials
aws configure
```

### 2. Создание Lambda функции
```bash
# Создание функции
python scripts/deploy_lambda.py

# Проверка статуса
aws lambda get-function --function-name barbershop-booking
```

### 3. Настройка API Gateway
```bash
# Создание API
python scripts/setup_api_gateway.py

# Получение endpoint URL
python scripts/get_api_endpoint.py
```

## 🌐 Интеграция на сайт

### 1. Добавление виджета
```html
<!-- Добавьте в <head> вашего сайта -->
<script src="https://your-domain.com/barbershop-widget.js"></script>

<!-- Добавьте в <body> -->
<div id="barbershop-booking-widget"></div>
```

### 2. Инициализация виджета
```javascript
// Инициализация виджета
BarbershopWidget.init({
    apiEndpoint: 'https://your-api-gateway-url.amazonaws.com',
    theme: 'modern',
    language: 'ru'
});
```

### 3. Кастомизация стилей
```css
/* Ваши стили для виджета */
#barbershop-booking-widget {
    font-family: 'Arial', sans-serif;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
```

## 🧪 Тестирование

### 1. Запуск тестов
```bash
# Запуск всех тестов
python -m pytest tests/

# Запуск конкретного теста
python -m pytest tests/test_booking.py -v
```

### 2. Проверка API
```bash
# Тест endpoints
python scripts/test_api.py

# Проверка здоровья сервисов
curl http://localhost:8000/health
```

### 3. Тестирование виджета
```bash
# Запуск локального сервера
python -m http.server 8080

# Откройте http://localhost:8080 в браузере
```

## 🔧 Устранение неполадок

### Частые проблемы:

#### 1. Ошибка подключения к Firebase
```bash
# Проверьте credentials
python scripts/verify_firebase.py

# Пересоздайте service account key
```

#### 2. Telegram бот не отвечает
```bash
# Проверьте webhook
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo

# Переустановите webhook
python scripts/setup_telegram_webhook.py
```

#### 3. Lambda функция недоступна
```bash
# Проверьте логи
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/barbershop

# Пересоздайте функцию
python scripts/redeploy_lambda.py
```

#### 4. Виджет не загружается
```bash
# Проверьте CORS настройки
python scripts/check_cors.py

# Проверьте SSL сертификат
openssl s_client -connect your-domain.com:443
```

### Логи и отладка:
```bash
# Просмотр логов Docker
docker-compose logs -f

# Логи приложения
tail -f logs/app.log

# Логи Lambda
aws logs tail /aws/lambda/barbershop-booking --follow
```

## 📞 Поддержка

### Полезные команды:
```bash
# Статус всех сервисов
python scripts/status.py

# Перезапуск сервисов
python scripts/restart.py

# Очистка данных
python scripts/cleanup.py

# Резервное копирование
python scripts/backup.py
```

### Контакты для поддержки:
- **Email**: support@barbershop-plugin.com
- **Telegram**: @barbershop_support
- **Документация**: https://docs.barbershop-plugin.com

### Полезные ссылки:
- [Firebase Documentation](https://firebase.google.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [JALM Full Stack](https://github.com/jalm-full-stack)

## 🎯 Следующие шаги

После успешной установки:

1. **Настройте барберов** в админ панели
2. **Добавьте услуги** и цены
3. **Настройте расписание** работы
4. **Протестируйте** полный цикл бронирования
5. **Настройте уведомления** для клиентов
6. **Добавьте аналитику** и отчеты

---

**🎉 Поздравляем! Ваш барбершоп готов к работе!**

Для получения дополнительной помощи обратитесь к документации или свяжитесь с поддержкой. 