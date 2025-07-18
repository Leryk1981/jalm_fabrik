"""
Команда deploy - деплой шаблонов
"""

import subprocess
import os
import json
import logging
from pathlib import Path

def run(template: str, name: str, config_path: str, config, logger: logging.Logger):
    """Деплоит шаблон"""
    
    logger.info(f"🚀 Деплой шаблона: {template}")
    
    # Определяем имя деплоя
    deploy_name = name or f"{template}-{int(time.time())}"
    
    logger.info(f"Имя деплоя: {deploy_name}")
    
    try:
        # Проверяем доступность шаблона
        template_info = _check_template_availability(template, config, logger)
        if not template_info:
            return False
        
        # Создаем директорию для деплоя
        deploy_dir = _create_deploy_directory(deploy_name, logger)
        if not deploy_dir:
            return False
        
        # Генерируем конфигурацию деплоя
        deploy_config = _generate_deploy_config(template, deploy_name, config_path, config, logger)
        if not deploy_config:
            return False
        
        # Выполняем деплой
        success = _execute_deploy(deploy_name, deploy_config, config, logger)
        
        if success:
            logger.info(f"✅ Деплой {deploy_name} завершен успешно!")
            _print_deploy_info(deploy_name, deploy_config, logger)
        else:
            logger.error(f"❌ Деплой {deploy_name} не удался")
        
        return success
        
    except Exception as e:
        logger.error(f"Ошибка деплоя: {e}")
        return False

def _check_template_availability(template: str, config, logger: logging.Logger) -> dict:
    """Проверяет доступность шаблона"""
    
    logger.info(f"Проверка доступности шаблона: {template}")
    
    # Проверяем в shablon-spec
    shablon_config = config.get_service_config('shablon-spec')
    shablon_port = shablon_config.get('port', 8002)
    
    try:
        import requests
        url = f"http://localhost:{shablon_port}/templates/{template}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            template_data = response.json()
            logger.info(f"✅ Шаблон {template} найден в shablon-spec")
            return template_data
        else:
            logger.warning(f"Шаблон {template} не найден в shablon-spec")
            
    except Exception as e:
        logger.debug(f"Ошибка проверки shablon-spec: {e}")
    
    # Проверяем локальные шаблоны
    local_templates = _find_local_templates(config, logger)
    if template in local_templates:
        logger.info(f"✅ Шаблон {template} найден локально")
        return local_templates[template]
    
    logger.error(f"❌ Шаблон {template} не найден")
    logger.info("Доступные шаблоны:")
    for t in local_templates.keys():
        logger.info(f"  - {t}")
    
    return None

def _find_local_templates(config, logger: logging.Logger) -> dict:
    """Ищет локальные шаблоны"""
    
    templates = {}
    
    # Ищем в shablon_spec
    shablon_config = config.get_service_config('shablon-spec')
    shablon_path = shablon_config.get('path', './shablon_spec')
    
    templates_dir = os.path.join(shablon_path, 'templates')
    if os.path.exists(templates_dir):
        for item in os.listdir(templates_dir):
            item_path = os.path.join(templates_dir, item)
            if os.path.isdir(item_path):
                # Ищем metadata.json
                metadata_file = os.path.join(item_path, 'metadata.json')
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            templates[item] = metadata
                    except Exception as e:
                        logger.debug(f"Ошибка чтения {metadata_file}: {e}")
    
    return templates

def _create_deploy_directory(deploy_name: str, logger: logging.Logger) -> str:
    """Создает директорию для деплоя"""
    
    deploy_dir = f"./deployments/{deploy_name}"
    
    try:
        os.makedirs(deploy_dir, exist_ok=True)
        logger.info(f"Создана директория деплоя: {deploy_dir}")
        return deploy_dir
    except Exception as e:
        logger.error(f"Ошибка создания директории деплоя: {e}")
        return None

def _generate_deploy_config(template: str, deploy_name: str, config_path: str, config, logger: logging.Logger) -> dict:
    """Генерирует конфигурацию деплоя"""
    
    logger.info("Генерация конфигурации деплоя...")
    
    # Базовая конфигурация
    deploy_config = {
        'name': deploy_name,
        'template': template,
        'created_at': int(time.time()),
        'services': {},
        'ports': {},
        'environment': {}
    }
    
    # Загружаем пользовательскую конфигурацию
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                deploy_config.update(user_config)
            logger.info(f"Загружена пользовательская конфигурация: {config_path}")
        except Exception as e:
            logger.warning(f"Ошибка загрузки конфигурации {config_path}: {e}")
    
    # Генерируем порты для сервисов
    base_port = 9000
    for service in ['core-runner', 'tula-spec', 'shablon-spec']:
        deploy_config['ports'][service] = base_port
        base_port += 1
    
    # Сохраняем конфигурацию
    config_file = f"./deployments/{deploy_name}/deploy.json"
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(deploy_config, f, indent=2, ensure_ascii=False)
        logger.info(f"Конфигурация сохранена: {config_file}")
    except Exception as e:
        logger.error(f"Ошибка сохранения конфигурации: {e}")
        return None
    
    return deploy_config

def _execute_deploy(deploy_name: str, deploy_config: dict, config, logger: logging.Logger) -> bool:
    """Выполняет деплой"""
    
    logger.info("Выполнение деплоя...")
    
    deploy_dir = f"./deployments/{deploy_name}"
    
    try:
        # Используем SaaS Provisioner для создания продукта
        provisioner_path = './saas_provisioner.py'
        if os.path.exists(provisioner_path):
            logger.info("Использование SaaS Provisioner...")
            
            cmd = [
                'python', provisioner_path,
                '--template', deploy_config['template'],
                '--name', deploy_name,
                '--config', f"{deploy_dir}/deploy.json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 минут на деплой
            )
            
            if result.returncode == 0:
                logger.info("SaaS Provisioner выполнен успешно")
                return True
            else:
                logger.error(f"Ошибка SaaS Provisioner: {result.stderr}")
                return False
        else:
            logger.warning("SaaS Provisioner не найден, используем базовый деплой")
            return _basic_deploy(deploy_name, deploy_config, config, logger)
            
    except subprocess.TimeoutExpired:
        logger.error("Таймаут деплоя")
        return False
    except Exception as e:
        logger.error(f"Ошибка выполнения деплоя: {e}")
        return False

def _basic_deploy(deploy_name: str, deploy_config: dict, config, logger: logging.Logger) -> bool:
    """Базовый деплой без SaaS Provisioner"""
    
    logger.info("Выполнение базового деплоя...")
    
    # Создаем docker-compose.yml для деплоя
    compose_content = _generate_docker_compose(deploy_config, config, logger)
    
    compose_file = f"./deployments/{deploy_name}/docker-compose.yml"
    try:
        with open(compose_file, 'w', encoding='utf-8') as f:
            f.write(compose_content)
        logger.info(f"Создан docker-compose.yml: {compose_file}")
    except Exception as e:
        logger.error(f"Ошибка создания docker-compose.yml: {e}")
        return False
    
    # Запускаем через docker-compose
    try:
        cmd = ['docker-compose', '-f', compose_file, 'up', '-d']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            logger.info("Docker Compose запущен успешно")
            return True
        else:
            logger.error(f"Ошибка Docker Compose: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка запуска Docker Compose: {e}")
        return False

def _generate_docker_compose(deploy_config: dict, config, logger: logging.Logger) -> str:
    """Генерирует docker-compose.yml для деплоя"""
    
    services = {}
    
    # Добавляем сервисы
    for service_name in ['core-runner', 'tula-spec', 'shablon-spec']:
        service_config = config.get_service_config(service_name)
        port = deploy_config['ports'].get(service_name, service_config.get('port', 8000))
        
        services[service_name] = {
            'build': service_config.get('path', f'./{service_name}'),
            'ports': [f"{port}:{service_config.get('port', 8000)}"],
            'environment': deploy_config.get('environment', {}),
            'networks': ['jalm-network']
        }
    
    compose = {
        'version': '3.8',
        'services': services,
        'networks': {
            'jalm-network': {
                'driver': 'bridge'
            }
        }
    }
    
    import yaml
    return yaml.dump(compose, default_flow_style=False, allow_unicode=True)

def _print_deploy_info(deploy_name: str, deploy_config: dict, logger: logging.Logger):
    """Выводит информацию о деплое"""
    
    logger.info("\n" + "="*50)
    logger.info("ИНФОРМАЦИЯ О ДЕПЛОЕ")
    logger.info("="*50)
    logger.info(f"Имя: {deploy_name}")
    logger.info(f"Шаблон: {deploy_config['template']}")
    logger.info(f"Директория: ./deployments/{deploy_name}")
    
    logger.info("\nПорты сервисов:")
    for service, port in deploy_config['ports'].items():
        logger.info(f"  {service}: http://localhost:{port}")
    
    logger.info(f"\nУправление:")
    logger.info(f"  Остановка: docker-compose -f ./deployments/{deploy_name}/docker-compose.yml down")
    logger.info(f"  Логи: docker-compose -f ./deployments/{deploy_name}/docker-compose.yml logs")

# Импорт time для timestamp
import time 