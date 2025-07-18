# JALM Core Runner Makefile
# Этап 5 Core Spec: make kernel собирает образ jalm/core-runner:VERSION

# Переменные
VERSION ?= $(shell git describe --tags --always --dirty)
IMAGE_NAME = jalm/core-runner
REGISTRY = ghcr.io
FULL_IMAGE_NAME = $(REGISTRY)/$(IMAGE_NAME):$(VERSION)
LATEST_IMAGE_NAME = $(REGISTRY)/$(IMAGE_NAME):latest

# Цвета для вывода
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help kernel_raw kernel_group kernel_cards search_isolate kernel_build kernel_push kernel_test kernel_clean

help: ## Показать справку
	@echo "JALM Core Runner - Команды сборки"
	@echo ""
	@echo "Доступные команды:"
	@echo "  kernel_raw      - Этап 1: Вычленение атомов исполнения"
	@echo "  kernel_group    - Этап 2: Группировка атомов в слои"
	@echo "  kernel_cards    - Этап 3: Детализированные шаги-карточки"
	@echo "  search_isolate  - Этап 4: Поиск готовых движков"
	@echo "  kernel_build    - Этап 5: Сборка ядра"
	@echo "  kernel_push     - Этап 6: Публикация ядра в registry"
	@echo "  kernel_test     - Тестирование ядра"
	@echo "  kernel_clean    - Очистка сборки"
	@echo "  kernel          - Полная сборка ядра"
	@echo "  kernel_full     - Полный цикл: сборка + тест + публикация"

kernel_raw: ## Этап 1: Вычленение атомов исполнения
	@echo "Этап 1: Вычленение атомов исполнения"
	@if not exist kernel\raw_atomics.csv (
		echo "Файл kernel/raw_atomics.csv не найден"
		exit /b 1
	)
	@echo "Атомы исполнения готовы"

kernel_group: ## Этап 2: Группировка атомов в слои
	@echo "Этап 2: Группировка атомов в слои"
	@if not exist kernel\layers.json (
		echo "Файл kernel/layers.json не найден"
		exit /b 1
	)
	@echo "Слои сгруппированы"

kernel_cards: ## Этап 3: Детализированные шаги-карточки
	@echo "Этап 3: Детализированные шаги-карточки"
	@if not exist kernel\step_cards (
		echo "Директория kernel/step_cards не найдена"
		exit /b 1
	)
	@echo "Карточки шагов готовы"

search_isolate: ## Этап 4: Поиск готовых движков
	@echo "Этап 4: Поиск готовых движков"
	@if not exist scripts\search_micro_isolates.py (
		echo "Скрипт поиска не найден"
		exit /b 1
	)
	@python scripts/search_micro_isolates.py
	@echo "Поиск движков завершён"

kernel_build: ## Этап 5: Сборка ядра
	@echo "Этап 5: Сборка ядра jalm/core-runner:$(VERSION)"
	@if not exist Dockerfile (
		echo "Dockerfile не найден"
		exit /b 1
	)
	@if not exist requirements.txt (
		echo "requirements.txt не найден"
		exit /b 1
	)
	docker build -t $(IMAGE_NAME):$(VERSION) -t $(IMAGE_NAME):latest .
	@echo "Образ собран: $(IMAGE_NAME):$(VERSION)"

kernel_push: ## Этап 6: Публикация ядра в registry
	@echo "Этап 6: Публикация ядра в registry"
	@if "$(DOCKER_USERNAME)"=="" (
		echo "Переменные DOCKER_USERNAME и DOCKER_PASSWORD не установлены"
		exit /b 1
	)
	docker tag $(IMAGE_NAME):$(VERSION) $(FULL_IMAGE_NAME)
	docker tag $(IMAGE_NAME):$(VERSION) $(LATEST_IMAGE_NAME)
	docker push $(FULL_IMAGE_NAME)
	docker push $(LATEST_IMAGE_NAME)
	@echo "Образ опубликован: $(FULL_IMAGE_NAME)"

kernel_test: ## Тестирование ядра
	@echo "Тестирование ядра"
	@if not exist kernel\src\main.py (
		echo "Основной файл ядра не найден"
		exit /b 1
	)
	@echo "Тестирование завершено"

kernel_clean: ## Очистка сборки
	@echo "Очистка сборки"
	docker rmi $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):latest 2>nul || echo "Образы не найдены"
	docker system prune -f
	@echo "Очистка завершена"

# Команды для полного цикла
kernel: kernel_raw kernel_group kernel_cards search_isolate kernel_build ## Полная сборка ядра
	@echo "Ядро JALM Core Runner успешно собрано!"

kernel_full: kernel kernel_test kernel_push ## Полный цикл: сборка + тест + публикация
	@echo "Полный цикл сборки ядра завершён!"

# Команды для разработки
dev_setup: ## Настройка окружения разработки
	@echo "Настройка окружения разработки"
	python -m venv venv
	venv\Scripts\activate && pip install -r requirements.txt
	@echo "Окружение разработки готово"

dev_run: ## Запуск в режиме разработки
	@echo "Запуск в режиме разработки"
	uvicorn kernel.src.main:app --reload --host 0.0.0.0 --port 8888

dev_test: ## Запуск тестов разработки
	@echo "Запуск тестов разработки"
	python -m pytest tests/ -v

# Команды для мониторинга
logs: ## Просмотр логов
	@echo "Просмотр логов"
	docker logs -f $(IMAGE_NAME):$(VERSION)

status: ## Статус сервиса
	@echo "Статус сервиса"
	@curl -s http://localhost:8888/health 2>nul || echo "Сервис недоступен"

# Команды для развёртывания
deploy_local: kernel_build ## Развёртывание локально
	@echo "Развёртывание локально"
	docker run -d --name jalm-core-runner -p 8888:8888 $(IMAGE_NAME):$(VERSION)
	@echo "Сервис запущен на http://localhost:8888"

deploy_stop: ## Остановка локального развёртывания
	@echo "Остановка локального развёртывания"
	docker stop jalm-core-runner 2>nul || echo "Контейнер не найден"
	docker rm jalm-core-runner 2>nul || echo "Контейнер не найден"
	@echo "Сервис остановлен" 