# Barbershop Plugin - Готовый Docker образ
# Включает все компоненты JALM Full Stack

# Многостадийная сборка
FROM python:3.11-alpine AS builder

# Установка зависимостей для сборки
RUN apk add --no-cache \
    build-base \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    git \
    && rm -rf /var/cache/apk/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.11-alpine AS runtime

# Установка runtime зависимостей
RUN apk add --no-cache \
    musl \
    libffi \
    openssl \
    curl \
    && rm -rf /var/cache/apk/*

# Копирование виртуального окружения из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создание пользователя для безопасности
RUN addgroup -g 1000 jalm && \
    adduser -D -s /bin/sh -u 1000 -G jalm jalm

# Создание директорий
RUN mkdir -p /app /data /logs /tmp/jalm /templates && \
    chown -R jalm:jalm /app /data /logs /tmp/jalm /templates

# Копирование исходного кода
COPY --chown=jalm:jalm . /app/

# Установка рабочей директории
WORKDIR /app

# Переключение на пользователя jalm
USER jalm

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV JALM_ENV=production
ENV PORT=8000

# Открытие портов
EXPOSE 8000 8001 8002

# Скрипт запуска всех сервисов
COPY --chown=jalm:jalm docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Точка входа
ENTRYPOINT ["/app/docker-entrypoint.sh"]
