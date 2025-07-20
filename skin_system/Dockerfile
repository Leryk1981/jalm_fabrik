# Skin-As-Code система - Dockerfile
FROM python:3.11-slim

# Метаданные
LABEL maintainer="JALM Foundation"
LABEL description="Skin-As-Code система для JALM Full Stack"
LABEL version="1.0.0"

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .
COPY requirements-dev.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY skin_system/ ./skin_system/
COPY setup.py .
COPY README.md .

# Создание необходимых директорий
RUN mkdir -p skin_system/skins/default \
    && mkdir -p skin_system/registry

# Инициализация default скина
RUN python -c "from skin_system import SkinStore; SkinStore()"

# Создание пользователя
RUN useradd --create-home --shell /bin/bash skinuser \
    && chown -R skinuser:skinuser /app

# Переключение на пользователя
USER skinuser

# Экспорт порта
EXPOSE 8080

# Переменные окружения
ENV PYTHONPATH=/app
ENV SKIN_SYSTEM_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Команда запуска
CMD ["python", "-m", "skin_system.cli", "serve"] 