import time
import schedule
import logging
import os
from datetime import datetime
from typing import Optional

from .collector import DataCollector
from .analyzer import PatternAnalyzer
from .integration import JALMIntegration as ResearchIntegration

class ResearchScheduler:
    """Планировщик задач для автоматизации Research Layer"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.collector = DataCollector()
        self.analyzer = PatternAnalyzer()
        self.integration = ResearchIntegration()
        
        # Настройка из переменных окружения
        self.schedule_interval = int(os.getenv('SCHEDULE_INTERVAL', 3600))  # секунды
        self.auto_integrate = os.getenv('AUTO_INTEGRATE', 'false').lower() == 'true'
        
    def run_research_cycle(self):
        """Выполнение полного цикла исследований"""
        try:
            self.logger.info("Начинаем цикл автоматических исследований")
            
            # Сбор данных
            self.logger.info("Этап 1: Сбор данных")
            self.collector.collect_all_data()
            
            # Анализ паттернов
            self.logger.info("Этап 2: Анализ паттернов")
            self.analyzer.analyze_all_patterns()
            
            # Интеграция (если включена)
            if self.auto_integrate:
                self.logger.info("Этап 3: Автоматическая интеграция")
                self.integration.integrate_all_data()
            
            self.logger.info(f"Цикл исследований завершен: {datetime.now()}")
            
        except Exception as e:
            self.logger.error(f"Ошибка в цикле исследований: {e}")
    
    def schedule_research(self):
        """Настройка расписания задач"""
        # Ежечасное выполнение
        schedule.every(self.schedule_interval).seconds.do(self.run_research_cycle)
        
        # Ежедневное выполнение в 2:00
        schedule.every().day.at("02:00").do(self.run_research_cycle)
        
        # Еженедельное выполнение в воскресенье в 3:00
        schedule.every().sunday.at("03:00").do(self.run_research_cycle)
        
        self.logger.info(f"Планировщик настроен: интервал {self.schedule_interval} сек")
    
    def start(self):
        """Запуск планировщика"""
        self.logger.info("Запуск планировщика Research Layer")
        
        # Первоначальный запуск
        self.run_research_cycle()
        
        # Настройка расписания
        self.schedule_research()
        
        # Бесконечный цикл выполнения задач
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Проверка каждую минуту
            except KeyboardInterrupt:
                self.logger.info("Планировщик остановлен")
                break
            except Exception as e:
                self.logger.error(f"Ошибка в планировщике: {e}")
                time.sleep(300)  # Пауза 5 минут при ошибке

class ResearchWorker:
    """Воркер для выполнения разовых задач"""
    
    def __init__(self):
        self.scheduler = ResearchScheduler()
    
    def run_once(self):
        """Выполнение разового цикла исследований"""
        self.scheduler.run_research_cycle()
    
    def run_with_retry(self, max_retries: int = 3):
        """Выполнение с повторными попытками"""
        for attempt in range(max_retries):
            try:
                self.run_once()
                break
            except Exception as e:
                self.scheduler.logger.error(f"Попытка {attempt + 1} неудачна: {e}")
                if attempt < max_retries - 1:
                    time.sleep(60 * (attempt + 1))  # Увеличивающаяся пауза 