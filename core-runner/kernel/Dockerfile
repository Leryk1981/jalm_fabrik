# Многостадийная сборка для JALM Core Runner
# Этап 1: Базовый образ для сборки
FROM python:3.11-alpine AS builder

# Установка зависимостей для сборки
RUN apk add --no-cache \
    build-base \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    && rm -rf /var/cache/apk/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.11-alpine AS runtime

# Установка runtime зависимостей
RUN apk add --no-cache \
    musl \
    libffi \
    openssl \
    && rm -rf /var/cache/apk/*

# Копирование виртуального окружения из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создание пользователя для безопасности
RUN addgroup -g 1000 jalm && \
    adduser -D -s /bin/sh -u 1000 -G jalm jalm

# Создание директорий
RUN mkdir -p /app /data /tmp/jalm && \
    chown -R jalm:jalm /app /data /tmp/jalm

# Копирование исходного кода
COPY --chown=jalm:jalm kernel/ /app/kernel/
COPY --chown=jalm:jalm cfg/ /app/cfg/
COPY --chown=jalm:jalm scheduler/ /app/scheduler/
COPY --chown=jalm:jalm registry-proxy/ /app/registry-proxy/
COPY --chown=jalm:jalm api/ /app/api/
COPY --chown=jalm:jalm state-store/ /app/state-store/

# Установка рабочей директории
WORKDIR /app

# Переключение на пользователя jalm
USER jalm

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV JALM_ENV=production

# Открытие порта
EXPOSE 8888

# Точка входа
ENTRYPOINT ["python", "kernel/src/main.py"] 