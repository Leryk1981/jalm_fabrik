#!/usr/bin/env python3
"""
JALM Full Stack CLI - командная строка для управления JALM Full Stack

Основной модуль CLI с командами для управления всеми компонентами системы.
"""

import click
import logging
import sys
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Импорт команд
from .commands import up, down, status, logs, test, deploy, research

# Попытка импорта context7 (может быть не установлен)
try:
    from .commands import context7
    CONTEXT7_AVAILABLE = True
except ImportError:
    CONTEXT7_AVAILABLE = False

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🚀 JALM Full Stack CLI
    
    Командная строка для управления JALM Full Stack - полной экосистемой
    для создания SaaS-приложений с LLM-ядром.
    
    Основные команды:
    • up/down - управление сервисами
    • status/logs - мониторинг
    • test - тестирование
    • deploy - развертывание
    • research - аналитика
    • context7 - поиск кода (если доступен)
    """
    pass

# Регистрация команд
cli.add_command(up.up)
cli.add_command(down.down)
cli.add_command(status.status)
cli.add_command(logs.logs)
cli.add_command(test.test)
cli.add_command(deploy.deploy)
cli.add_command(research.research)

# Регистрация context7 если доступен
if CONTEXT7_AVAILABLE:
    cli.add_command(context7.context7)

if __name__ == '__main__':
    cli() 