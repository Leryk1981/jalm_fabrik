#!/usr/bin/env python3
"""
JALM CLI - Главный модуль командной строки
"""

import argparse
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.core.config import Config
from cli.utils.logger import setup_logger
from cli.commands import up, down, status, logs, test, deploy
from cli.commands import research

def create_parser():
    """Создает парсер аргументов командной строки"""
    parser = argparse.ArgumentParser(
        prog='jalm',
        description='JALM Full Stack CLI - управление экосистемой',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  jalm up core-runner          # Запуск core-runner
  jalm up all                  # Запуск всех сервисов
  jalm status                  # Статус всех сервисов
  jalm logs core-runner        # Логи core-runner
  jalm test                    # Запуск всех тестов
  jalm deploy booking_light    # Деплой шаблона
        """
    )
    
    # Основные команды
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда up
    up_parser = subparsers.add_parser('up', help='Запуск сервисов')
    up_parser.add_argument('service', nargs='?', default='all', 
                          choices=['all', 'core-runner', 'tula-spec', 'shablon-spec'],
                          help='Сервис для запуска')
    up_parser.add_argument('--detach', '-d', action='store_true',
                          help='Запуск в фоновом режиме')
    
    # Команда down
    down_parser = subparsers.add_parser('down', help='Остановка сервисов')
    down_parser.add_argument('service', nargs='?', default='all',
                            choices=['all', 'core-runner', 'tula-spec', 'shablon-spec'],
                            help='Сервис для остановки')
    
    # Команда status
    status_parser = subparsers.add_parser('status', help='Статус сервисов')
    status_parser.add_argument('--verbose', '-v', action='store_true',
                              help='Подробный вывод')
    
    # Команда logs
    logs_parser = subparsers.add_parser('logs', help='Просмотр логов')
    logs_parser.add_argument('service', 
                            choices=['core-runner', 'tula-spec', 'shablon-spec', 'all'],
                            help='Сервис для просмотра логов')
    logs_parser.add_argument('--follow', '-f', action='store_true',
                            help='Следовать за логами')
    logs_parser.add_argument('--lines', '-n', type=int, default=50,
                            help='Количество строк логов')
    
    # Команда test
    test_parser = subparsers.add_parser('test', help='Запуск тестов')
    test_parser.add_argument('service', nargs='?', default='all',
                            choices=['all', 'core-runner', 'tula-spec', 'shablon-spec'],
                            help='Сервис для тестирования')
    test_parser.add_argument('--verbose', '-v', action='store_true',
                            help='Подробный вывод')
    
    # Команда deploy
    deploy_parser = subparsers.add_parser('deploy', help='Деплой шаблона')
    deploy_parser.add_argument('template', help='Название шаблона для деплоя')
    deploy_parser.add_argument('--name', '-n', help='Имя деплоя')
    deploy_parser.add_argument('--config', '-c', help='Путь к конфигурации')
    
    # Добавляем команды research
    research.add_research_parser(subparsers)
    
    # Глобальные опции
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--debug', action='store_true', help='Режим отладки')
    parser.add_argument('--config-file', help='Путь к файлу конфигурации')
    
    return parser

def main():
    """Главная функция CLI"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Настройка логирования
    logger = setup_logger(debug=args.debug)
    
    # Загрузка конфигурации
    config = Config(config_file=args.config_file)
    
    try:
        if args.command == 'up':
            up.run(args.service, args.detach, config, logger)
        elif args.command == 'down':
            down.run(args.service, config, logger)
        elif args.command == 'status':
            status.run(args.verbose, config, logger)
        elif args.command == 'logs':
            logs.run(args.service, args.follow, args.lines, config, logger)
        elif args.command == 'test':
            test.run(args.service, args.verbose, config, logger)
        elif args.command == 'deploy':
            deploy.run(args.template, args.name, args.config, config, logger)
        elif args.command == 'research':
            if hasattr(args, 'func'):
                args.func(args)
            else:
                print("Используйте: jalm research --help для справки")
                sys.exit(1)
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Операция прервана пользователем")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 