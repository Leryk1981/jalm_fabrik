"""
Модуль анализа паттернов для Research Layer
"""

import json
import yaml
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import logging
from pathlib import Path

from .config import ResearchConfig

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """
    Класс для анализа паттернов использования и группировки данных.
    Фокусируется на создании паттернов для чистых клиентских контейнеров JALM.
    """
    
    def __init__(self, config: Optional[ResearchConfig] = None):
        self.config = config or ResearchConfig()
        
    def analyze_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Анализировать паттерны использования.
        Создает структурированный анализ для интеграции с JALM-стеком.
        """
        analysis = {
            'summary': self._create_summary(patterns),
            'categories': self._categorize_patterns(patterns),
            'recommendations': self._generate_recommendations(patterns),
            'jalm_integration': self._prepare_jalm_integration(patterns),
            'analyzed_at': datetime.now().isoformat()
        }
        
        return analysis
    
    def group_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Группировать паттерны по категориям для JALM-стека.
        """
        groups = {
            'booking_systems': [],
            'ecommerce': [],
            'notification_services': [],
            'auth_systems': [],
            'api_gateways': [],
            'data_processing': [],
            'file_management': [],
            'reporting': []
        }
        
        for pattern in patterns:
            group = self._determine_pattern_group(pattern)
            if group in groups:
                groups[group].append(pattern)
                
        # Фильтруем пустые группы
        return {k: v for k, v in groups.items() if v}
    
    def _create_summary(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Создать сводку по паттернам"""
        if not patterns:
            return {'total_patterns': 0}
            
        total_patterns = len(patterns)
        app_types = Counter(p.get('app_type', 'unknown') for p in patterns)
        avg_frequency = sum(p.get('frequency', 0) for p in patterns) / total_patterns
        
        # Анализ компонентов
        all_components = []
        all_env_vars = []
        
        for pattern in patterns:
            all_components.extend(pattern.get('components', []))
            all_env_vars.extend(pattern.get('env_vars', []))
            
        common_components = Counter(all_components).most_common(10)
        common_env_vars = Counter(all_env_vars).most_common(10)
        
        return {
            'total_patterns': total_patterns,
            'app_types': dict(app_types),
            'average_frequency': round(avg_frequency, 2),
            'common_components': common_components,
            'common_env_vars': common_env_vars,
            'analysis_date': datetime.now().isoformat()
        }
    
    def _categorize_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Категоризация паттернов по сложности и типу"""
        categories = {
            'simple': [],
            'medium': [],
            'complex': []
        }
        
        for pattern in patterns:
            complexity = self._calculate_pattern_complexity(pattern)
            
            if complexity <= 2:
                categories['simple'].append(pattern)
            elif complexity <= 4:
                categories['medium'].append(pattern)
            else:
                categories['complex'].append(pattern)
                
        return categories
    
    def _calculate_pattern_complexity(self, pattern: Dict[str, Any]) -> int:
        """Вычислить сложность паттерна"""
        complexity = 1
        
        # Факторы сложности
        components = pattern.get('components', [])
        env_vars = pattern.get('env_vars', [])
        config = pattern.get('config_structure', {})
        
        # Количество компонентов
        if len(components) > 3:
            complexity += 1
        if len(components) > 5:
            complexity += 1
            
        # Количество переменных окружения
        if len(env_vars) > 5:
            complexity += 1
        if len(env_vars) > 10:
            complexity += 1
            
        # Сложность конфигурации
        if isinstance(config, dict) and len(config) > 3:
            complexity += 1
            
        # Тип приложения
        app_type = pattern.get('app_type', '')
        if app_type in ['microservice', 'ssr']:
            complexity += 1
            
        return min(complexity, 5)
    
    def _generate_recommendations(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Генерировать рекомендации для JALM-стека"""
        recommendations = []
        
        # Анализ популярных паттернов
        popular_patterns = sorted(patterns, key=lambda x: x.get('frequency', 0), reverse=True)[:5]
        
        for pattern in popular_patterns:
            recommendations.append({
                'type': 'popular_pattern',
                'pattern_name': pattern.get('pattern_name'),
                'frequency': pattern.get('frequency'),
                'recommendation': f"Добавить в каталог шаблонов: {pattern.get('pattern_name')}",
                'priority': 'high' if pattern.get('frequency', 0) > 50 else 'medium'
            })
        
        # Анализ недостающих компонентов
        all_components = set()
        for pattern in patterns:
            all_components.update(pattern.get('components', []))
            
        jalm_components = {'frontend', 'api', 'database', 'cache', 'auth'}
        missing_components = jalm_components - all_components
        
        for component in missing_components:
            recommendations.append({
                'type': 'missing_component',
                'component': component,
                'recommendation': f"Добавить базовый шаблон для {component}",
                'priority': 'medium'
            })
            
        # Рекомендации по переменным окружения
        common_env_vars = Counter()
        for pattern in patterns:
            common_env_vars.update(pattern.get('env_vars', []))
            
        top_env_vars = common_env_vars.most_common(5)
        for env_var, count in top_env_vars:
            recommendations.append({
                'type': 'common_env_var',
                'env_var': env_var,
                'frequency': count,
                'recommendation': f"Добавить {env_var} в стандартные переменные окружения",
                'priority': 'medium'
            })
            
        return recommendations
    
    def _prepare_jalm_integration(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Подготовить данные для интеграции с JALM-стеком"""
        integration_data = {
            'templates': [],
            'functions': [],
            'config_templates': [],
            'env_templates': []
        }
        
        for pattern in patterns:
            # Создание шаблона для Shablon Spec
            template = {
                'name': pattern.get('pattern_name'),
                'type': pattern.get('app_type'),
                'components': pattern.get('components', []),
                'description': f"Автоматически созданный шаблон для {pattern.get('pattern_name')}",
                'version': '1.0.0',
                'created_at': datetime.now().isoformat(),
                'frequency': pattern.get('frequency', 0)
            }
            integration_data['templates'].append(template)
            
            # Создание функций для Tula Registry
            for component in pattern.get('components', []):
                function = {
                    'name': f"{component}_handler",
                    'type': component,
                    'description': f"Обработчик для компонента {component}",
                    'version': '1.0.0',
                    'created_at': datetime.now().isoformat()
                }
                integration_data['functions'].append(function)
                
            # Шаблоны конфигурации
            config_template = {
                'name': f"{pattern.get('pattern_name')}_config",
                'structure': pattern.get('config_structure', {}),
                'env_vars': pattern.get('env_vars', []),
                'created_at': datetime.now().isoformat()
            }
            integration_data['config_templates'].append(config_template)
            
        return integration_data
    
    def _determine_pattern_group(self, pattern: Dict[str, Any]) -> str:
        """Определить группу паттерна на основе его характеристик"""
        pattern_name = pattern.get('pattern_name', '').lower()
        components = [c.lower() for c in pattern.get('components', [])]
        env_vars = [v.lower() for v in pattern.get('env_vars', [])]
        
        # Определение группы по ключевым словам
        if any(word in pattern_name for word in ['booking', 'reservation', 'appointment']):
            return 'booking_systems'
        elif any(word in pattern_name for word in ['shop', 'store', 'cart', 'payment']):
            return 'ecommerce'
        elif any(word in pattern_name for word in ['notification', 'email', 'sms', 'push']):
            return 'notification_services'
        elif any(word in pattern_name for word in ['auth', 'login', 'user', 'permission']):
            return 'auth_systems'
        elif any(word in pattern_name for word in ['gateway', 'proxy', 'router']):
            return 'api_gateways'
        elif any(word in pattern_name for word in ['data', 'process', 'transform']):
            return 'data_processing'
        elif any(word in pattern_name for word in ['file', 'upload', 'download']):
            return 'file_management'
        elif any(word in pattern_name for word in ['report', 'analytics', 'dashboard']):
            return 'reporting'
        else:
            return 'general'
    
    def export_groups(self, groups: Dict[str, List[Dict[str, Any]]], format: str = "json", filename: str = None) -> str:
        """
        Экспортировать сгруппированные данные
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pattern_groups_{timestamp}.{format}"
            
        filepath = self.config.get_data_path(filename)
        
        if format == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(groups, f, indent=2, ensure_ascii=False)
                
        elif format == "yaml":
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(groups, f, default_flow_style=False, allow_unicode=True)
                
        elif format == "csv":
            # Экспорт в CSV требует плоской структуры
            flat_data = []
            for group_name, patterns in groups.items():
                for pattern in patterns:
                    flat_data.append({
                        'group': group_name,
                        **pattern
                    })
                    
            if flat_data:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
                    writer.writeheader()
                    writer.writerows(flat_data)
                    
        logger.info(f"Группы паттернов экспортированы в {filepath}")
        return str(filepath)
    
    def create_jalm_artifacts(self, patterns: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Создать артефакты для интеграции с JALM-стеком
        """
        artifacts = {}
        
        # Анализ паттернов
        analysis = self.analyze_patterns(patterns)
        analysis_file = self.config.get_data_path("pattern_analysis.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        artifacts['analysis'] = str(analysis_file)
        
        # Группировка паттернов
        groups = self.group_patterns(patterns)
        groups_file = self.config.get_data_path("pattern_groups.json")
        with open(groups_file, 'w', encoding='utf-8') as f:
            json.dump(groups, f, indent=2, ensure_ascii=False)
        artifacts['groups'] = str(groups_file)
        
        # Шаблоны для Shablon Spec
        templates = analysis['jalm_integration']['templates']
        templates_file = self.config.get_data_path("jalm_templates.json")
        with open(templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)
        artifacts['templates'] = str(templates_file)
        
        # Функции для Tula Registry
        functions = analysis['jalm_integration']['functions']
        functions_file = self.config.get_data_path("jalm_functions.json")
        with open(functions_file, 'w', encoding='utf-8') as f:
            json.dump(functions, f, indent=2, ensure_ascii=False)
        artifacts['functions'] = str(functions_file)
        
        logger.info(f"Создано {len(artifacts)} артефактов для JALM-стека")
        return artifacts 