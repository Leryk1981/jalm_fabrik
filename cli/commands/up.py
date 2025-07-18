"""
Команда up - запуск сервисов
"""

import subprocess
import time
from typing import Optional
import logging

def run(service: str, detach: bool, config, logger: logging.Logger):
    """Запускает сервисы"""
    
    services = ['core-runner', 'tula-spec', 'shablon-spec'] if service == 'all' else [service]
    
    logger.info(f"Запуск сервисов: {', '.join(services)}")
    
    for service_name in services:
        try:
            _start_service(service_name, detach, config, logger)
        except Exception as e:
            logger.error(f"Ошибка запуска {service_name}: {e}")
            return False
    
    logger.info("Все сервисы запущены успешно")
    return True

def _start_service(service_name: str, detach: bool, config, logger: logging.Logger):
    """Запускает отдельный сервис"""
    
    service_config = config.get_service_config(service_name)
    service_path = service_config.get('path', f'./{service_name}')
    
    logger.info(f"Запуск {service_name} из {service_path}")
    
    # Проверяем существование директории
    import os
    if not os.path.exists(service_path):
        logger.error(f"Директория {service_path} не найдена")
        return False
    
    # Пытаемся запустить через Makefile
    makefile_path = os.path.join(service_path, 'Makefile')
    if os.path.exists(makefile_path):
        logger.info(f"Найден Makefile в {service_path}")
        
        # Команда для запуска
        cmd = ['make', 'run-docker'] if detach else ['make', 'run']
        
        try:
            result = subprocess.run(
                cmd,
                cwd=service_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"{service_name} запущен успешно")
            else:
                logger.error(f"Ошибка запуска {service_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Таймаут запуска {service_name}")
            return False
        except Exception as e:
            logger.error(f"Ошибка выполнения команды для {service_name}: {e}")
            return False
    
    else:
        # Пытаемся запустить через Docker Compose
        docker_config = config.get_docker_config()
        compose_file = docker_config.get('compose_file', './docker/docker-compose.yml')
        
        if os.path.exists(compose_file):
            logger.info(f"Запуск через Docker Compose: {compose_file}")
            
            cmd = ['docker-compose', '-f', compose_file, 'up', service_name]
            if detach:
                cmd.append('-d')
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    logger.info(f"{service_name} запущен через Docker Compose")
                else:
                    logger.error(f"Ошибка Docker Compose для {service_name}: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Таймаут Docker Compose для {service_name}")
                return False
            except Exception as e:
                logger.error(f"Ошибка Docker Compose для {service_name}: {e}")
                return False
        else:
            logger.error(f"Не найден Makefile или docker-compose.yml для {service_name}")
            return False
    
    # Ждем немного для стабилизации
    if not detach:
        time.sleep(2)
    
    return True 