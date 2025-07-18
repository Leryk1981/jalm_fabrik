#!/bin/sh
# Docker Entrypoint для Barbershop Plugin
# Запускает все сервисы JALM Full Stack

set -e

echo "🚀 Запуск Barbershop Plugin с JALM Full Stack"
echo "=============================================="

# Проверка переменных окружения
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠️  TELEGRAM_BOT_TOKEN не установлен"
fi

if [ -z "$FIREBASE_PROJECT_ID" ]; then
    echo "⚠️  FIREBASE_PROJECT_ID не установлен"
fi

# Создание необходимых директорий
mkdir -p /app/data /app/logs /app/tmp

# Инициализация базы данных (если нужно)
if [ ! -f /app/data/initialized ]; then
    echo "📊 Инициализация базы данных..."
    python -c "
import json
import os

# Создание базовой структуры данных
data = {
    'barbers': [
        {'id': 'barber_1', 'name': 'Иван', 'specialties': ['стрижка', 'борода']},
        {'id': 'barber_2', 'name': 'Петр', 'specialties': ['стрижка', 'окрашивание']}
    ],
    'services': [
        {'id': 'service_1', 'name': 'Стрижка', 'price': 1500, 'duration': 60},
        {'id': 'service_2', 'name': 'Борода', 'price': 800, 'duration': 30},
        {'id': 'service_3', 'name': 'Стрижка + Борода', 'price': 2000, 'duration': 90}
    ],
    'settings': {
        'working_hours': {'start': '09:00', 'end': '21:00'},
        'slot_duration': 60,
        'advance_booking_days': 14
    }
}

with open('/app/data/initial_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Создание маркера инициализации
with open('/app/data/initialized', 'w') as f:
    f.write('true')

print('✅ База данных инициализирована')
"
fi

# Запуск Core Runner (основной сервис)
echo "🔧 Запуск Core Runner на порту 8000..."
cd /app
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
CORE_PID=$!

# Запуск Tula Spec (функции)
echo "🔧 Запуск Tula Spec на порту 8001..."
cd /app
python -m uvicorn tula_spec.api.main:app --host 0.0.0.0 --port 8001 &
TULA_PID=$!

# Запуск Shablon Spec (шаблоны)
echo "🔧 Запуск Shablon Spec на порту 8002..."
cd /app
python -m uvicorn shablon_spec.api.main:app --host 0.0.0.0 --port 8002 &
SHABLON_PID=$!

# Ожидание запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 5

# Проверка здоровья сервисов
echo "🏥 Проверка здоровья сервисов..."

check_health() {
    local service=$1
    local port=$2
    local pid=$3
    
    if kill -0 $pid 2>/dev/null; then
        if curl -f -s http://localhost:$port/health >/dev/null 2>&1; then
            echo "✅ $service здоров (порт $port)"
            return 0
        else
            echo "⚠️  $service запущен, но health check не прошел"
            return 1
        fi
    else
        echo "❌ $service не запущен"
        return 1
    fi
}

check_health "Core Runner" 8000 $CORE_PID
check_health "Tula Spec" 8001 $TULA_PID
check_health "Shablon Spec" 8002 $SHABLON_PID

echo ""
echo "🎉 Barbershop Plugin запущен!"
echo "📊 Доступные сервисы:"
echo "   🌐 Основной API: http://localhost:8000"
echo "   🔧 Tula Spec: http://localhost:8001"
echo "   📋 Shablon Spec: http://localhost:8002"
echo "   📚 Документация: http://localhost:8000/docs"
echo ""
echo "🤖 Telegram бот: @${TELEGRAM_BOT_USERNAME:-your_bot}"
echo "🌐 Веб-виджет: http://localhost:8000/widget"
echo "👨‍💼 Админ панель: http://localhost:8000/admin"
echo ""
echo "⏹️  Для остановки нажмите Ctrl+C"

# Функция очистки при завершении
cleanup() {
    echo ""
    echo "🛑 Остановка сервисов..."
    kill $CORE_PID $TULA_PID $SHABLON_PID 2>/dev/null || true
    wait
    echo "✅ Все сервисы остановлены"
    exit 0
}

# Обработка сигналов завершения
trap cleanup SIGTERM SIGINT

# Ожидание завершения
wait
