# Shablon Spec Makefile

.PHONY: help build test run clean publish

# Переменные
IMAGE_NAME = jalm-shablon-spec
IMAGE_TAG = latest
REGISTRY = jalm-registry.local

help:
	@echo "Доступные команды:"
	@echo "  build    - Сборка Docker образа"
	@echo "  test     - Запуск тестов"
	@echo "  run      - Запуск сервера локально"
	@echo "  clean    - Очистка"
	@echo "  publish  - Публикация образа"

build:
	@echo "Сборка Docker образа..."
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "Образ собран: $(IMAGE_NAME):$(IMAGE_TAG)"

test:
	@echo "Запуск тестов..."
	cd tests && python -m pytest -v

run:
	@echo "Запуск сервера на порту 8002..."
	python api/main.py

run-docker:
	@echo "Запуск в Docker..."
	docker run -p 8002:8002 $(IMAGE_NAME):$(IMAGE_TAG)

clean:
	@echo "Очистка..."
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

publish:
	@echo "Публикация образа..."
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "Образ опубликован: $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)"

# Команды для разработки
dev-install:
	@echo "Установка зависимостей для разработки..."
	pip install -r requirements.txt

dev-test:
	@echo "Запуск тестов в режиме разработки..."
	python -m pytest tests/ -v --tb=short

dev-run:
	@echo "Запуск сервера в режиме разработки..."
	uvicorn api.main:app --host 0.0.0.0 --port 8002 --reload

# Команды для работы с шаблонами
validate-template:
	@echo "Валидация всех шаблонов..."
	python -c "from api.main import validate_jalm_syntax; import os; [print(f'Validating {f}') or validate_jalm_syntax(open(f'templates/{f}').read()) for f in os.listdir('templates') if f.endswith('.jalm')]"

list-templates:
	@echo "Список шаблонов:"
	@ls -la templates/*.jalm 