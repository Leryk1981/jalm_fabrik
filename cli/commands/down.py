"""
Команда down - остановка сервисов
"""

import subprocess
import logging

def run(service: str, config, logger: logging.Logger):
    """Останавливает сервисы"""
    
    services = ['core-runner', 'tula-spec', 'shablon-spec'] if service == 'all' else [service]
    
    logger.info(f"Остановка сервисов: {', '.join(services)}")
    
    for service_name in services:
        try:
            _stop_service(service_name, config, logger)
        except Exception as e:
            logger.error(f"Ошибка остановки {service_name}: {e}")
            return False
    
    logger.info("Все сервисы остановлены успешно")
    return True

def _stop_service(service_name: str, config, logger: logging.Logger):
    """Останавливает отдельный сервис"""
    
    service_config = config.get_service_config(service_name)
    service_path = service_config.get('path', f'./{service_name}')
    
    logger.info(f"Остановка {service_name} из {service_path}")
    
    # Проверяем существование директории
    import os
    if not os.path.exists(service_path):
        logger.error(f"Директория {service_path} не найдена")
        return False
    
    # Пытаемся остановить через Makefile
    makefile_path = os.path.join(service_path, 'Makefile')
    if os.path.exists(makefile_path):
        logger.info(f"Найден Makefile в {service_path}")
        
        # Команда для остановки
        cmd = ['make', 'stop']
        
        try:
            result = subprocess.run(
                cmd,
                cwd=service_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"{service_name} остановлен успешно")
            else:
                logger.warning(f"Предупреждение при остановке {service_name}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error(f"Таймаут остановки {service_name}")
            return False
        except Exception as e:
            logger.error(f"Ошибка выполнения команды для {service_name}: {e}")
            return False
    
    else:
        # Пытаемся остановить через Docker Compose
        docker_config = config.get_docker_config()
        compose_file = docker_config.get('compose_file', './docker/docker-compose.yml')
        
        if os.path.exists(compose_file):
            logger.info(f"Остановка через Docker Compose: {compose_file}")
            
            cmd = ['docker-compose', '-f', compose_file, 'down', service_name]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    logger.info(f"{service_name} остановлен через Docker Compose")
                else:
                    logger.warning(f"Предупреждение Docker Compose для {service_name}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Таймаут Docker Compose для {service_name}")
                return False
            except Exception as e:
                logger.error(f"Ошибка Docker Compose для {service_name}: {e}")
                return False
        else:
            logger.error(f"Не найден Makefile или docker-compose.yml для {service_name}")
            return False
    
    return True 