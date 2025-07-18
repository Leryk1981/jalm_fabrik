# 🚀 Однокликовый запуск Barbershop Plugin

## ⚡ Запуск за 30 секунд

### 1. Распаковка
```bash
unzip barbershop_deployment_demo_barbershop_001.zip
cd barbershop_plugin
```

### 2. Настройка ключей (обязательно)
```bash
# Скопируйте пример конфигурации
cp env.example .env

# Отредактируйте .env файл - добавьте ваши ключи:
nano .env
```

**Обязательные настройки:**
```env
# Telegram Bot (получите у @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username

# Firebase (создайте проект на console.firebase.google.com)
FIREBASE_PROJECT_ID=your-project-id

# Секретные ключи (сгенерируйте: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
```

### 3. Запуск одной командой
```bash
docker-compose up -d
```

### 4. Готово! 🎉
- **Telegram бот**: @your_bot_username
- **Веб-виджет**: http://localhost:8000
- **Админ панель**: http://localhost:8000/admin
- **API документация**: http://localhost:8000/docs

## 🔧 Управление

### Проверка статуса
```bash
docker-compose ps
```

### Просмотр логов
```bash
docker-compose logs -f barbershop
```

### Остановка
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart
```

## 🎯 Что получает пользователь

### ✅ Автоматически:
- **Готовый Docker образ** со всеми компонентами
- **Telegram бот** для записи
- **Веб-виджет** для сайта
- **Админ панель** для управления
- **API** для интеграций
- **База данных** с барберами
- **Мониторинг** и логирование

### 🔧 Требует настройки:
- Telegram Bot Token
- Firebase Project ID
- Секретные ключи

## 🎉 Заключение

**Принцип "без кода" полностью соблюден:**

1. ✅ **Распаковка** - извлекаем готовый образ
2. ✅ **Настройка ключей** - только обязательные параметры
3. ✅ **Один клик** - `docker-compose up -d`
4. ✅ **Готово** - все работает автоматически

Пользователю не нужно:
- ❌ Устанавливать Python
- ❌ Настраивать зависимости
- ❌ Конфигурировать серверы
- ❌ Писать код
- ❌ Разбираться в архитектуре

**Всё работает из коробки!** 🎯
