"""
Команда status - проверка статуса сервисов
"""

import subprocess
import requests
import logging
from typing import Dict, Any

def run(verbose: bool, config, logger: logging.Logger):
    """Проверяет статус сервисов"""
    
    services = ['core-runner', 'tula-spec', 'shablon-spec']
    status_info = {}
    
    logger.info("Проверка статуса сервисов...")
    
    for service_name in services:
        service_status = _check_service_status(service_name, config, logger, verbose)
        status_info[service_name] = service_status
    
    # Выводим сводку
    _print_status_summary(status_info, logger)
    
    if verbose:
        _print_detailed_status(status_info, logger)
    
    return True

def _check_service_status(service_name: str, config, logger: logging.Logger, verbose: bool) -> Dict[str, Any]:
    """Проверяет статус отдельного сервиса"""
    
    service_config = config.get_service_config(service_name)
    port = service_config.get('port', 8000)
    
    status_info = {
        'name': service_name,
        'port': port,
        'docker_running': False,
        'api_responding': False,
        'health_check': False
    }
    
    # Проверяем Docker контейнер
    docker_status = _check_docker_status(service_name, config, logger)
    status_info['docker_running'] = docker_status['running']
    status_info['docker_info'] = docker_status
    
    # Проверяем API
    if docker_status['running']:
        api_status = _check_api_status(service_name, port, logger)
        status_info['api_responding'] = api_status['responding']
        status_info['api_info'] = api_status
        
        # Проверяем health check
        if api_status['responding']:
            health_status = _check_health_endpoint(service_name, port, logger)
            status_info['health_check'] = health_status['healthy']
            status_info['health_info'] = health_status
    
    return status_info

def _check_docker_status(service_name: str, config, logger: logging.Logger) -> Dict[str, Any]:
    """Проверяет статус Docker контейнера"""
    
    try:
        # Ищем контейнер по имени
        cmd = ['docker', 'ps', '--filter', f'name={service_name}', '--format', '{{.Names}}\t{{.Status}}\t{{.Ports}}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if service_name in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        return {
                            'running': True,
                            'status': parts[1],
                            'ports': parts[2] if len(parts) > 2 else 'N/A'
                        }
        
        return {'running': False, 'status': 'Not found', 'ports': 'N/A'}
        
    except Exception as e:
        logger.debug(f"Ошибка проверки Docker для {service_name}: {e}")
        return {'running': False, 'status': 'Error', 'ports': 'N/A'}

def _check_api_status(service_name: str, port: int, logger: logging.Logger) -> Dict[str, Any]:
    """Проверяет доступность API"""
    
    try:
        url = f"http://localhost:{port}/"
        response = requests.get(url, timeout=5)
        
        return {
            'responding': True,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds()
        }
        
    except requests.exceptions.RequestException as e:
        logger.debug(f"API {service_name} не отвечает: {e}")
        return {
            'responding': False,
            'status_code': None,
            'response_time': None
        }

def _check_health_endpoint(service_name: str, port: int, logger: logging.Logger) -> Dict[str, Any]:
    """Проверяет health endpoint"""
    
    try:
        url = f"http://localhost:{port}/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            try:
                health_data = response.json()
                return {
                    'healthy': True,
                    'data': health_data
                }
            except:
                return {
                    'healthy': True,
                    'data': {'status': 'ok'}
                }
        else:
            return {
                'healthy': False,
                'data': {'status': f'HTTP {response.status_code}'}
            }
            
    except requests.exceptions.RequestException as e:
        logger.debug(f"Health check для {service_name} не удался: {e}")
        return {
            'healthy': False,
            'data': {'error': str(e)}
        }

def _print_status_summary(status_info: Dict[str, Any], logger: logging.Logger):
    """Выводит сводку статуса"""
    
    logger.info("\n" + "="*50)
    logger.info("СВОДКА СТАТУСА СЕРВИСОВ")
    logger.info("="*50)
    
    for service_name, info in status_info.items():
        status_icon = "🟢" if info['docker_running'] and info['api_responding'] else "🔴"
        logger.info(f"{status_icon} {service_name:<15} | Docker: {'✅' if info['docker_running'] else '❌'} | API: {'✅' if info['api_responding'] else '❌'} | Health: {'✅' if info['health_check'] else '❌'}")

def _print_detailed_status(status_info: Dict[str, Any], logger: logging.Logger):
    """Выводит детальную информацию о статусе"""
    
    logger.info("\n" + "="*50)
    logger.info("ДЕТАЛЬНАЯ ИНФОРМАЦИЯ")
    logger.info("="*50)
    
    for service_name, info in status_info.items():
        logger.info(f"\n📋 {service_name.upper()}")
        logger.info(f"   Порт: {info['port']}")
        logger.info(f"   Docker: {info['docker_info']['status']}")
        
        if info['api_responding']:
            logger.info(f"   API: ✅ (HTTP {info['api_info']['status_code']}, {info['api_info']['response_time']:.3f}s)")
            if info['health_check']:
                logger.info(f"   Health: ✅ {info['health_info']['data']}")
            else:
                logger.info(f"   Health: ❌ {info['health_info']['data']}")
        else:
            logger.info(f"   API: ❌ Не отвечает")
            logger.info(f"   Health: ❌ Недоступен") 