# Core Runner Dockerfile
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Экспорт порта
EXPOSE 8888

# Команда запуска
CMD ["python", "api/main.py"] 