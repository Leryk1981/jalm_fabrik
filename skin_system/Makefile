# Skin-As-Code система - Makefile
# Управление модулем Skin-As-Code

.PHONY: help install test lint format build docker-build docker-run docker-stop clean

# Переменные
PYTHON = python
PIP = pip
PYTEST = pytest
COVERAGE = coverage

# Цвета для вывода
GREEN = \033[0;32m
RED = \033[0;31m
YELLOW = \033[1;33m
NC = \033[0m # No Color

help:
	@echo "$(GREEN)Доступные команды:$(NC)"
	@echo "  install     - Установка зависимостей"
	@echo "  test        - Запуск тестов с покрытием"
	@echo "  lint        - Проверка качества кода"
	@echo "  format      - Форматирование кода"
	@echo "  build       - Сборка пакета"
	@echo "  docker-build- Сборка Docker образа"
	@echo "  docker-run  - Запуск Docker контейнера"
	@echo "  docker-stop - Остановка Docker контейнера"
	@echo "  clean       - Очистка временных файлов"

install:
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

test:
	@echo "$(GREEN)Запуск тестов Skin-As-Code...$(NC) "
	$(PYTHON) -m $(PYTEST) tests/ -v --cov=skin_system --cov-report=html --cov-report=term

lint:
	@echo "$(GREEN)Проверка качества кода...$(NC)"
	$(PYTHON) -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	$(PYTHON) -m pylint skin_system/ || true
	$(PYTHON) -m mypy skin_system/ || true

format:
	@echo "$(GREEN)Форматирование кода...$(NC)"
	$(PYTHON) -m black . --check || $(PYTHON) -m black .
	$(PYTHON) -m isort . --check-only || $(PYTHON) -m isort .

build:
	@echo "$(GREEN)Сборка пакета...$(NC)"
	$(PYTHON) setup.py sdist bdist_wheel

docker-build:
	@echo "$(GREEN)Сборка Docker образа...$(NC)"
	docker build -t skin-system .

docker-run:
	@echo "$(GREEN)Запуск Docker контейнера...$(NC)"
	docker-compose up -d

docker-stop:
	@echo "$(YELLOW)Остановка Docker контейнера...$(NC)"
	docker-compose down

clean:
	@echo "$(YELLOW)Очистка временных файлов...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Команды для управления скинами
create-skin:
	@echo "$(GREEN)Создание нового скина...$(NC)"
	@read -p "Введите имя клиента: " client; \
	read -p "Введите цвет (hex): " color; \
	read -p "Введите макет: " layout; \
	$(PYTHON) -m skin_system.cli create-skin --client=$$client --color=$$color --layout=$$layout

list-skins:
	@echo "$(GREEN)Список скинов:$(NC)"
	$(PYTHON) -m skin_system.cli list

validate-skin:
	@echo "$(GREEN)Валидация скина...$(NC)"
	@read -p "Введите имя клиента: " client; \
	$(PYTHON) -m skin_system.cli validate --client=$$client

delete-skin:
	@echo "$(RED)Удаление скина...$(NC)"
	@read -p "Введите имя клиента: " client; \
	$(PYTHON) -m skin_system.cli delete --client=$$client

serve:
	@echo "$(GREEN)Запуск сервера...$(NC)"
	$(PYTHON) -m skin_system.cli serve

# Команды для отладки
debug-info:
	@echo "$(GREEN)Информация о системе:$(NC)"
	@echo "Python версия: $$(python --version)"
	@echo "Pip версия: $$(pip --version)"
	@echo "Pytest версия: $$(pytest --version)"
	@echo "Текущая директория: $$(pwd)"
	@echo "Содержимое директории:"
	@ls -la

debug-test:
	@echo "$(GREEN)Запуск одного теста для отладки...$(NC)"
	$(PYTHON) -m $(PYTEST) tests/test_cli.py::TestSkinCLI::test_create_skin_command_success -v -s 