"""
Команда research для CLI - интеграция с Research Layer
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Добавляем путь к research модулю
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from research import DataCollector, PatternAnalyzer, ResearchConfig
except ImportError as e:
    print(f"❌ Ошибка импорта Research Layer: {e}")
    print("Убедитесь, что модуль research установлен")
    sys.exit(1)

logger = logging.getLogger(__name__)


def research_collect(args: argparse.Namespace) -> int:
    """
    Сбор данных через Research Layer
    """
    try:
        logger.info("🔍 Запуск сбора данных через Research Layer...")
        
        # Создание конфигурации
        config = ResearchConfig()
        
        # Создание сборщика
        collector = DataCollector(config)
        
        # Сбор действий
        logger.info("📊 Собираем действия...")
        actions = collector.collect_actions()
        logger.info(f"✅ Собрано {len(actions)} действий")
        
        # Экспорт действий
        actions_file = collector.export(actions, args.format, "raw_actions.csv")
        logger.info(f"📁 Действия экспортированы в {actions_file}")
        
        # Сбор паттернов
        logger.info("🎯 Собираем паттерны...")
        patterns = collector.collect_patterns()
        logger.info(f"✅ Собрано {len(patterns)} паттернов")
        
        # Экспорт паттернов
        patterns_file = collector.export(patterns, args.format, "raw_patterns.csv")
        logger.info(f"📁 Паттерны экспортированы в {patterns_file}")
        
        logger.info("🎉 Сбор данных завершен успешно!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка сбора данных: {e}")
        return 1


def research_analyze(args: argparse.Namespace) -> int:
    """
    Анализ паттернов через Research Layer
    """
    try:
        logger.info("🔍 Запуск анализа паттернов...")
        
        # Создание конфигурации
        config = ResearchConfig()
        
        # Проверка наличия данных
        patterns_file = config.get_data_path("raw_patterns.csv")
        if not patterns_file.exists():
            logger.error("❌ Файл с паттернами не найден. Сначала запустите 'jalm research collect'")
            return 1
        
        # Создание анализатора
        analyzer = PatternAnalyzer(config)
        
        # Загрузка данных
        logger.info("📂 Загружаем данные для анализа...")
        if args.input_file:
            input_path = Path(args.input_file)
        else:
            input_path = patterns_file
            
        if not input_path.exists():
            logger.error(f"❌ Файл {input_path} не найден")
            return 1
        
        # Загрузка в зависимости от формата
        if input_path.suffix == '.json':
            import json
            with open(input_path, 'r', encoding='utf-8') as f:
                patterns = json.load(f)
        elif input_path.suffix == '.csv':
            import pandas as pd
            df = pd.read_csv(input_path)
            patterns = df.to_dict('records')
        else:
            logger.error(f"❌ Неподдерживаемый формат файла: {input_path.suffix}")
            return 1
        
        logger.info(f"📊 Загружено {len(patterns)} паттернов для анализа")
        
        # Анализ паттернов
        logger.info("🔬 Анализируем паттерны...")
        analysis = analyzer.analyze_patterns(patterns)
        logger.info("✅ Анализ паттернов завершен")
        
        # Группировка паттернов
        logger.info("📂 Группируем паттерны...")
        groups = analyzer.group_patterns(patterns)
        logger.info(f"✅ Паттерны сгруппированы в {len(groups)} категорий")
        
        # Создание артефактов для JALM
        logger.info("🎯 Создаем артефакты для JALM...")
        artifacts = analyzer.create_jalm_artifacts(patterns)
        
        for artifact_type, filepath in artifacts.items():
            logger.info(f"📁 Создан артефакт {artifact_type}: {filepath}")
        
        logger.info("🎉 Анализ завершен успешно!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка анализа: {e}")
        return 1


def research_integrate(args: argparse.Namespace) -> int:
    """
    Интеграция с JALM компонентами
    """
    try:
        logger.info("🔗 Запуск интеграции с JALM компонентами...")
        
        # Создание конфигурации
        config = ResearchConfig()
        
        # Проверка наличия артефактов
        artifacts_dir = config.patterns_dir
        required_files = [
            "jalm_templates.json",
            "jalm_functions.json", 
            "pattern_analysis.json",
            "pattern_groups.json"
        ]
        
        missing_files = []
        for file in required_files:
            if not (artifacts_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"❌ Отсутствуют артефакты: {', '.join(missing_files)}")
            logger.info("💡 Сначала запустите 'jalm research analyze'")
            return 1
        
        logger.info("✅ Все необходимые артефакты найдены")
        
        # Интеграция с Tool Catalog
        logger.info("📚 Интегрируем с Tool Catalog...")
        _integrate_with_tool_catalog(config)
        
        # Интеграция с Shablon Spec
        logger.info("📋 Интегрируем с Shablon Spec...")
        _integrate_with_shablon_spec(config)
        
        # Интеграция с Tula Registry
        logger.info("🔧 Интегрируем с Tula Registry...")
        _integrate_with_tula_registry(config)
        
        logger.info("🎉 Интеграция с JALM компонентами завершена!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка интеграции: {e}")
        return 1


def research_status(args: argparse.Namespace) -> int:
    """
    Статус Research Layer
    """
    try:
        logger.info("📊 Статус Research Layer:")
        
        # Создание конфигурации
        config = ResearchConfig()
        
        # Проверка директорий
        patterns_dir = config.patterns_dir
        logger.info(f"📁 Директория паттернов: {patterns_dir}")
        logger.info(f"   Существует: {'✅' if patterns_dir.exists() else '❌'}")
        
        # Проверка файлов данных
        logger.info("📄 Файлы данных:")
        data_files = [
            "raw_actions.csv",
            "raw_patterns.csv", 
            "pattern_analysis.json",
            "pattern_groups.json",
            "jalm_templates.json",
            "jalm_functions.json"
        ]
        
        for file in data_files:
            file_path = patterns_dir / file
            status = "✅" if file_path.exists() else "❌"
            size = f"({file_path.stat().st_size} bytes)" if file_path.exists() else ""
            logger.info(f"   {file}: {status} {size}")
        
        # Проверка зависимостей
        logger.info("🔧 Зависимости:")
        try:
            import requests, yaml, pandas
            logger.info("   ✅ Все зависимости установлены")
        except ImportError as e:
            logger.info(f"   ❌ Отсутствуют зависимости: {e}")
        
        # Статистика
        if (patterns_dir / "raw_patterns.csv").exists():
            import pandas as pd
            df = pd.read_csv(patterns_dir / "raw_patterns.csv")
            logger.info(f"📊 Статистика: {len(df)} паттернов")
        
        logger.info("✅ Статус проверен")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Ошибка проверки статуса: {e}")
        return 1


def _integrate_with_tool_catalog(config: ResearchConfig) -> None:
    """Интеграция с Tool Catalog"""
    try:
        from research.integration import JALMIntegration
        integration = JALMIntegration()
        success = integration.integrate_with_tool_catalog()
        if success:
            logger.info("   📚 Tool Catalog интеграция завершена")
        else:
            logger.error("   ❌ Ошибка интеграции с Tool Catalog")
    except Exception as e:
        logger.error(f"   ❌ Ошибка интеграции с Tool Catalog: {e}")


def _integrate_with_shablon_spec(config: ResearchConfig) -> None:
    """Интеграция с Shablon Spec"""
    try:
        from research.integration import JALMIntegration
        integration = JALMIntegration()
        success = integration.integrate_with_shablon_spec()
        if success:
            logger.info("   📋 Shablon Spec интеграция завершена")
        else:
            logger.error("   ❌ Ошибка интеграции с Shablon Spec")
    except Exception as e:
        logger.error(f"   ❌ Ошибка интеграции с Shablon Spec: {e}")


def _integrate_with_tula_registry(config: ResearchConfig) -> None:
    """Интеграция с Tula Registry"""
    try:
        from research.integration import JALMIntegration
        integration = JALMIntegration()
        success = integration.integrate_with_tula_registry()
        if success:
            logger.info("   🔧 Tula Registry интеграция завершена")
        else:
            logger.error("   ❌ Ошибка интеграции с Tula Registry")
    except Exception as e:
        logger.error(f"   ❌ Ошибка интеграции с Tula Registry: {e}")


def research_docker_build(args: argparse.Namespace) -> int:
    """Собрать Docker образ для Research Layer"""
    try:
        import subprocess
        
        logger.info("🐳 Сборка Docker образа...")
        result = subprocess.run(
            ["docker", "build", "-t", "jalm-research", "."],
            cwd="research",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Docker образ собран успешно")
            return 0
        else:
            logger.error(f"❌ Ошибка сборки: {result.stderr}")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return 1


def research_docker_up(args: argparse.Namespace) -> int:
    """Запустить Research Layer в Docker"""
    try:
        import subprocess
        
        logger.info("🐳 Запуск Research Layer в Docker...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd="research",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Research Layer запущен в Docker")
            return 0
        else:
            logger.error(f"❌ Ошибка запуска: {result.stderr}")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return 1


def research_docker_down(args: argparse.Namespace) -> int:
    """Остановить Research Layer в Docker"""
    try:
        import subprocess
        
        logger.info("🐳 Остановка Research Layer...")
        result = subprocess.run(
            ["docker-compose", "down"],
            cwd="research",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Research Layer остановлен")
            return 0
        else:
            logger.error(f"❌ Ошибка остановки: {result.stderr}")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return 1


def research_docker_logs(args: argparse.Namespace) -> int:
    """Показать логи Research Layer"""
    try:
        import subprocess
        
        logger.info("🐳 Просмотр логов...")
        subprocess.run(
            ["docker-compose", "logs", "-f"],
            cwd="research"
        )
        return 0
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return 1


def add_research_parser(subparsers: argparse._SubParsersAction) -> None:
    """
    Добавить парсер для команды research
    """
    research_parser = subparsers.add_parser(
        'research',
        help='Управление Research Layer'
    )
    
    research_subparsers = research_parser.add_subparsers(
        dest='research_command',
        help='Команды Research Layer'
    )
    
    # Команда collect
    collect_parser = research_subparsers.add_parser(
        'collect',
        help='Сбор данных через Research Layer'
    )
    collect_parser.add_argument(
        '--format',
        choices=['csv', 'json', 'yaml'],
        default='csv',
        help='Формат выходных файлов'
    )
    collect_parser.set_defaults(func=research_collect)
    
    # Команда analyze
    analyze_parser = research_subparsers.add_parser(
        'analyze',
        help='Анализ паттернов через Research Layer'
    )
    analyze_parser.add_argument(
        '--input-file',
        type=str,
        help='Путь к файлу с данными для анализа'
    )
    analyze_parser.add_argument(
        '--format',
        choices=['csv', 'json', 'yaml'],
        default='json',
        help='Формат выходных файлов'
    )
    analyze_parser.set_defaults(func=research_analyze)
    
    # Команда integrate
    integrate_parser = research_subparsers.add_parser(
        'integrate',
        help='Интеграция с JALM компонентами'
    )
    integrate_parser.set_defaults(func=research_integrate)
    
    # Команда status
    status_parser = research_subparsers.add_parser(
        'status',
        help='Статус Research Layer'
    )
    status_parser.set_defaults(func=research_status)
    
    # Команда docker-build
    docker_build_parser = research_subparsers.add_parser(
        'docker-build',
        help='Собрать Docker образ для Research Layer'
    )
    docker_build_parser.set_defaults(func=research_docker_build)
    
    # Команда docker-up
    docker_up_parser = research_subparsers.add_parser(
        'docker-up',
        help='Запустить Research Layer в Docker'
    )
    docker_up_parser.set_defaults(func=research_docker_up)
    
    # Команда docker-down
    docker_down_parser = research_subparsers.add_parser(
        'docker-down',
        help='Остановить Research Layer в Docker'
    )
    docker_down_parser.set_defaults(func=research_docker_down)
    
    # Команда docker-logs
    docker_logs_parser = research_subparsers.add_parser(
        'docker-logs',
        help='Показать логи Research Layer'
    )
    docker_logs_parser.set_defaults(func=research_docker_logs) 

# Click команда для совместимости с CLI
import click

@click.group()
def research():
    """Research Layer - управление аналитикой и исследованиями"""
    pass

@research.command()
@click.option('--format', default='csv', type=click.Choice(['csv', 'json', 'yaml']), help='Формат выходных файлов')
def collect(format):
    """Сбор данных через Research Layer"""
    import argparse
    args = argparse.Namespace()
    args.format = format
    return research_collect(args)

@research.command()
@click.option('--input-file', help='Путь к файлу с данными для анализа')
@click.option('--format', default='json', type=click.Choice(['csv', 'json', 'yaml']), help='Формат выходных файлов')
def analyze(input_file, format):
    """Анализ паттернов через Research Layer"""
    import argparse
    args = argparse.Namespace()
    args.input_file = input_file
    args.format = format
    return research_analyze(args)

@research.command()
def integrate():
    """Интеграция с JALM компонентами"""
    import argparse
    args = argparse.Namespace()
    return research_integrate(args)

@research.command()
def status():
    """Статус Research Layer"""
    import argparse
    args = argparse.Namespace()
    return research_status(args)

@research.command()
def docker_build():
    """Собрать Docker образ для Research Layer"""
    import argparse
    args = argparse.Namespace()
    return research_docker_build(args)

@research.command()
def docker_up():
    """Запустить Research Layer в Docker"""
    import argparse
    args = argparse.Namespace()
    return research_docker_up(args)

@research.command()
def docker_down():
    """Остановить Research Layer в Docker"""
    import argparse
    args = argparse.Namespace()
    return research_docker_down(args)

@research.command()
def docker_logs():
    """Показать логи Research Layer"""
    import argparse
    args = argparse.Namespace()
    return research_docker_logs(args) 