FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директорий для данных
RUN mkdir -p /app/data /app/patterns /app/results

# Переменные окружения
ENV PYTHONPATH=/app
ENV RESEARCH_DATA_DIR=/app/data
ENV RESEARCH_PATTERNS_DIR=/app/patterns
ENV RESEARCH_RESULTS_DIR=/app/results

# Точка входа для автоматизации
ENTRYPOINT ["python", "main.py"] 