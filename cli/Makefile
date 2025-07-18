# JALM CLI Makefile

.PHONY: help install install-dev test clean lint format build run

# Переменные
PYTHON = python
PIP = pip
CLI_DIR = .

help: ## Показать справку
	@echo "JALM CLI - Доступные команды:"
	@echo "  install       - Установить CLI"
	@echo "  install-dev   - Установить CLI с зависимостями для разработки"
	@echo "  test          - Запустить тесты"
	@echo "  clean         - Очистить временные файлы"
	@echo "  lint          - Проверить код"
	@echo "  format        - Форматировать код"
	@echo "  build         - Собрать пакет"
	@echo "  run           - Запустить CLI (для разработки)"
	@echo "  demo          - Демонстрация CLI"
	@echo "  version       - Показать версию"
	@echo "  config        - Показать конфигурацию"

install: ## Установить CLI
	$(PIP) install -e .

install-dev: ## Установить CLI с зависимостями для разработки
	$(PIP) install -e .[dev]

test: ## Запустить тесты
	@if exist tests\ (
		$(PYTHON) -m pytest tests\ -v
	) else (
		echo "Директория tests не найдена"
	)

test-coverage: ## Запустить тесты с покрытием
	@if exist tests\ (
		$(PYTHON) -m pytest tests\ --cov=cli --cov-report=html --cov-report=term
	) else (
		echo "Директория tests не найдена"
	)

lint: ## Проверить код
	@if exist cli\ (
		flake8 cli\
		black --check cli\
	) else (
		echo "Директория cli не найдена"
	)

format: ## Форматировать код
	@if exist cli\ (
		black cli\
	) else (
		echo "Директория cli не найдена"
	)

clean: ## Очистить временные файлы
	@echo "Очистка временных файлов..."
	@for /r . %%f in (*.pyc) do @del "%%f" 2>nul
	@for /d /r . %%d in (__pycache__) do @rmdir /s /q "%%d" 2>nul
	@for /d /r . %%d in (*.egg-info) do @rmdir /s /q "%%d" 2>nul
	@if exist build\ rmdir /s /q build\ 2>nul
	@if exist dist\ rmdir /s /q dist\ 2>nul
	@if exist htmlcov\ rmdir /s /q htmlcov\ 2>nul
	@echo "Очистка завершена"

build: ## Собрать пакет
	$(PYTHON) setup.py sdist bdist_wheel

run: ## Запустить CLI (для разработки)
	$(PYTHON) cli\main.py

demo: ## Демонстрация CLI
	@echo "=== Демонстрация JALM CLI ==="
	@echo "1. Проверка версии:"
	$(PYTHON) cli\main.py --version
	@echo ""
	@echo "2. Справка:"
	$(PYTHON) cli\main.py --help
	@echo ""
	@echo "3. Статус сервисов:"
	$(PYTHON) cli\main.py status

check-deps: ## Проверить зависимости
	$(PIP) check

update-deps: ## Обновить зависимости
	$(PIP) install --upgrade -r requirements.txt

install-hooks: ## Установить git hooks
	@echo "Установка pre-commit hooks..."
	pre-commit install

uninstall: ## Удалить CLI
	$(PIP) uninstall jalm-cli -y

# Команды для разработки
dev-install: install-dev install-hooks ## Полная установка для разработки

dev-test: lint test ## Полное тестирование

dev-build: clean build ## Полная сборка

# Команды для CI/CD
ci-install: ## Установка для CI
	$(PIP) install -r requirements.txt

ci-test: ## Тестирование для CI
	@if exist tests\ (
		$(PYTHON) -m pytest tests\ --cov=cli --cov-report=xml
	) else (
		echo "Директория tests не найдена"
	)

ci-lint: ## Линтинг для CI
	@if exist cli\ (
		flake8 cli\
		black --check cli\
	) else (
		echo "Директория cli не найдена"
	)

# Специальные команды
version: ## Показать версию
	$(PYTHON) -c "import cli; print(cli.__version__)"

config: ## Показать конфигурацию
	$(PYTHON) -c "from cli.core.config import Config; c = Config(); print(c.config)"

# Команды для документации
docs: ## Создать документацию
	@echo "Создание документации..."
	@if not exist docs\ mkdir docs\
	@echo "Документация создана в docs\"

docs-serve: ## Запустить сервер документации
	@echo "Запуск сервера документации на http://localhost:8000"
	@if exist docs\ (
		python -m http.server 8000 --directory docs\
	) else (
		echo "Директория docs не найдена"
	)

# Команды для релиза
release-patch: ## Создать patch релиз
	bumpversion patch
	$(MAKE) build
	$(MAKE) test

release-minor: ## Создать minor релиз
	bumpversion minor
	$(MAKE) build
	$(MAKE) test

release-major: ## Создать major релиз
	bumpversion major
	$(MAKE) build
	$(MAKE) test 