# Context7 Helper Makefile
# Автоматизация задач для Context7 Helper

.PHONY: help install test clean search generate status cleanup docker-build docker-run

# Переменные
PYTHON = python
PIP = pip
MODULE = context7_helper
CLI_SCRIPT = cd .. && $(PYTHON) -m $(MODULE).cli

help: ## Показать справку
	@echo "Context7 Helper - автоматический поиск кода для JALM Full Stack"
	@echo ""
	@echo "Доступные команды:"
	@echo "  install         - Установить зависимости"
	@echo "  test            - Запустить тесты"
	@echo "  test-coverage   - Запустить тесты с покрытием"
	@echo "  clean           - Очистить временные файлы"
	@echo "  search          - Поиск кода (пример)"
	@echo "  generate        - Генерация кандидатов из Research Layer"
	@echo "  status          - Статус Context7 Helper"
	@echo "  cleanup         - Очистка старых кандидатов"
	@echo "  test-integration- Тестирование интеграции"
	@echo "  docker-build    - Сборка Docker образа"
	@echo "  docker-run      - Запуск в Docker"
	@echo "  jalm-integrate  - Интеграция с JALM Full Stack CLI"
	@echo "  dev-install     - Установка для разработки"
	@echo "  format          - Форматирование кода"
	@echo "  lint            - Проверка кода"
	@echo "  demo            - Демонстрация функциональности"
	@echo "  pipeline        - Запуск полного пайплайна"
	@echo "  windows-install - Установка на Windows"
	@echo "  windows-test    - Тесты на Windows"
	@echo "  windows-search  - Поиск на Windows"
	@echo "  windows-generate- Генерация на Windows"
	@echo "  docs            - Генерация документации"
	@echo "  stats           - Статистика проекта"

install: ## Установить зависимости
	$(PIP) install -r requirements.txt
	cd .. && $(PIP) install -e .

test: ## Запустить тесты
	$(PYTHON) -m pytest test_context7.py -v

test-coverage: ## Запустить тесты с покрытием
	$(PYTHON) -m pytest test_context7.py --cov=$(MODULE) --cov-report=html

clean: ## Очистить временные файлы
	@echo "Очистка временных файлов..."
	@if exist *.pyc del /Q *.pyc
	@if exist __pycache__ rmdir /S /Q __pycache__
	@if exist *.egg-info rmdir /S /Q *.egg-info
	@if exist build rmdir /S /Q build
	@if exist dist rmdir /S /Q dist
	@if exist .pytest_cache rmdir /S /Q .pytest_cache
	@if exist htmlcov rmdir /S /Q htmlcov

search: ## Поиск кода (пример)
	$(CLI_SCRIPT) search --query "booking system" --top-k 3

generate: ## Генерация кандидатов из Research Layer
	$(CLI_SCRIPT) generate --research-dir research --top-k 3

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
	@if exist "../cli/commands/context7.py" ( \
		echo "Context7 Helper уже интегрирован в CLI" \
	) else ( \
		echo "Context7 Helper не интегрирован в CLI" \
		echo "Скопируйте cli/commands/context7.py в ../cli/commands/" \
	)

# Разработка
dev-install: ## Установка для разработки
	$(PIP) install -r requirements.txt
	cd .. && $(PIP) install -e .[dev]

format: ## Форматирование кода
	black $(MODULE)/*.py
	black test_*.py

lint: ## Проверка кода
	flake8 $(MODULE)/*.py
	flake8 test_*.py

# Демонстрация
demo: ## Демонстрация функциональности
	@echo "Демонстрация Context7 Helper"
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
	@echo "Запуск полного пайплайна Context7 Helper"
	@echo "1. Проверка статуса..."
	$(CLI_SCRIPT) status
	@echo "2. Генерация кандидатов..."
	$(CLI_SCRIPT) generate --research-dir research --top-k 3
	@echo "3. Очистка старых файлов..."
	$(CLI_SCRIPT) cleanup --days 7
	@echo "Пайплайн завершен!"

# Windows совместимость
windows-install: ## Установка на Windows
	$(PIP) install -r requirements.txt
	cd .. && $(PIP) install -e .

windows-test: ## Тесты на Windows
	$(PYTHON) -m pytest test_context7.py -v

windows-search: ## Поиск на Windows
	$(CLI_SCRIPT) search --query "booking system" --top-k 3

windows-generate: ## Генерация на Windows
	$(CLI_SCRIPT) generate --research-dir research --top-k 3

# Документация
docs: ## Генерация документации
	@echo "Генерация документации..."
	@python -c "import pdoc3; pdoc3.pdoc('$(MODULE)', output_directory='docs')" 2>nul || echo "pdoc3 не установлен. Установите: pip install pdoc3"

# Статистика
stats: ## Статистика проекта
	@echo "Статистика Context7 Helper:"
	@echo "Файлы Python:"
	@dir /B *.py 2>nul | find /C /V "" || echo 0
	@echo "Строки кода:"
	@findstr /R /N "^" *.py 2>nul | find /C /V "" || echo 0
	@echo "Тесты:"
	@dir /B test_*.py 2>nul | find /C /V "" || echo 0
	@echo "Кандидаты:"
	@if exist tool_candidates\*.json (dir /B tool_candidates\*.json | find /C /V "") else (echo 0) 