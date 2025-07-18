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
	@echo "JALM Full Stack - Готовый продукт"
	@echo "====================================="
	@echo ""
	@echo "Компоненты готового продукта:"
	@echo "  - Core Runner (порт 8000): Исполнительное ядро"
	@echo "  - Tula Spec (порт 8001): Каталог функций"
	@echo "  - Shablon Spec (порт 8002): Каталог шаблонов"
	@echo ""
	@echo "Доступные команды:"
	@echo "  build         - Собрать все Docker образы"
	@echo "  build-fast    - Быстрая сборка (без --no-cache)"
	@echo "  run           - Запустить все сервисы"
	@echo "  stop          - Остановить все сервисы"
	@echo "  restart       - Перезапустить все сервисы"
	@echo "  logs          - Показать логи всех сервисов"
	@echo "  status        - Показать статус всех сервисов"
	@echo "  health        - Проверить здоровье всех сервисов"
	@echo "  test          - Запустить тесты готового продукта"
	@echo "  clean         - Очистить все (контейнеры, образы, тома)"
	@echo "  backup        - Создать резервную копию данных"
	@echo "  restore       - Восстановить данные из резервной копии"

build: ## Собрать все Docker образы
	@echo "Сборка Docker образов JALM Full Stack..."
	docker-compose -f $(COMPOSE_FILE) build --no-cache
	@echo "Все образы собраны успешно"

build-fast: ## Быстрая сборка (без --no-cache)
	@echo "Быстрая сборка Docker образов..."
	docker-compose -f $(COMPOSE_FILE) build
	@echo "Все образы собраны успешно"

run: ## Запустить все сервисы
	@echo "Запуск JALM Full Stack - готового продукта..."
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "Все сервисы запущены"
	@echo "Доступные сервисы:"
	@echo "   - Core Runner: http://localhost:8000"
	@echo "   - Tula Spec: http://localhost:8001"
	@echo "   - Shablon Spec: http://localhost:8002"

stop: ## Остановить все сервисы
	@echo "Остановка всех сервисов..."
	docker-compose -f $(COMPOSE_FILE) down
	@echo "Все сервисы остановлены"

restart: ## Перезапустить все сервисы
	@echo "Перезапуск всех сервисов..."
	docker-compose -f $(COMPOSE_FILE) restart
	@echo "Все сервисы перезапущены"

logs: ## Показать логи всех сервисов
	@echo "Логи всех сервисов:"
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-core: ## Показать логи Core Runner
	@echo "Логи Core Runner:"
	docker-compose -f $(COMPOSE_FILE) logs -f core-runner

logs-tula: ## Показать логи Tula Spec
	@echo "Логи Tula Spec:"
	docker-compose -f $(COMPOSE_FILE) logs -f tula-spec

logs-shablon: ## Показать логи Shablon Spec
	@echo "Логи Shablon Spec:"
	docker-compose -f $(COMPOSE_FILE) logs -f shablon-spec

status: ## Показать статус всех сервисов
	@echo "Статус сервисов:"
	docker-compose -f $(COMPOSE_FILE) ps

health: ## Проверить здоровье всех сервисов
	@echo "Проверка здоровья сервисов..."
	@echo -n "Порт 8000: "
	@curl -s -o nul -w "%%{http_code}" http://localhost:8000/health 2>nul || echo "недоступен"
	@echo -n "Порт 8001: "
	@curl -s -o nul -w "%%{http_code}" http://localhost:8001/health 2>nul || echo "недоступен"
	@echo -n "Порт 8002: "
	@curl -s -o nul -w "%%{http_code}" http://localhost:8002/health 2>nul || echo "недоступен"

test: ## Запустить тесты готового продукта
	@echo "Запуск тестов готового продукта..."
	@echo "Тестирование Core Runner..."
	@curl -f http://localhost:8000/health || echo "Core Runner недоступен"
	@echo "Тестирование Tula Spec..."
	@curl -f http://localhost:8001/health || echo "Tula Spec недоступен"
	@echo "Тестирование Shablon Spec..."
	@curl -f http://localhost:8002/health || echo "Shablon Spec недоступен"

shell-core: ## Войти в контейнер Core Runner
	@echo "Вход в Core Runner..."
	docker-compose -f $(COMPOSE_FILE) exec core-runner /bin/sh

shell-tula: ## Войти в контейнер Tula Spec
	@echo "Вход в Tula Spec..."
	docker-compose -f $(COMPOSE_FILE) exec tula-spec /bin/bash

shell-shablon: ## Войти в контейнер Shablon Spec
	@echo "Вход в Shablon Spec..."
	docker-compose -f $(COMPOSE_FILE) exec shablon-spec /bin/bash

clean: ## Очистить все (контейнеры, образы, тома)
	@echo "Очистка всех Docker ресурсов..."
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker system prune -f
	@echo "Очистка завершена"

clean-volumes: ## Очистить только тома
	@echo "Очистка томов..."
	docker-compose -f $(COMPOSE_FILE) down -v
	@echo "Тома очищены"

backup: ## Создать резервную копию данных
	@echo "Создание резервной копии..."
	@if not exist backups mkdir backups
	@docker run --rm -v jalm_data:/data -v %cd%/backups:/backup alpine tar czf /backup/jalm_data_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.tar.gz -C /data .
	@echo "Резервная копия создана в папке backups/"

restore: ## Восстановить данные из резервной копии
	@echo "Восстановление данных..."
	@if "$(BACKUP_FILE)"=="" (
		echo "Укажите файл резервной копии: make restore BACKUP_FILE=backups/filename.tar.gz"
		exit /b 1
	)
	@docker run --rm -v jalm_data:/data -v %cd%/$(BACKUP_FILE):/backup.tar.gz alpine sh -c "cd /data && tar xzf /backup.tar.gz"
	@echo "Данные восстановлены"

monitor: ## Мониторинг ресурсов
	@echo "Мониторинг ресурсов контейнеров:"
	docker stats jalm-core-runner jalm-tula-spec jalm-shablon-spec

# Команды для работы с сетью
network-info: ## Информация о сети
	@echo "Информация о сети:"
	docker network ls | findstr jalm
	docker network inspect docker_jalm-network 2>nul || echo "Сеть не найдена"

# Команды для работы с томами
volumes-info: ## Информация о томах
	@echo "Информация о томах:"
	docker volume ls | findstr jalm
	@echo "Том jalm_data:"
	@docker volume inspect docker_jalm_data 2>nul | findstr "Mountpoint Size" || echo "  Не найден"
	@echo "Том jalm_logs:"
	@docker volume inspect docker_jalm_logs 2>nul | findstr "Mountpoint Size" || echo "  Не найден" 