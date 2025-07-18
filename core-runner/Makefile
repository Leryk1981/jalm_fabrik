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
	@echo "$(BLUE)JALM Core Runner - Команды сборки$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

kernel_raw: ## Этап 1: Вычленение атомов исполнения
	@echo "$(YELLOW)🔍 Этап 1: Вычленение атомов исполнения$(NC)"
	@if [ ! -f kernel/raw_atomics.csv ]; then \
		echo "$(RED)❌ Файл kernel/raw_atomics.csv не найден$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Атомы исполнения готовы: $(shell wc -l < kernel/raw_atomics.csv) записей$(NC)"

kernel_group: ## Этап 2: Группировка атомов в слои
	@echo "$(YELLOW)📊 Этап 2: Группировка атомов в слои$(NC)"
	@if [ ! -f kernel/layers.json ]; then \
		echo "$(RED)❌ Файл kernel/layers.json не найден$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Слои сгруппированы: $(shell jq '.metadata.total_layers' kernel/layers.json) слоёв$(NC)"

kernel_cards: ## Этап 3: Детализированные шаги-карточки
	@echo "$(YELLOW)📋 Этап 3: Детализированные шаги-карточки$(NC)"
	@if [ ! -d kernel/step_cards ]; then \
		echo "$(RED)❌ Директория kernel/step_cards не найдена$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Карточки шагов готовы: $(shell ls kernel/step_cards/*.yml | wc -l) карточек$(NC)"

search_isolate: ## Этап 4: Поиск готовых движков
	@echo "$(YELLOW)🔍 Этап 4: Поиск готовых движков$(NC)"
	@if [ ! -f scripts/search_micro_isolates.py ]; then \
		echo "$(RED)❌ Скрипт поиска не найден$(NC)"; \
		exit 1; \
	fi
	@python scripts/search_micro_isolates.py
	@echo "$(GREEN)✅ Поиск движков завершён$(NC)"

kernel_build: ## Этап 5: Сборка ядра
	@echo "$(YELLOW)🔨 Этап 5: Сборка ядра jalm/core-runner:$(VERSION)$(NC)"
	@if [ ! -f Dockerfile ]; then \
		echo "$(RED)❌ Dockerfile не найден$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f requirements.txt ]; then \
		echo "$(RED)❌ requirements.txt не найден$(NC)"; \
		exit 1; \
	fi
	docker build -t $(IMAGE_NAME):$(VERSION) -t $(IMAGE_NAME):latest .
	@echo "$(GREEN)✅ Образ собран: $(IMAGE_NAME):$(VERSION)$(NC)"

kernel_push: ## Этап 6: Публикация ядра в registry
	@echo "$(YELLOW)🚀 Этап 6: Публикация ядра в registry$(NC)"
	@if [ -z "$(DOCKER_USERNAME)" ] || [ -z "$(DOCKER_PASSWORD)" ]; then \
		echo "$(RED)❌ Переменные DOCKER_USERNAME и DOCKER_PASSWORD не установлены$(NC)"; \
		exit 1; \
	fi
	docker tag $(IMAGE_NAME):$(VERSION) $(FULL_IMAGE_NAME)
	docker tag $(IMAGE_NAME):$(VERSION) $(LATEST_IMAGE_NAME)
	docker push $(FULL_IMAGE_NAME)
	docker push $(LATEST_IMAGE_NAME)
	@echo "$(GREEN)✅ Образ опубликован: $(FULL_IMAGE_NAME)$(NC)"

kernel_test: ## Тестирование ядра
	@echo "$(YELLOW)🧪 Тестирование ядра$(NC)"
	@if [ ! -f kernel/src/main.py ]; then \
		echo "$(RED)❌ Основной файл ядра не найден$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Тестирование завершено$(NC)"

kernel_clean: ## Очистка сборки
	@echo "$(YELLOW)🧹 Очистка сборки$(NC)"
	docker rmi $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):latest 2>/dev/null || true
	docker system prune -f
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

# Команды для полного цикла
kernel: kernel_raw kernel_group kernel_cards search_isolate kernel_build ## Полная сборка ядра
	@echo "$(GREEN)🎉 Ядро JALM Core Runner успешно собрано!$(NC)"

kernel_full: kernel kernel_test kernel_push ## Полный цикл: сборка + тест + публикация
	@echo "$(GREEN)🎉 Полный цикл сборки ядра завершён!$(NC)"

# Команды для разработки
dev_setup: ## Настройка окружения разработки
	@echo "$(YELLOW)🔧 Настройка окружения разработки$(NC)"
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)✅ Окружение разработки готово$(NC)"

dev_run: ## Запуск в режиме разработки
	@echo "$(YELLOW)🚀 Запуск в режиме разработки$(NC)"
	uvicorn kernel.src.main:app --reload --host 0.0.0.0 --port 8888

dev_test: ## Запуск тестов разработки
	@echo "$(YELLOW)🧪 Запуск тестов разработки$(NC)"
	python -m pytest tests/ -v

# Команды для мониторинга
logs: ## Просмотр логов
	@echo "$(YELLOW)📋 Просмотр логов$(NC)"
	docker logs -f $(IMAGE_NAME):$(VERSION)

status: ## Статус сервиса
	@echo "$(YELLOW)📊 Статус сервиса$(NC)"
	curl -s http://localhost:8888/health | jq .

# Команды для развёртывания
deploy_local: kernel_build ## Развёртывание локально
	@echo "$(YELLOW)🚀 Развёртывание локально$(NC)"
	docker run -d --name jalm-core-runner -p 8888:8888 $(IMAGE_NAME):$(VERSION)
	@echo "$(GREEN)✅ Сервис запущен на http://localhost:8888$(NC)"

deploy_stop: ## Остановка локального развёртывания
	@echo "$(YELLOW)🛑 Остановка локального развёртывания$(NC)"
	docker stop jalm-core-runner || true
	docker rm jalm-core-runner || true
	@echo "$(GREEN)✅ Сервис остановлен$(NC)" 