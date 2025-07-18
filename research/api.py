from flask import Flask, request, jsonify
import logging
import os
from datetime import datetime
from typing import Dict, Any

from .collector import DataCollector
from .analyzer import PatternAnalyzer
from .integration import JALMIntegration as ResearchIntegration
from .scheduler import ResearchScheduler

class ResearchAPI:
    """REST API для Research Layer"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.logger = logging.getLogger(__name__)
        
        # Инициализация компонентов
        self.collector = DataCollector()
        self.analyzer = PatternAnalyzer()
        self.integration = ResearchIntegration()
        self.scheduler = ResearchScheduler()
        
        # Настройка маршрутов
        self.setup_routes()
    
    def setup_routes(self):
        """Настройка API маршрутов"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Проверка состояния API"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
        
        @self.app.route('/api/v1/collect', methods=['POST'])
        def collect_data():
            """Запуск сбора данных"""
            try:
                data = request.get_json() or {}
                sources = data.get('sources', ['all'])
                
                self.logger.info(f"Запуск сбора данных: {sources}")
                self.collector.collect_all_data()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Сбор данных завершен',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Ошибка сбора данных: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/v1/analyze', methods=['POST'])
        def analyze_patterns():
            """Запуск анализа паттернов"""
            try:
                data = request.get_json() or {}
                patterns = data.get('patterns', ['all'])
                
                self.logger.info(f"Запуск анализа паттернов: {patterns}")
                self.analyzer.analyze_all_patterns()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Анализ паттернов завершен',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Ошибка анализа: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/v1/integrate', methods=['POST'])
        def integrate_data():
            """Запуск интеграции данных"""
            try:
                data = request.get_json() or {}
                targets = data.get('targets', ['all'])
                
                self.logger.info(f"Запуск интеграции: {targets}")
                self.integration.integrate_all_data()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Интеграция завершена',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Ошибка интеграции: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/v1/research-cycle', methods=['POST'])
        def run_research_cycle():
            """Запуск полного цикла исследований"""
            try:
                self.logger.info("Запуск полного цикла исследований")
                self.scheduler.run_research_cycle()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Цикл исследований завершен',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Ошибка цикла исследований: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/v1/status', methods=['GET'])
        def get_status():
            """Получение статуса Research Layer"""
            try:
                # Проверка файлов данных
                data_files = self.collector.get_data_files()
                pattern_files = self.analyzer.get_pattern_files()
                
                return jsonify({
                    'status': 'operational',
                    'data_files': len(data_files),
                    'pattern_files': len(pattern_files),
                    'last_update': datetime.now().isoformat(),
                    'auto_integrate': self.scheduler.auto_integrate,
                    'schedule_interval': self.scheduler.schedule_interval
                })
            except Exception as e:
                self.logger.error(f"Ошибка получения статуса: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/v1/patterns', methods=['GET'])
        def get_patterns():
            """Получение списка паттернов"""
            try:
                patterns = self.analyzer.get_all_patterns()
                return jsonify({
                    'patterns': patterns,
                    'count': len(patterns)
                })
            except Exception as e:
                self.logger.error(f"Ошибка получения паттернов: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
    
    def start(self):
        """Запуск API сервера"""
        port = int(os.getenv('API_PORT', 8080))
        self.logger.info(f"Запуск Research API на порту {port}")
        
        self.app.run(
            host='0.0.0.0',
            port=port,
            debug=False
        ) 