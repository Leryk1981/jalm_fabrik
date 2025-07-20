# CLI Dockerfile для JALM Full Stack
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Установка CLI как пакета
RUN pip install -e .

# Переменные окружения
ENV PYTHONPATH=/app
ENV JALM_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import cli; print('CLI healthy')" || exit 1

# Точка входа
ENTRYPOINT ["python", "-m", "cli.main"]
CMD ["--help"] 