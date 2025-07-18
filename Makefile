# JALM Full Stack - Корневой Makefile
# Управление всей системой JALM Full Stack

.PHONY: help start stop restart status health test clean demo build-all research-collect research-analyze research-integrate research-status

# Переменные
JALM_SERVICES_SCRIPT = start_jalm_services.py

help: ## Показать справку по командам
	@echo "JALM Full Stack - Корневой Makefile"
	@echo "====================================="
	@echo ""
	@echo "Доступные команды:"
	@echo "  help       - Показать эту справку"
	@echo "  start      - Запустить JALM сервисы"
	@echo "  stop       - Остановить JALM сервисы"
	@echo "  restart    - Перезапустить JALM сервисы"
	@echo "  status     - Статус всех сервисов"
	@echo "  health     - Проверить здоровье всех сервисов"
	@echo "  test       - Запустить все тесты"
	@echo "  clean      - Очистить все"
	@echo "  demo       - Запустить демонстрацию барбершопа"
	@echo "  build-all  - Собрать все компоненты"
	@echo ""
	@echo "Research Layer команды:"
	@echo "  research-collect   - Сбор данных через Research Layer"
	@echo "  research-analyze   - Анализ паттернов"
	@echo "  research-integrate - Интеграция с JALM компонентами"
	@echo "  research-status    - Статус Research Layer"

start: ## Запустить JALM сервисы
	@echo "Запуск JALM Full Stack сервисов..."
	@python $(JALM_SERVICES_SCRIPT)
	@echo "JALM сервисы запущены"
	@echo "Core Runner: http://localhost:8000"
	@echo "Tula Spec: http://localhost:8001"
	@echo "Shablon Spec: http://localhost:8002"

stop: ## Остановить JALM сервисы
	@echo "Остановка JALM сервисов..."
	@echo "Нажмите Ctrl+C в терминале с JALM сервисами"
	@echo "Или закройте терминал с start_jalm_services.py"

restart: ## Перезапустить JALM сервисы
	@echo "Перезапуск JALM сервисов..."
	@echo "Сначала остановите сервисы (Ctrl+C), затем запустите: make start"

status: ## Статус всех сервисов
	@echo "Статус JALM Full Stack:"
	@echo "1. JALM сервисы:"
	@curl -s -o nul -w "   Core Runner (8000): %%{http_code}\n" http://localhost:8000/health 2>nul || echo "   Core Runner (8000): Недоступен"
	@curl -s -o nul -w "   Tula Spec (8001): %%{http_code}\n" http://localhost:8001/health 2>nul || echo "   Tula Spec (8001): Недоступен"
	@curl -s -o nul -w "   Shablon Spec (8002): %%{http_code}\n" http://localhost:8002/health 2>nul || echo "   Shablon Spec (8002): Недоступен"
	@echo "2. Клиентские продукты:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr demo 2>nul || echo "   Нет запущенных клиентских продуктов"

health: ## Проверить здоровье всех сервисов
	@echo "Проверка здоровья JALM Full Stack..."
	@echo "JALM сервисы:"
	@curl -f http://localhost:8000/health && echo "✅ Core Runner здоров" || echo "❌ Core Runner недоступен"
	@curl -f http://localhost:8001/health && echo "✅ Tula Spec здоров" || echo "❌ Tula Spec недоступен"
	@curl -f http://localhost:8002/health && echo "✅ Shablon Spec здоров" || echo "❌ Shablon Spec недоступен"
	@echo "Клиентские продукты:"
	@curl -f http://localhost:8080/health && echo "✅ Демо-продукт здоров" || echo "❌ Демо-продукт недоступен"

test: ## Запустить все тесты
	@echo "Запуск всех тестов JALM Full Stack..."
	@echo "1. Тестирование JALM сервисов..."
	@python test_discovery.py
	@echo "2. Тестирование демо-продукта..."
	@python test_barbershop_simple.py
	@echo "3. Тестирование полного сценария..."
	@python test_barbershop_scenario.py
	@echo "✅ Все тесты завершены"

demo: ## Запустить демонстрацию барбершопа
	@echo "Запуск демонстрации барбершопа..."
	@python demo_barbershop_deployment.py
	@echo "Демонстрация запущена"
	@echo "Доступна по адресу: http://localhost:8080"

build-all: ## Собрать все компоненты
	@echo "Сборка всех компонентов JALM Full Stack..."
	@echo "1. Сборка Core Runner..."
	@cd core-runner && make kernel_build
	@echo "2. Сборка Tula Spec..."
	@cd tula_spec && make build
	@echo "3. Сборка Shablon Spec..."
	@cd shablon_spec && make build
	@echo "4. Сборка демо-продукта..."
	@cd instances/demo && make build
	@echo "✅ Все компоненты собраны"

clean: ## Очистить все
	@echo "Очистка всех ресурсов JALM Full Stack..."
	@echo "1. Очистка клиентских продуктов..."
	@cd instances/demo && make clean
	@echo "2. Очистка JALM сервисов..."
	@cd core-runner && make kernel_clean
	@cd tula_spec && make clean
	@cd shablon_spec && make clean
	@echo "3. Очистка Docker..."
	@docker system prune -f
	@echo "✅ Очистка завершена"

# Команды для разработки
dev-setup: ## Настройка окружения разработки
	@echo "Настройка окружения разработки JALM Full Stack..."
	@echo "1. Установка Python зависимостей..."
	@pip install -r requirements.txt
	@echo "2. Установка Node.js зависимостей..."
	@cd instances/demo && npm install
	@echo "3. Проверка Docker..."
	@docker --version
	@echo "✅ Окружение разработки готово"

dev-test: ## Запуск тестов в режиме разработки
	@echo "Запуск тестов в режиме разработки..."
	@python -m pytest tests/ -v

# Research Layer команды
research-collect: ## Сбор данных через Research Layer
	@echo "Сбор данных через Research Layer..."
	@cd research && make collect
	@echo "✅ Сбор данных завершен"

research-analyze: ## Анализ паттернов через Research Layer
	@echo "Анализ паттернов через Research Layer..."
	@cd research && make analyze
	@echo "✅ Анализ паттернов завершен"

research-integrate: ## Интеграция с JALM компонентами
	@echo "Интеграция Research Layer с JALM компонентами..."
	@cd research && make artifacts
	@echo "✅ Интеграция завершена"

research-status: ## Статус Research Layer
	@echo "Статус Research Layer:"
	@cd research && make status

# Информация о системе
info: ## Информация о JALM Full Stack
	@echo "JALM Full Stack - Информация о системе:"
	@echo "  Архитектура: Правильная JALM-land"
	@echo "  Core Runner: Порт 8000"
	@echo "  Tula Spec: Порт 8001"
	@echo "  Shablon Spec: Порт 8002"
	@echo "  Research Layer: Порт 8003"
	@echo "  Клиентские продукты: Порт 8080+"
	@echo "  Размер клиентского продукта: ~50MB"
	@echo "  Общий размер системы: Минимальный"
