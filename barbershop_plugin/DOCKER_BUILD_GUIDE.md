# 🐳 Сборка Docker образа

## ⚡ Быстрая сборка

### Вариант 1: Скрипт (рекомендуется)
```bash
./build.sh
```

### Вариант 2: Makefile
```bash
make docker-build
```

### Вариант 3: Docker напрямую
```bash
docker build -t barbershop-plugin:latest .
```

## 🔧 Проверка сборки

### Просмотр образов
```bash
docker images | grep barbershop
```

### Тестирование образа
```bash
# Запуск тестового контейнера
docker run -d --name test-barbershop \
  -p 8000:8000 -p 8001:8001 -p 8002:8002 \
  barbershop-plugin:latest

# Проверка здоровья
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health

# Остановка тестового контейнера
docker stop test-barbershop
docker rm test-barbershop
```

## 🚀 Запуск после сборки

### Использование docker-compose
```bash
# Настройка переменных окружения
cp env.example .env
nano .env

# Запуск
docker-compose up -d
```

### Использование Docker напрямую
```bash
docker run -d \
  --name barbershop-plugin \
  -p 8000:8000 -p 8001:8001 -p 8002:8002 \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e FIREBASE_PROJECT_ID=your_project \
  -e SECRET_KEY=your_secret \
  barbershop-plugin:latest
```

## 📊 Управление

### Просмотр логов
```bash
docker logs -f barbershop-plugin
```

### Остановка
```bash
docker stop barbershop-plugin
```

### Перезапуск
```bash
docker restart barbershop-plugin
```

### Вход в контейнер
```bash
docker exec -it barbershop-plugin /bin/sh
```

## 🎯 Результат

После успешной сборки вы получите:
- ✅ **Docker образ** barbershop-plugin:latest
- ✅ **Все компоненты** JALM Full Stack
- ✅ **Готовый к запуску** контейнер
- ✅ **Автоматическую инициализацию** всех сервисов

## 🔍 Устранение неполадок

### Ошибка "Docker не найден"
```bash
# Установка Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### Ошибка сборки
```bash
# Очистка кэша Docker
docker system prune -a

# Повторная сборка
docker build --no-cache -t barbershop-plugin:latest .
```

### Ошибка портов
```bash
# Проверка занятых портов
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001
netstat -tulpn | grep :8002

# Остановка процессов на портах
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:8001 | xargs kill -9
sudo lsof -ti:8002 | xargs kill -9
```
