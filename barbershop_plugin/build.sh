#!/bin/bash
# Быстрая сборка Docker образа

echo "🚀 Быстрая сборка Barbershop Plugin..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Установите Docker и повторите попытку."
    exit 1
fi

# Сборка образа
echo "🐳 Сборка Docker образа..."
docker build -t barbershop-plugin:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker образ успешно собран!"
    echo "📦 Образ: barbershop-plugin:latest"
    echo ""
    echo "🚀 Для запуска выполните:"
    echo "   docker-compose up -d"
    echo ""
    echo "🌐 Доступные сервисы:"
    echo "   Основной API: http://localhost:8000"
    echo "   Tula Spec: http://localhost:8001"
    echo "   Shablon Spec: http://localhost:8002"
else
    echo "❌ Ошибка сборки Docker образа"
    exit 1
fi
