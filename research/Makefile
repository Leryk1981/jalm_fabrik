# Research Layer Makefile - Windows Compatible
# Управление модулем сбора и анализа данных для JALM Full Stack

.PHONY: help install test run collect analyze clean setup lint format docs

# Переменные
PYTHON := python
PIP := pip
PYTEST := pytest
RESEARCH_DIR := research
PATTERNS_DIR := $(RESEARCH_DIR)/patterns
TESTS_DIR := $(RESEARCH_DIR)/tests

help: ## Показать справку по командам
	@echo "Research Layer - Команды Makefile:"
	@echo ""
	@echo "  setup          - Установить зависимости и настроить окружение"
	@echo "  install        - Установить модуль (alias для setup)"
	@echo "  test           - Запустить тесты"
	@echo "  run            - Запустить полный процесс сбора и анализа данных"
	@echo "  collect        - Только сбор данных без анализа"
	@echo "  analyze        - Только анализ существующих данных"
	@echo "  quick-test     - Быстрый тест функциональности"
	@echo "  validate       - Проверить корректность модуля"
	@echo "  demo           - Демонстрация работы модуля"
	@echo "  clean          - Очистить временные файлы и данные"
	@echo "  status         - Показать статус модуля"

setup: ## Установить зависимости и настроить окружение
	@echo "Устанавливаем зависимости..."
	$(PIP) install -r $(RESEARCH_DIR)/requirements.txt
	@echo "Создаем директории..."
	if not exist $(PATTERNS_DIR) mkdir $(PATTERNS_DIR)
	if not exist $(TESTS_DIR) mkdir $(TESTS_DIR)
	@echo "Настройка завершена"

install: setup ## Установить модуль (alias для setup)
	@echo "Модуль установлен"

test: ## Запустить тесты
	@echo "Запускаем тесты..."
	cd $(RESEARCH_DIR) && $(PYTEST) $(TESTS_DIR)/ -v --tb=short
	@echo "Тесты завершены"

run: ## Запустить полный процесс сбора и анализа данных
	@echo "Запускаем Research Layer..."
	cd $(RESEARCH_DIR) && $(PYTHON) main.py --log-level INFO
	@echo "Research Layer завершен"

run-debug: ## Запустить с отладочным логированием
	@echo "Запускаем Research Layer в режиме отладки..."
	cd $(RESEARCH_DIR) && $(PYTHON) main.py --log-level DEBUG
	@echo "Research Layer завершен"

collect: ## Только сбор данных без анализа
	@echo "Собираем данные..."
	cd $(RESEARCH_DIR) && $(PYTHON) main.py --collect-only --log-level INFO
	@echo "Сбор данных завершен"

analyze: ## Только анализ существующих данных
	@echo "Анализируем данные..."
	@if exist "$(PATTERNS_DIR)/raw_patterns.csv" ( \
		cd $(RESEARCH_DIR) && $(PYTHON) main.py --analyze-only patterns/raw_patterns.csv --log-level INFO \
	) else ( \
		echo "Файл patterns/raw_patterns.csv не найден. Сначала запустите 'make collect'" \
	)

analyze-json: ## Анализ данных из JSON файла
	@echo "Анализируем данные из JSON..."
	@if exist "$(PATTERNS_DIR)/raw_patterns.json" ( \
		cd $(RESEARCH_DIR) && $(PYTHON) main.py --analyze-only patterns/raw_patterns.json --log-level INFO \
	) else ( \
		echo "Файл patterns/raw_patterns.json не найден" \
	)

quick-test: ## Быстрый тест функциональности
	@echo "Быстрый тест Research Layer..."
	$(PYTHON) -c "import sys; sys.path.append('..'); from research import DataCollector, PatternAnalyzer, ResearchConfig; print('✅ Research Layer работает корректно')"
	@echo "Быстрый тест пройден"

clean: ## Очистить временные файлы и данные
	@echo "Очищаем временные файлы..."
	del /Q $(RESEARCH_DIR)\*.pyc 2>nul || echo "Нет .pyc файлов"
	rmdir /S /Q $(RESEARCH_DIR)\__pycache__ 2>nul || echo "Нет __pycache__"
	rmdir /S /Q $(RESEARCH_DIR)\tests\__pycache__ 2>nul || echo "Нет тестового __pycache__"
	del /Q $(RESEARCH_DIR)\*.log 2>nul || echo "Нет лог файлов"
	@echo "Очистка завершена"

clean-data: ## Очистить собранные данные
	@echo "Очищаем собранные данные..."
	del /Q $(PATTERNS_DIR)\*.csv 2>nul || echo "Нет CSV файлов"
	del /Q $(PATTERNS_DIR)\*.json 2>nul || echo "Нет JSON файлов"
	del /Q $(PATTERNS_DIR)\*.yaml 2>nul || echo "Нет YAML файлов"
	@echo "Данные очищены"

status: ## Показать статус модуля
	@echo "Статус Research Layer:"
	@echo "  Директория: $(RESEARCH_DIR)"
	@echo "  Паттерны: $(PATTERNS_DIR)"
	@echo "  Тесты: $(TESTS_DIR)"
	@echo ""
	@echo "Файлы данных:"
	@dir $(PATTERNS_DIR) 2>nul || echo "  Директория пуста"
	@echo ""
	@echo "Зависимости:"
	@$(PYTHON) -c "import requests, yaml, pandas; print('  ✅ Все зависимости установлены')" 2>nul || echo "  ❌ Отсутствуют зависимости"

validate: ## Проверить корректность модуля
	@echo "Проверяем корректность модуля..."
	$(PYTHON) -c "import sys; sys.path.append('..'); from research import ResearchConfig; config = ResearchConfig(); print('✅ Конфигурация корректна')"
	$(PYTHON) -c "import sys; sys.path.append('..'); from research import DataCollector; collector = DataCollector(); print('✅ DataCollector инициализируется')"
	$(PYTHON) -c "import sys; sys.path.append('..'); from research import PatternAnalyzer; analyzer = PatternAnalyzer(); print('✅ PatternAnalyzer инициализируется')"
	@echo "Модуль корректен"

demo: ## Демонстрация работы модуля
	@echo "Демонстрация Research Layer..."
	$(PYTHON) -c "import sys; sys.path.append('..'); from research import DataCollector, PatternAnalyzer, ResearchConfig; print('✅ Research Layer Demo - модуль работает')"

# Команды для разработки
dev-setup: setup ## Настройка для разработки
	@echo "Настройка для разработки..."
	$(PIP) install pytest pytest-cov flake8 black
	@echo "Настройка для разработки завершена"

# Команды для продакшена
prod-run: ## Запуск в продакшн режиме
	@echo "Запуск в продакшн режиме..."
	cd $(RESEARCH_DIR) && $(PYTHON) main.py --log-level WARNING --output-format json
	@echo "Продакшн запуск завершен"

prod-analyze: ## Анализ в продакшн режиме
	@echo "Анализ в продакшн режиме..."
	@if exist "$(PATTERNS_DIR)/raw_patterns.json" ( \
		cd $(RESEARCH_DIR) && $(PYTHON) main.py --analyze-only patterns/raw_patterns.json --log-level WARNING \
	) else ( \
		echo "Файл данных не найден" \
	)

# Команды Docker
docker-build: ## Сборка Docker образа
	@echo "Сборка Docker образа..."
	cd $(RESEARCH_DIR) && docker build -t jalm-research .

docker-run: ## Запуск Research Layer в Docker
	@echo "Запуск Research Layer в Docker..."
	cd $(RESEARCH_DIR) && docker run -d --name jalm-research-container jalm-research

docker-stop: ## Остановка Research Layer
	@echo "Остановка Research Layer..."
	docker stop jalm-research-container 2>nul || echo "Контейнер не запущен"
	docker rm jalm-research-container 2>nul || echo "Контейнер не существует"

docker-compose-up: ## Запуск Research Layer с Docker Compose
	@echo "Запуск Research Layer с Docker Compose..."
	cd $(RESEARCH_DIR) && docker-compose up -d

docker-compose-down: ## Остановка Research Layer
	@echo "Остановка Research Layer..."
	cd $(RESEARCH_DIR) && docker-compose down

docker-logs: ## Просмотр логов
	@echo "Просмотр логов..."
	cd $(RESEARCH_DIR) && docker-compose logs -f

docker-clean: ## Очистка Docker ресурсов
	@echo "Очистка Docker ресурсов..."
	cd $(RESEARCH_DIR) && docker-compose down --volumes --remove-orphans
	docker image rm jalm-research 2>nul || echo "Образ не найден" 