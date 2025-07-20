"""
CLI для Context7 Helper - командная строка для управления поиском кода

Обеспечивает удобный интерфейс для запуска поиска, генерации кандидатов
и интеграции с JALM Full Stack.
"""

import argparse
import logging
import json
import sys
from pathlib import Path
from typing import Optional
from .integration import IntegrationManager
import click

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False):
    """Настройка логирования"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(
        description="Context7 Helper - автоматический поиск кода для JALM Full Stack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  context7 search --query "booking system" --top-k 5
  context7 generate --research-dir research --top-k 3
  context7 status
  context7 cleanup --days 7
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда search
    search_parser = subparsers.add_parser('search', help='Поиск кода по запросу')
    search_parser.add_argument('--query', required=True, help='Поисковый запрос')
    search_parser.add_argument('--language', default='python', help='Язык программирования')
    search_parser.add_argument('--top-k', type=int, default=5, help='Количество результатов')
    search_parser.add_argument('--output', help='Файл для сохранения результатов')
    
    # Команда generate
    generate_parser = subparsers.add_parser('generate', help='Генерация кандидатов из Research Layer')
    generate_parser.add_argument('--research-dir', default='research', help='Директория с данными исследований')
    generate_parser.add_argument('--top-k', type=int, default=3, help='Количество результатов на запрос')
    generate_parser.add_argument('--output-dir', default='tool_candidates', help='Директория для сохранения')
    
    # Команда status
    status_parser = subparsers.add_parser('status', help='Статус Context7 Helper')
    
    # Команда cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Очистка старых кандидатов')
    cleanup_parser.add_argument('--days', type=int, default=7, help='Количество дней для хранения')
    
    # Команда test
    test_parser = subparsers.add_parser('test', help='Тестирование функциональности')
    test_parser.add_argument('--verbose', action='store_true', help='Подробный вывод')
    
    # Общие аргументы
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробный вывод')
    parser.add_argument('--api-key', help='API ключ для Context7')
    
    args = parser.parse_args()
    
    # Настройка логирования
    setup_logging(args.verbose)
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Создание менеджера интеграции
        manager = IntegrationManager(api_key=args.api_key)
        
        if args.command == 'search':
            return handle_search(manager, args)
        elif args.command == 'generate':
            return handle_generate(manager, args)
        elif args.command == 'status':
            return handle_status(manager, args)
        elif args.command == 'cleanup':
            return handle_cleanup(manager, args)
        elif args.command == 'test':
            return handle_test(manager, args)
        else:
            logger.error(f"Неизвестная команда: {args.command}")
            return 1
            
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
        return 1

def handle_search(manager: IntegrationManager, args) -> int:
    """Обработка команды search"""
    logger.info(f"Поиск кода: {args.query}")
    
    try:
        from .searcher import SearchQuery
        
        # Создаем поисковый запрос
        query = SearchQuery(
            action_name=args.query,
            description=args.query,
            language=args.language
        )
        
        # Выполняем поиск
        results = manager.searcher.search(query, args.top_k)
        
        if not results:
            logger.warning("Не найдено результатов")
            return 0
        
        # Выводим результаты
        click.echo(f"\nНайдено {len(results)} результатов:\n")
        
        for i, result in enumerate(results, 1):
            click.echo(f"{i}. {result.function_name}")
            click.echo(f"   Репозиторий: {result.repo}")
            click.echo(f"   Файл: {result.source_file}")
            click.echo(f"   Скор: {result.score:.3f}")
            click.echo(f"   Звезды: {result.stars}")
            click.echo(f"   Лицензия: {result.license}")
            click.echo(f"   Пример: {result.example[:100]}...")
            click.echo()
        
        # Сохраняем в файл если указан
        if args.output:
            import json
            output_data = []
            for result in results:
                output_data.append({
                    "function_name": result.function_name,
                    "repo": result.repo,
                    "file_path": result.source_file,
                    "score": result.score,
                    "stars": result.stars,
                    "license": result.license,
                    "example": result.example
                })
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            click.echo(f"Результаты сохранены в {args.output}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        return 1

def handle_generate(manager: IntegrationManager, args) -> int:
    """Обработка команды generate"""
    logger.info(f"Генерация кандидатов из {args.research_dir}")
    
    try:
        # Запускаем полный пайплайн
        result = manager.run_full_pipeline(args.research_dir, args.top_k)
        
        if not result["success"]:
            logger.error(f"Ошибка в пайплайне: {result.get('error', 'Неизвестная ошибка')}")
            return 1
        
        # Выводим отчет
        click.echo(f"\nПайплайн завершен успешно!")
        click.echo(f"Обработано действий: {result['processed_actions']}")
        click.echo(f"Поисковых запросов: {result['search_queries']}")
        click.echo(f"Создано кандидатов: {result['generated_candidates']}")
        
        if result['categories']:
            click.echo(f"\nПо категориям:")
            for category, count in result['categories'].items():
                click.echo(f"   {category}: {count}")
        
        click.echo(f"\nСохранено файлов:")
        for file_type, paths in result['saved_files'].items():
            if isinstance(paths, list):
                click.echo(f"   {file_type}: {len(paths)} файлов")
            else:
                click.echo(f"   {file_type}: {paths}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Ошибка при генерации: {e}")
        return 1

def handle_status(manager: IntegrationManager, args) -> int:
    """Обработка команды status"""
    logger.info("Получение статуса Context7 Helper")
    
    try:
        status = manager.get_status()
        
        print(f"\nСтатус Context7 Helper:")
        print(f"Context7 API: {'Доступен' if status['context7_api'] else 'Недоступен'}")
        print(f"Директория вывода: {status['output_directory']}")
        print(f"Директория существует: {'Да' if status['output_directory_exists'] else 'Нет'}")
        print(f"Всего кандидатов: {status['candidates_count']}")
        
        if status['categories']:
            print(f"\nКандидаты по категориям:")
            for category, count in status['categories'].items():
                print(f"   {category}: {count}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Ошибка при получении статуса: {e}")
        return 1

def handle_cleanup(manager: IntegrationManager, args) -> int:
    """Обработка команды cleanup"""
    logger.info(f"Очистка старых кандидатов (старше {args.days} дней)")
    
    try:
        deleted_count = manager.cleanup_old_candidates(args.days)
        
        print(f"\n🧹 Очистка завершена!")
        print(f"🗑️  Удалено файлов: {deleted_count}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Ошибка при очистке: {e}")
        return 1

def handle_test(manager: IntegrationManager, args) -> int:
    """Обработка команды test"""
    logger.info("Тестирование функциональности Context7 Helper")
    
    try:
        # Тест 1: Проверка статуса
        print("1. Тест статуса...")
        status = manager.get_status()
        print(f"   Статус получен: {status['context7_api']}")
        
        # Тест 2: Проверка поиска
        print("2. Тест поиска...")
        from .searcher import SearchQuery
        query = SearchQuery(
            action_name="test_search",
            description="Test search functionality",
            language="python"
        )
        results = manager.searcher.search(query, 1)
        print(f"   Поиск выполнен: {len(results)} результатов")
        
        # Тест 3: Проверка генератора
        print("3. Тест генератора...")
        if results:
            candidate = manager.generator.create_candidate(results[0], query)
            print(f"   Кандидат создан: {candidate.name}")
        else:
            print("   Кандидат не создан (нет результатов поиска)")
        
        # Тест 4: Проверка интеграции
        print("4. Тест интеграции...")
        integration_status = manager.get_status()
        print(f"   Интеграция работает: {integration_status['output_directory_exists']}")
        
        print("\nВсе тесты завершены!")
        return 0
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 