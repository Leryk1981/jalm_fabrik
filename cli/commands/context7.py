"""
Context7 Helper команды для CLI JALM Full Stack

Интеграция Context7 Helper с основным CLI для автоматического поиска кода
и генерации tool_candidates.
"""

import click
import logging
import sys
from pathlib import Path

# Добавляем путь к context7_helper
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "context7_helper"))

try:
    from context7_helper.integration import IntegrationManager
    from context7_helper.searcher import SearchQuery
    CONTEXT7_AVAILABLE = True
except ImportError:
    CONTEXT7_AVAILABLE = False

logger = logging.getLogger(__name__)

@click.group()
def context7():
    """Context7 Helper - автоматический поиск кода"""
    if not CONTEXT7_AVAILABLE:
        click.echo("❌ Context7 Helper не установлен. Установите модуль context7_helper.")
        sys.exit(1)

@context7.command()
@click.option('--query', required=True, help='Поисковый запрос')
@click.option('--language', default='python', help='Язык программирования')
@click.option('--top-k', default=5, help='Количество результатов')
@click.option('--output', help='Файл для сохранения результатов')
@click.option('--api-key', help='API ключ для Context7')
def search(query, language, top_k, output, api_key):
    """Поиск кода по запросу"""
    try:
        manager = IntegrationManager(api_key=api_key)
        
        # Создаем поисковый запрос
        search_query = SearchQuery(
            action_name=query,
            description=query,
            language=language
        )
        
        # Выполняем поиск
        results = manager.searcher.search(search_query, top_k)
        
        if not results:
            click.echo("❌ Не найдено результатов")
            return
        
        # Выводим результаты
        click.echo(f"\n✅ Найдено {len(results)} результатов:\n")
        
        for i, result in enumerate(results, 1):
            click.echo(f"{i}. {result.function_name}")
            click.echo(f"   📦 Репозиторий: {result.repo}")
            click.echo(f"   📁 Файл: {result.source_file}")
            click.echo(f"   ⭐ Скор: {result.score:.3f}")
            click.echo(f"   🌟 Звезды: {result.stars}")
            click.echo(f"   📄 Лицензия: {result.license}")
            click.echo(f"   💻 Пример: {result.example[:100]}...")
            click.echo()
        
        # Сохраняем в файл если указан
        if output:
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
            
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            click.echo(f"💾 Результаты сохранены в {output}")
        
    except Exception as e:
        click.echo(f"❌ Ошибка при поиске: {e}")
        logger.error(f"Ошибка при поиске: {e}")

@context7.command()
@click.option('--research-dir', default='research', help='Директория с данными исследований')
@click.option('--top-k', default=3, help='Количество результатов на запрос')
@click.option('--output-dir', default='tool_candidates', help='Директория для сохранения')
@click.option('--api-key', help='API ключ для Context7')
def generate(research_dir, top_k, output_dir, api_key):
    """Генерация кандидатов из Research Layer"""
    try:
        manager = IntegrationManager(api_key=api_key, output_dir=output_dir)
        
        # Запускаем полный пайплайн
        result = manager.run_full_pipeline(research_dir, top_k)
        
        if not result["success"]:
            click.echo(f"❌ Ошибка в пайплайне: {result.get('error', 'Неизвестная ошибка')}")
            return
        
        # Выводим отчет
        click.echo(f"\n✅ Пайплайн завершен успешно!")
        click.echo(f"📊 Обработано действий: {result['processed_actions']}")
        click.echo(f"🔍 Поисковых запросов: {result['search_queries']}")
        click.echo(f"🎯 Создано кандидатов: {result['generated_candidates']}")
        
        if result['categories']:
            click.echo(f"\n📂 По категориям:")
            for category, count in result['categories'].items():
                click.echo(f"   {category}: {count}")
        
        click.echo(f"\n💾 Сохранено файлов:")
        for file_type, paths in result['saved_files'].items():
            if isinstance(paths, list):
                click.echo(f"   {file_type}: {len(paths)} файлов")
            else:
                click.echo(f"   {file_type}: {paths}")
        
    except Exception as e:
        click.echo(f"❌ Ошибка при генерации: {e}")
        logger.error(f"Ошибка при генерации: {e}")

@context7.command()
@click.option('--api-key', help='API ключ для Context7')
def status(api_key):
    """Статус Context7 Helper"""
    try:
        manager = IntegrationManager(api_key=api_key)
        status = manager.get_status()
        
        click.echo(f"\n📊 Статус Context7 Helper:")
        click.echo(f"🔌 Context7 API: {'✅ Доступен' if status['context7_api'] else '❌ Недоступен'}")
        click.echo(f"📁 Директория вывода: {status['output_directory']}")
        click.echo(f"📂 Директория существует: {'✅ Да' if status['output_directory_exists'] else '❌ Нет'}")
        click.echo(f"🎯 Всего кандидатов: {status['candidates_count']}")
        
        if status['categories']:
            click.echo(f"\n📂 Кандидаты по категориям:")
            for category, count in status['categories'].items():
                click.echo(f"   {category}: {count}")
        
    except Exception as e:
        click.echo(f"❌ Ошибка при получении статуса: {e}")
        logger.error(f"Ошибка при получении статуса: {e}")

@context7.command()
@click.option('--days', default=7, help='Количество дней для хранения')
@click.option('--api-key', help='API ключ для Context7')
def cleanup(days, api_key):
    """Очистка старых кандидатов"""
    try:
        manager = IntegrationManager(api_key=api_key)
        deleted_count = manager.cleanup_old_candidates(days)
        
        click.echo(f"\n🧹 Очистка завершена!")
        click.echo(f"🗑️  Удалено файлов: {deleted_count}")
        
    except Exception as e:
        click.echo(f"❌ Ошибка при очистке: {e}")
        logger.error(f"Ошибка при очистке: {e}")

@context7.command()
@click.option('--api-key', help='API ключ для Context7')
def test(api_key):
    """Тестирование Context7 Helper"""
    try:
        manager = IntegrationManager(api_key=api_key)
        
        # Проверяем статус
        status = manager.get_status()
        
        if not status['context7_api']:
            click.echo("❌ Context7 API недоступен")
            return
        
        # Тестируем поиск
        from context7_helper.searcher import SearchQuery
        
        test_query = SearchQuery(
            action_name="test_search",
            description="Test search functionality",
            language="python"
        )
        
        results = manager.searcher.search(test_query, top_k=1)
        
        if results:
            click.echo("✅ Context7 Helper работает корректно")
            click.echo(f"📊 Найдено тестовых результатов: {len(results)}")
        else:
            click.echo("⚠️  Context7 Helper работает, но не найдено результатов")
        
    except Exception as e:
        click.echo(f"❌ Ошибка при тестировании: {e}")
        logger.error(f"Ошибка при тестировании: {e}") 