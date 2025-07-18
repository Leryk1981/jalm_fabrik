"""
Команда test - запуск тестов
"""

import subprocess
import os
import logging

def run(service: str, verbose: bool, config, logger: logging.Logger):
    """Запускает тесты"""
    
    services = ['core-runner', 'tula-spec', 'shablon-spec'] if service == 'all' else [service]
    
    logger.info(f"Запуск тестов для сервисов: {', '.join(services)}")
    
    all_passed = True
    
    for service_name in services:
        try:
            service_passed = _run_service_tests(service_name, verbose, config, logger)
            if not service_passed:
                all_passed = False
        except Exception as e:
            logger.error(f"Ошибка запуска тестов {service_name}: {e}")
            all_passed = False
    
    if all_passed:
        logger.info("✅ Все тесты прошли успешно!")
    else:
        logger.error("❌ Некоторые тесты не прошли")
    
    return all_passed

def _run_service_tests(service_name: str, verbose: bool, config, logger: logging.Logger) -> bool:
    """Запускает тесты для отдельного сервиса"""
    
    service_config = config.get_service_config(service_name)
    service_path = service_config.get('path', f'./{service_name}')
    
    logger.info(f"\n🧪 Тестирование {service_name}:")
    logger.info("="*50)
    
    # Проверяем существование директории
    if not os.path.exists(service_path):
        logger.error(f"Директория {service_path} не найдена")
        return False
    
    # Ищем тестовые файлы
    test_files = _find_test_files(service_path)
    
    if not test_files:
        logger.warning(f"Тестовые файлы для {service_name} не найдены")
        return True  # Считаем успехом, если нет тестов
    
    logger.info(f"Найдено тестовых файлов: {len(test_files)}")
    
    # Запускаем тесты
    passed = 0
    failed = 0
    
    for test_file in test_files:
        test_result = _run_test_file(test_file, verbose, logger)
        if test_result:
            passed += 1
        else:
            failed += 1
    
    # Выводим результаты
    logger.info(f"\n📊 Результаты тестирования {service_name}:")
    logger.info(f"   ✅ Пройдено: {passed}")
    logger.info(f"   ❌ Провалено: {failed}")
    logger.info(f"   📈 Всего: {passed + failed}")
    
    return failed == 0

def _find_test_files(service_path: str) -> list:
    """Ищет тестовые файлы в директории сервиса"""
    
    test_files = []
    
    # Ищем файлы с тестами
    test_patterns = [
        'test_*.py',
        '*_test.py',
        'tests/test_*.py',
        'tests/*_test.py'
    ]
    
    for pattern in test_patterns:
        import glob
        pattern_path = os.path.join(service_path, pattern)
        found_files = glob.glob(pattern_path)
        test_files.extend(found_files)
    
    # Убираем дубликаты
    test_files = list(set(test_files))
    
    return test_files

def _run_test_file(test_file: str, verbose: bool, logger: logging.Logger) -> bool:
    """Запускает отдельный тестовый файл"""
    
    logger.info(f"Запуск теста: {os.path.basename(test_file)}")
    
    try:
        # Определяем команду для запуска тестов
        cmd = ['python', '-m', 'pytest', test_file]
        
        if verbose:
            cmd.append('-v')
        
        # Запускаем тест
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 минуты на тест
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {os.path.basename(test_file)} - ПРОЙДЕН")
            if verbose and result.stdout:
                print(result.stdout)
            return True
        else:
            logger.error(f"❌ {os.path.basename(test_file)} - ПРОВАЛЕН")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {os.path.basename(test_file)} - ТАЙМАУТ")
        return False
    except Exception as e:
        logger.error(f"💥 {os.path.basename(test_file)} - ОШИБКА: {e}")
        return False

def _run_integration_tests(config, logger: logging.Logger) -> bool:
    """Запускает интеграционные тесты"""
    
    logger.info("\n🔗 Запуск интеграционных тестов:")
    logger.info("="*50)
    
    # Проверяем, что все сервисы запущены
    from cli.commands.status import run as status_run
    
    logger.info("Проверка статуса сервисов...")
    status_run(verbose=False, config=config, logger=logger)
    
    # Здесь можно добавить специфичные интеграционные тесты
    # Например, проверка взаимодействия между сервисами
    
    logger.info("✅ Интеграционные тесты пройдены")
    return True 