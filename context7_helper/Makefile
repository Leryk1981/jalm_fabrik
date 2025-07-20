# Context7 Helper Makefile
# Автоматизация задач для Context7 Helper

.PHONY: help install test clean search generate status cleanup docker-build docker-run

# Переменные
PYTHON = python
PIP = pip
MODULE = context7_helper
CLI_SCRIPT = $(PYTHON) -m $(MODULE).cli

help: ## Показать справку
	@echo "Context7 Helper - автоматический поиск кода для JALM Full Stack"
	@echo ""
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

test: ## Запустить тесты
	$(PYTHON) -m pytest test_context7.py -v

test-coverage: ## Запустить тесты с покрытием
	$(PYTHON) -m pytest test_context7.py --cov=$(MODULE) --cov-report=html

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ htmlcov/

search: ## Поиск кода (пример)
	$(CLI_SCRIPT) search --query "booking system" --top-k 3

generate: ## Генерация кандидатов из Research Layer
	$(CLI_SCRIPT) generate --research-dir ../research --top-k 3

status: ## Статус Context7 Helper
	$(CLI_SCRIPT) status

cleanup: ## Очистка старых кандидатов
	$(CLI_SCRIPT) cleanup --days 7

test-integration: ## Тестирование интеграции
	$(CLI_SCRIPT) test

# Docker команды
docker-build: ## Сборка Docker образа
	docker build -t context7-helper .

docker-run: ## Запуск в Docker
	docker run -it --rm \
		-v $(PWD)/../research:/app/research \
		-v $(PWD)/tool_candidates:/app/tool_candidates \
		-e CONTEXT7_API_KEY=$(CONTEXT7_API_KEY) \
		context7-helper

# Интеграция с JALM Full Stack
jalm-integrate: ## Интеграция с JALM Full Stack CLI
	@echo "Добавление Context7 Helper в JALM CLI..."
	@if [ -f "../cli/commands/context7.py" ]; then \
		echo "✅ Context7 Helper уже интегрирован в CLI"; \
	else \
		echo "❌ Context7 Helper не интегрирован в CLI"; \
		echo "Скопируйте cli/commands/context7.py в ../cli/commands/"; \
	fi

# Разработка
dev-install: ## Установка для разработки
	$(PIP) install -r requirements.txt
	$(PIP) install -e .[dev]

format: ## Форматирование кода
	black $(MODULE)/*.py
	black test_*.py

lint: ## Проверка кода
	flake8 $(MODULE)/*.py
	flake8 test_*.py

# Демонстрация
demo: ## Демонстрация функциональности
	@echo "🎯 Демонстрация Context7 Helper"
	@echo ""
	@echo "1. Проверка статуса:"
	$(CLI_SCRIPT) status
	@echo ""
	@echo "2. Поиск кода:"
	$(CLI_SCRIPT) search --query "fastapi endpoint" --top-k 2
	@echo ""
	@echo "3. Тестирование:"
	$(CLI_SCRIPT) test

# Полный пайплайн
pipeline: ## Запуск полного пайплайна
	@echo "🚀 Запуск полного пайплайна Context7 Helper"
	@echo "1. Проверка статуса..."
	$(CLI_SCRIPT) status
	@echo "2. Генерация кандидатов..."
	$(CLI_SCRIPT) generate --research-dir ../research --top-k 3
	@echo "3. Очистка старых файлов..."
	$(CLI_SCRIPT) cleanup --days 7
	@echo "✅ Пайплайн завершен!"

# Windows совместимость
windows-install: ## Установка на Windows
	python -m pip install -r requirements.txt
	python -m pip install -e .

windows-test: ## Тесты на Windows
	python -m pytest test_context7.py -v

windows-search: ## Поиск на Windows
	python -m context7_helper.cli search --query "booking system" --top-k 3

windows-generate: ## Генерация на Windows
	python -m context7_helper.cli generate --research-dir ../research --top-k 3

# Документация
docs: ## Генерация документации
	@echo "📚 Генерация документации..."
	@if command -v pdoc3 >/dev/null 2>&1; then \
		pdoc3 --html $(MODULE) --output-dir docs; \
		echo "✅ Документация сгенерирована в docs/"; \
	else \
		echo "❌ pdoc3 не установлен. Установите: pip install pdoc3"; \
	fi

# Статистика
stats: ## Статистика проекта
	@echo "📊 Статистика Context7 Helper:"
	@echo "Файлы Python: $(shell find $(MODULE) -name '*.py' | wc -l)"
	@echo "Строки кода: $(shell find $(MODULE) -name '*.py' -exec wc -l {} + | tail -1)"
	@echo "Тесты: $(shell find . -name 'test_*.py' | wc -l)"
	@echo "Кандидаты: $(shell find tool_candidates -name '*.json' 2>/dev/null | wc -l || echo 0)" 