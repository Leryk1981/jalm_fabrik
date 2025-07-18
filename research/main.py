#!/usr/bin/env python3
"""
Основной файл для запуска Research Layer
"""

import argparse
import logging
import sys
from pathlib import Path

from research import DataCollector, PatternAnalyzer, ResearchConfig


def setup_logging(level: str = "INFO"):
    """Настройка логирования"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('research.log')
        ]
    )


def collect_data(config: ResearchConfig, output_format: str = "json"):
    """Сбор данных из всех источников"""
    logging.info("Начинаем сбор данных...")
    
    collector = DataCollector(config)
    
    # Сбор действий
    logging.info("Собираем действия...")
    actions = collector.collect_actions()
    logging.info(f"Собрано {len(actions)} действий")
    
    # Экспорт действий
    actions_file = collector.export(actions, output_format, "raw_actions.csv")
    logging.info(f"Действия экспортированы в {actions_file}")
    
    # Сбор паттернов
    logging.info("Собираем паттерны...")
    patterns = collector.collect_patterns()
    logging.info(f"Собрано {len(patterns)} паттернов")
    
    # Экспорт паттернов
    patterns_file = collector.export(patterns, output_format, "raw_patterns.csv")
    logging.info(f"Паттерны экспортированы в {patterns_file}")
    
    return actions, patterns


def analyze_patterns(config: ResearchConfig, patterns: list):
    """Анализ паттернов"""
    logging.info("Начинаем анализ паттернов...")
    
    analyzer = PatternAnalyzer(config)
    
    # Анализ паттернов
    analysis = analyzer.analyze_patterns(patterns)
    logging.info("Анализ паттернов завершен")
    
    # Группировка паттернов
    groups = analyzer.group_patterns(patterns)
    logging.info(f"Паттерны сгруппированы в {len(groups)} категорий")
    
    # Создание артефактов для JALM
    logging.info("Создаем артефакты для JALM...")
    artifacts = analyzer.create_jalm_artifacts(patterns)
    
    for artifact_type, filepath in artifacts.items():
        logging.info(f"Создан артефакт {artifact_type}: {filepath}")
    
    return analysis, groups, artifacts


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Research Layer - сбор и анализ данных")
    parser.add_argument(
        "--config", 
        type=str, 
        help="Путь к файлу конфигурации"
    )
    parser.add_argument(
        "--output-format", 
        choices=["csv", "json", "yaml"], 
        default="json",
        help="Формат выходных файлов"
    )
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
        default="INFO",
        help="Уровень логирования"
    )
    parser.add_argument(
        "--collect-only", 
        action="store_true",
        help="Только сбор данных, без анализа"
    )
    parser.add_argument(
        "--analyze-only", 
        type=str,
        help="Только анализ данных из указанного файла"
    )
    
    args = parser.parse_args()
    
    # Настройка логирования
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Загрузка конфигурации
        config = ResearchConfig()
        if args.config:
            # TODO: Реализовать загрузку из файла
            logger.warning("Загрузка конфигурации из файла не реализована")
        
        if not config.validate():
            logger.error("Ошибка валидации конфигурации")
            sys.exit(1)
        
        if args.analyze_only:
            # Только анализ существующих данных
            logger.info(f"Анализируем данные из {args.analyze_only}")
            
            # Загрузка данных из файла
            filepath = Path(args.analyze_only)
            if not filepath.exists():
                logger.error(f"Файл {filepath} не найден")
                sys.exit(1)
            
            with open(filepath, 'r') as f:
                if filepath.suffix == '.json':
                    patterns = json.load(f)
                elif filepath.suffix == '.csv':
                    import pandas as pd
                    df = pd.read_csv(filepath)
                    patterns = df.to_dict('records')
                else:
                    logger.error(f"Неподдерживаемый формат файла: {filepath.suffix}")
                    sys.exit(1)
            
            analysis, groups, artifacts = analyze_patterns(config, patterns)
            
        else:
            # Полный процесс: сбор + анализ
            actions, patterns = collect_data(config, args.output_format)
            
            if not args.collect_only:
                analysis, groups, artifacts = analyze_patterns(config, patterns)
        
        logger.info("Research Layer завершил работу успешно")
        
    except KeyboardInterrupt:
        logger.info("Работа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 