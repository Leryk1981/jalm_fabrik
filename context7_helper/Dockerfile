# Context7 Helper Dockerfile
# Контейнеризация модуля автоматического поиска кода

FROM python:3.11-slim

# Метаданные
LABEL maintainer="JALM Foundation"
LABEL description="Context7 Helper - автоматический поиск кода для JALM Full Stack"
LABEL version="1.0.0"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .
COPY setup.py .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# Копирование исходного кода
COPY context7_helper/ ./context7_helper/
COPY test_context7.py .
COPY Makefile .
COPY README.md .

# Создание директорий для данных
RUN mkdir -p /app/research /app/tool_candidates

# Переменные окружения
ENV PYTHONPATH=/app
ENV CONTEXT7_API_KEY=""
ENV CONTEXT7_MCP_URL="http://localhost:4000/v1"

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from context7_helper import IntegrationManager; \
    manager = IntegrationManager(); \
    status = manager.get_status(); \
    exit(0 if status['context7_api'] else 1)"

# Точка входа
ENTRYPOINT ["python", "-m", "context7_helper.cli"]

# Команда по умолчанию
CMD ["status"] 