"""
Команда logs - просмотр логов сервисов
"""

import subprocess
import logging

def run(service: str, follow: bool, lines: int, config, logger: logging.Logger):
    """Показывает логи сервисов"""
    
    services = ['core-runner', 'tula-spec', 'shablon-spec'] if service == 'all' else [service]
    
    logger.info(f"Просмотр логов сервисов: {', '.join(services)}")
    
    for service_name in services:
        try:
            _show_service_logs(service_name, follow, lines, config, logger)
        except Exception as e:
            logger.error(f"Ошибка просмотра логов {service_name}: {e}")
            return False
    
    return True

def _show_service_logs(service_name: str, follow: bool, lines: int, config, logger: logging.Logger):
    """Показывает логи отдельного сервиса"""
    
    logger.info(f"\n📋 Логи {service_name}:")
    logger.info("="*50)
    
    # Пытаемся получить логи через Docker
    docker_status = _check_docker_container(service_name, logger)
    
    if docker_status['found']:
        _show_docker_logs(service_name, follow, lines, logger)
    else:
        # Пытаемся получить логи из файлов
        _show_file_logs(service_name, config, logger)

def _check_docker_container(service_name: str, logger: logging.Logger) -> dict:
    """Проверяет наличие Docker контейнера"""
    
    try:
        cmd = ['docker', 'ps', '--filter', f'name={service_name}', '--format', '{{.Names}}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout.strip():
            return {'found': True, 'container_name': result.stdout.strip()}
        
        return {'found': False, 'container_name': None}
        
    except Exception as e:
        logger.debug(f"Ошибка проверки Docker контейнера {service_name}: {e}")
        return {'found': False, 'container_name': None}

def _show_docker_logs(service_name: str, follow: bool, lines: int, logger: logging.Logger):
    """Показывает логи Docker контейнера"""
    
    try:
        cmd = ['docker', 'logs']
        
        if not follow:
            cmd.extend(['--tail', str(lines)])
        
        cmd.append(service_name)
        
        if follow:
            logger.info(f"Следуем за логами {service_name} (Ctrl+C для выхода)...")
            # В режиме follow запускаем без capture_output
            subprocess.run(cmd)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                if result.stdout.strip():
                    print(result.stdout)
                else:
                    logger.info("Логи пусты")
            else:
                logger.error(f"Ошибка получения логов: {result.stderr}")
                
    except KeyboardInterrupt:
        logger.info("Просмотр логов прерван")
    except Exception as e:
        logger.error(f"Ошибка получения Docker логов для {service_name}: {e}")

def _show_file_logs(service_name: str, config, logger: logging.Logger):
    """Показывает логи из файлов"""
    
    import os
    from pathlib import Path
    
    service_config = config.get_service_config(service_name)
    service_path = service_config.get('path', f'./{service_name}')
    
    # Ищем файлы логов
    log_files = []
    possible_log_paths = [
        os.path.join(service_path, 'logs'),
        os.path.join(service_path, '*.log'),
        os.path.join(service_path, '*.out'),
        os.path.join(service_path, '*.err')
    ]
    
    for log_path in possible_log_paths:
        if os.path.exists(log_path):
            if os.path.isfile(log_path):
                log_files.append(log_path)
            elif os.path.isdir(log_path):
                # Ищем файлы логов в директории
                for file in os.listdir(log_path):
                    if file.endswith(('.log', '.out', '.err')):
                        log_files.append(os.path.join(log_path, file))
    
    if log_files:
        logger.info(f"Найдены файлы логов: {', '.join(log_files)}")
        
        for log_file in log_files:
            try:
                logger.info(f"\n📄 {log_file}:")
                logger.info("-" * 30)
                
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    # Читаем последние строки
                    lines = f.readlines()
                    for line in lines[-50:]:  # Последние 50 строк
                        print(line.rstrip())
                        
            except Exception as e:
                logger.error(f"Ошибка чтения файла {log_file}: {e}")
    else:
        logger.info(f"Файлы логов для {service_name} не найдены")
        logger.info("Попробуйте запустить сервис: jalm up {service_name}") 