# JALM Full Stack Docker Management
# Управление готовым продуктом - SaaS-конструктор с LLM-ядром

.PHONY: help build run stop restart logs clean status health test

# Переменные
COMPOSE_FILE = docker-compose.yml

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)JALM Full Stack - Готовый продукт$(NC)"
	@echo "====================================="
	@echo ""
	@echo "$(YELLOW)Компоненты готового продукта:$(NC)"
	@echo "  - Core Runner (порт 8000): Исполнительное ядро"
	@echo "  - Tula Spec (порт 8001): Каталог функций"
	@echo "  - Shablon Spec (порт 8002): Каталог шаблонов"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Собрать все Docker образы
	@echo "$(GREEN)🔨 Сборка Docker образов JALM Full Stack...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache
	@echo "$(GREEN)✅ Все образы собраны успешно$(NC)"

build-fast: ## Быстрая сборка (без --no-cache)
	@echo "$(GREEN)🔨 Быстрая сборка Docker образов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build
	@echo "$(GREEN)✅ Все образы собраны успешно$(NC)"

run: ## Запустить все сервисы
	@echo "$(GREEN)🚀 Запуск JALM Full Stack - готового продукта...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Все сервисы запущены$(NC)"
	@echo "$(YELLOW)📊 Доступные сервисы:$(NC)"
	@echo "   - Core Runner: http://localhost:8000"
	@echo "   - Tula Spec: http://localhost:8001"
	@echo "   - Shablon Spec: http://localhost:8002"

stop: ## Остановить все сервисы
	@echo "$(YELLOW)🛑 Остановка всех сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✅ Все сервисы остановлены$(NC)"

restart: ## Перезапустить все сервисы
	@echo "$(YELLOW)🔄 Перезапуск всех сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)✅ Все сервисы перезапущены$(NC)"

logs: ## Показать логи всех сервисов
	@echo "$(GREEN)📋 Логи всех сервисов:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-core: ## Показать логи Core Runner
	@echo "$(GREEN)📋 Логи Core Runner:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f core-runner

logs-tula: ## Показать логи Tula Spec
	@echo "$(GREEN)📋 Логи Tula Spec:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f tula-spec

logs-shablon: ## Показать логи Shablon Spec
	@echo "$(GREEN)📋 Логи Shablon Spec:$(NC)"
	docker-compose -f $(COMPOSE_FILE) logs -f shablon-spec

status: ## Показать статус всех сервисов
	@echo "$(GREEN)📊 Статус сервисов:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

health: ## Проверить здоровье всех сервисов
	@echo "$(GREEN)🏥 Проверка здоровья сервисов...$(NC)"
	@for port in 8000 8001 8002; do \
		echo -n "Порт $$port: "; \
		curl -s -o /dev/null -w "%{http_code}" http://localhost:$$port/health 2>/dev/null || echo "недоступен"; \
	done

test: ## Запустить тесты готового продукта
	@echo "$(GREEN)🧪 Запуск тестов готового продукта...$(NC)"
	@echo "$(YELLOW)Тестирование Core Runner...$(NC)"
	curl -f http://localhost:8000/health || echo "❌ Core Runner недоступен"
	@echo "$(YELLOW)Тестирование Tula Spec...$(NC)"
	curl -f http://localhost:8001/health || echo "❌ Tula Spec недоступен"
	@echo "$(YELLOW)Тестирование Shablon Spec...$(NC)"
	curl -f http://localhost:8002/health || echo "❌ Shablon Spec недоступен"

shell-core: ## Войти в контейнер Core Runner
	@echo "$(GREEN)🐚 Вход в Core Runner...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec core-runner /bin/sh

shell-tula: ## Войти в контейнер Tula Spec
	@echo "$(GREEN)🐚 Вход в Tula Spec...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec tula-spec /bin/bash

shell-shablon: ## Войти в контейнер Shablon Spec
	@echo "$(GREEN)🐚 Вход в Shablon Spec...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec shablon-spec /bin/bash

clean: ## Очистить все (контейнеры, образы, тома)
	@echo "$(RED)🧹 Очистка всех Docker ресурсов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

clean-volumes: ## Очистить только тома
	@echo "$(YELLOW)🗑️ Очистка томов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v
	@echo "$(GREEN)✅ Тома очищены$(NC)"

backup: ## Создать резервную копию данных
	@echo "$(GREEN)💾 Создание резервной копии...$(NC)"
	@mkdir -p backups
	@docker run --rm -v jalm_data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/jalm_data_$(shell date +%Y%m%d_%H%M%S).tar.gz -C /data .
	@echo "$(GREEN)✅ Резервная копия создана в папке backups/$(NC)"

restore: ## Восстановить данные из резервной копии
	@echo "$(YELLOW)📥 Восстановление данных...$(NC)"
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)❌ Укажите файл резервной копии: make restore BACKUP_FILE=backups/filename.tar.gz$(NC)"; \
		exit 1; \
	fi
	@docker run --rm -v jalm_data:/data -v $(PWD)/$(BACKUP_FILE):/backup.tar.gz alpine sh -c "cd /data && tar xzf /backup.tar.gz"
	@echo "$(GREEN)✅ Данные восстановлены$(NC)"

monitor: ## Мониторинг ресурсов
	@echo "$(GREEN)📈 Мониторинг ресурсов контейнеров:$(NC)"
	docker stats jalm-core-runner jalm-tula-spec jalm-shablon-spec

# Команды для работы с сетью
network-info: ## Информация о сети
	@echo "$(GREEN)🌐 Информация о сети:$(NC)"
	docker network ls | grep jalm
	docker network inspect docker_jalm-network 2>/dev/null || echo "Сеть не найдена"

# Команды для работы с томами
volumes-info: ## Информация о томах
	@echo "$(GREEN)💾 Информация о томах:$(NC)"
	docker volume ls | grep jalm
	@for volume in jalm_data jalm_logs; do \
		echo "Том $$volume:"; \
		docker volume inspect docker_$$volume 2>/dev/null | grep -E '"Mountpoint"|"Size"' || echo "  Не найден"; \
	done 