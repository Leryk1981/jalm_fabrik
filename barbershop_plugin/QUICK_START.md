# 🚀 Быстрый старт Barbershop Plugin

## ⚡ 5 минут до запуска

### 1. Распаковка (30 секунд)
```bash
unzip barbershop_deployment_demo_barbershop_001.zip
cd barbershop_plugin
```

### 2. Настройка (2 минуты)
```bash
# Автоматическая установка
python setup.py

# Настройка конфигурации
cp env.example .env
# Отредактируйте .env файл
```

### 3. Запуск (2 минуты)
```bash
# Запуск сервисов
docker-compose up -d

# Проверка статуса
python scripts/status.py
```

### 4. Тестирование (30 секунд)
```bash
# Откройте в браузере
http://localhost:8000
```

## 🎯 Что получите

✅ **Готовый Telegram бот** для бронирования  
✅ **Встраиваемый виджет** для сайта  
✅ **Админ панель** для управления  
✅ **API** для интеграций  
✅ **База данных** с барберами  

## 📱 Тестирование

### Telegram бот
1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Выберите услугу и время

### Веб-виджет
1. Откройте `http://localhost:8000`
2. Выберите барбера
3. Забронируйте время

### Админ панель
1. Откройте `http://localhost:8000/admin`
2. Добавьте барберов
3. Настройте услуги

## 🔧 Основные команды

```bash
# Статус сервисов
python scripts/status.py

# Перезапуск
python scripts/restart.py

# Логи
docker-compose logs -f

# Остановка
docker-compose down
```

## 📞 Поддержка

- **Документация**: `INSTALLATION_GUIDE.md`
- **Email**: support@barbershop-plugin.com
- **Telegram**: @barbershop_support

---

**🎉 Готово! Ваш барбершоп работает!** 