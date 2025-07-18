# Makefile для Barbershop Plugin

.PHONY: help build test run clean docker-build docker-run docker-stop

# Переменные
IMAGE_NAME = barbershop-plugin
TAG = latest
CONTAINER_NAME = barbershop-container

help:
	@echo "Доступные команды:"
	@echo "  build         - Установка зависимостей"
	@echo "  test          - Запуск тестов"
	@echo "  run           - Запуск локально"
	@echo "  docker-build  - Сборка Docker образа"
	@echo "  docker-run    - Запуск Docker контейнера"
	@echo "  docker-stop   - Остановка Docker контейнера"
	@echo "  clean         - Очистка"

build:
	@echo "📦 Установка зависимостей..."
	pip install -r requirements.txt

test:
	@echo "🧪 Запуск тестов..."
	python -m pytest tests/ -v

run:
	@echo "🚀 Запуск локально..."
	python api/main.py

docker-build:
	@echo "🐳 Сборка Docker образа..."
	docker build -t $(IMAGE_NAME):$(TAG) .
	@echo "✅ Образ собран: $(IMAGE_NAME):$(TAG)"

docker-run:
	@echo "🚀 Запуск Docker контейнера..."
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p 8000:8000 \
		-p 8001:8001 \
		-p 8002:8002 \
		-e JALM_ENV=production \
		$(IMAGE_NAME):$(TAG)
	@echo "✅ Контейнер запущен: $(CONTAINER_NAME)"

docker-stop:
	@echo "🛑 Остановка Docker контейнера..."
	docker stop $(CONTAINER_NAME) 2>/dev/null || true
	docker rm $(CONTAINER_NAME) 2>/dev/null || true
	@echo "✅ Контейнер остановлен"

docker-logs:
	@echo "📋 Логи Docker контейнера..."
	docker logs -f $(CONTAINER_NAME)

docker-shell:
	@echo "🐚 Вход в Docker контейнер..."
	docker exec -it $(CONTAINER_NAME) /bin/sh

clean:
	@echo "🧹 Очистка..."
	docker rmi $(IMAGE_NAME):$(TAG) 2>/dev/null || true
	docker system prune -f
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✅ Очистка завершена"

# Команды для разработки
dev-install:
	@echo "📦 Установка зависимостей для разработки..."
	pip install -r requirements.txt

dev-test:
	@echo "🧪 Запуск тестов в режиме разработки..."
	python -m pytest tests/ -v --tb=short

dev-run:
	@echo "🚀 Запуск в режиме разработки..."
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Команды для продакшена
prod-build:
	@echo "🏭 Сборка для продакшена..."
	docker build -t $(IMAGE_NAME):prod --target production .
	@echo "✅ Продакшен образ собран"

prod-run:
	@echo "🚀 Запуск продакшена..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Продакшен запущен"

prod-stop:
	@echo "🛑 Остановка продакшена..."
	docker-compose -f docker-compose.prod.yml down
	@echo "✅ Продакшен остановлен"
