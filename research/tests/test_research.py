"""
Тесты для Research Layer
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from research import DataCollector, PatternAnalyzer, ResearchConfig


class TestResearchConfig:
    """Тесты конфигурации"""
    
    def test_default_config(self):
        """Тест создания конфигурации по умолчанию"""
        config = ResearchConfig()
        
        assert config.min_pattern_frequency == 3
        assert config.max_pattern_length == 10
        assert config.similarity_threshold == 0.8
        assert "github_api" in config.data_sources
        assert "csv" in config.export_formats
        
    def test_custom_config(self):
        """Тест создания кастомной конфигурации"""
        config = ResearchConfig(
            min_pattern_frequency=5,
            data_sources=["github_api", "npm_registry"]
        )
        
        assert config.min_pattern_frequency == 5
        assert len(config.data_sources) == 2
        assert "github_api" in config.data_sources
        
    def test_validate_config(self):
        """Тест валидации конфигурации"""
        config = ResearchConfig()
        assert config.validate() is True
        
    def test_get_data_path(self):
        """Тест получения пути к файлу данных"""
        config = ResearchConfig()
        path = config.get_data_path("test.csv")
        assert "test.csv" in str(path)


class TestDataCollector:
    """Тесты сборщика данных"""
    
    def test_init(self):
        """Тест инициализации сборщика"""
        collector = DataCollector()
        assert collector.config is not None
        assert collector.session is not None
        
    @patch('research.collector.requests.Session')
    def test_collect_actions_mock(self, mock_session):
        """Тест сбора действий с моком"""
        # Настройка мока
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'full_name': 'test/repo',
                    'stargazers_count': 100,
                    'description': 'Test repo',
                    'language': 'Python',
                    'created_at': '2024-01-01T00:00:00Z'
                }
            ]
        }
        mock_session.return_value.get.return_value = mock_response
        
        collector = DataCollector()
        actions = collector.collect_actions()
        
        # Проверяем что данные собраны
        assert len(actions) > 0
        
    def test_estimate_complexity(self):
        """Тест оценки сложности"""
        collector = DataCollector()
        
        repo = {
            'language': 'Python',
            'size': 500,
            'forks_count': 50
        }
        
        complexity = collector._estimate_complexity(repo)
        assert 1 <= complexity <= 5
        
    def test_extract_spa_patterns(self):
        """Тест извлечения SPA паттернов"""
        collector = DataCollector()
        
        actions = [
            {
                'technology': 'react',
                'source': 'github',
                'usage_count': 100
            }
        ]
        
        patterns = collector._extract_spa_patterns(actions)
        assert len(patterns) > 0
        assert patterns[0]['name'] == 'basic_spa'
        
    def test_export(self):
        """Тест экспорта данных"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ResearchConfig()
            config.patterns_dir = Path(temp_dir)
            
            collector = DataCollector(config)
            
            data = [
                {'name': 'test1', 'value': 1},
                {'name': 'test2', 'value': 2}
            ]
            
            # Тест экспорта в JSON
            filepath = collector.export(data, "json", "test.json")
            assert Path(filepath).exists()
            
            # Проверяем содержимое
            with open(filepath, 'r') as f:
                exported_data = json.load(f)
                assert len(exported_data) == 2


class TestPatternAnalyzer:
    """Тесты анализатора паттернов"""
    
    def test_init(self):
        """Тест инициализации анализатора"""
        analyzer = PatternAnalyzer()
        assert analyzer.config is not None
        
    def test_analyze_patterns(self):
        """Тест анализа паттернов"""
        analyzer = PatternAnalyzer()
        
        patterns = [
            {
                'pattern_name': 'test_pattern',
                'components': ['frontend', 'api'],
                'env_vars': ['DB_URL'],
                'frequency': 10,
                'app_type': 'spa'
            }
        ]
        
        analysis = analyzer.analyze_patterns(patterns)
        
        assert 'summary' in analysis
        assert 'categories' in analysis
        assert 'recommendations' in analysis
        assert 'jalm_integration' in analysis
        
    def test_group_patterns(self):
        """Тест группировки паттернов"""
        analyzer = PatternAnalyzer()
        
        patterns = [
            {
                'pattern_name': 'booking_system',
                'components': ['frontend', 'api', 'database'],
                'env_vars': ['DB_URL'],
                'frequency': 10,
                'app_type': 'spa'
            }
        ]
        
        groups = analyzer.group_patterns(patterns)
        
        # Проверяем что паттерн попал в правильную группу
        assert 'booking_systems' in groups
        assert len(groups['booking_systems']) > 0
        
    def test_calculate_pattern_complexity(self):
        """Тест вычисления сложности паттерна"""
        analyzer = PatternAnalyzer()
        
        pattern = {
            'components': ['frontend', 'api', 'database', 'cache'],
            'env_vars': ['DB_URL', 'API_KEY', 'CACHE_URL'],
            'config_structure': {'api': {'port': 8080}},
            'app_type': 'microservice'
        }
        
        complexity = analyzer._calculate_pattern_complexity(pattern)
        assert 1 <= complexity <= 5
        
    def test_determine_pattern_group(self):
        """Тест определения группы паттерна"""
        analyzer = PatternAnalyzer()
        
        pattern = {
            'pattern_name': 'booking_light',
            'components': ['frontend', 'api'],
            'env_vars': ['DB_URL']
        }
        
        group = analyzer._determine_pattern_group(pattern)
        assert group == 'booking_systems'
        
    def test_create_jalm_artifacts(self):
        """Тест создания артефактов для JALM"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ResearchConfig()
            config.patterns_dir = Path(temp_dir)
            
            analyzer = PatternAnalyzer(config)
            
            patterns = [
                {
                    'pattern_name': 'test_pattern',
                    'components': ['frontend', 'api'],
                    'env_vars': ['DB_URL'],
                    'frequency': 10,
                    'app_type': 'spa'
                }
            ]
            
            artifacts = analyzer.create_jalm_artifacts(patterns)
            
            assert 'analysis' in artifacts
            assert 'groups' in artifacts
            assert 'templates' in artifacts
            assert 'functions' in artifacts
            
            # Проверяем что файлы созданы
            for filepath in artifacts.values():
                assert Path(filepath).exists()


class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ResearchConfig()
            config.patterns_dir = Path(temp_dir)
            
            # Создание тестовых данных
            test_actions = [
                {
                    'action_type': 'create_react',
                    'technology': 'react',
                    'complexity': 2,
                    'source': 'github',
                    'usage_count': 100
                }
            ]
            
            test_patterns = [
                {
                    'pattern_name': 'spa_basic',
                    'components': ['frontend', 'api'],
                    'env_vars': ['API_URL'],
                    'config_structure': {'frontend': {'build': 'dist'}},
                    'frequency': 50,
                    'app_type': 'spa'
                }
            ]
            
            # Тест сборщика
            collector = DataCollector(config)
            collector.export(test_actions, "json", "test_actions.json")
            
            # Тест анализатора
            analyzer = PatternAnalyzer(config)
            analysis = analyzer.analyze_patterns(test_patterns)
            groups = analyzer.group_patterns(test_patterns)
            artifacts = analyzer.create_jalm_artifacts(test_patterns)
            
            # Проверяем результаты
            assert len(analysis['summary']['total_patterns']) > 0
            assert len(groups) > 0
            assert len(artifacts) == 4


if __name__ == "__main__":
    pytest.main([__file__]) 