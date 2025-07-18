#!/usr/bin/env python3

from saas_provisioner import SaasProvisioner

def test_service_discovery():
    print("🔍 Тестирование автоматического обнаружения сервисов...")
    
    provisioner = SaasProvisioner()
    services = provisioner.discover_available_services()
    
    print(f"\n📊 Результаты обнаружения:")
    print(f"Tula services: {len(services['tula_spec'])}")
    print(f"Shablon services: {len(services['shablon_spec'])}")
    
    print(f"\n🔧 Tula Spec функции:")
    for service in services['tula_spec']:
        print(f"  - {service['service']} v{service['version']}")
        print(f"    Описание: {service['description']}")
        print(f"    Теги: {', '.join(service.get('tags', []))}")
    
    print(f"\n📋 Shablon Spec шаблоны:")
    for service in services['shablon_spec']:
        print(f"  - {service['service']} v{service['version']}")
        print(f"    Описание: {service['description']}")
        print(f"    Категория: {service.get('category', 'general')}")
        print(f"    Теги: {', '.join(service.get('tags', []))}")
    
    # Тестируем создание provision.yaml
    print(f"\n🏗️ Тестирование создания provision.yaml...")
    provision_path = provisioner._create_basic_provision_yaml("barbershop.jalm.yaml")
    print(f"Создан: {provision_path}")
    
    # Читаем созданный provision.yaml
    provision = provisioner.read_provision_yaml(provision_path)
    print(f"\n📋 Созданный provision.yaml:")
    print(f"Tula services: {len(provision['dependencies']['tula_spec'])}")
    print(f"Shablon services: {len(provision['dependencies']['shablon_spec'])}")
    
    for service in provision['dependencies']['tula_spec']:
        print(f"  - {service['service']} v{service['version']}")
    
    for service in provision['dependencies']['shablon_spec']:
        print(f"  - {service['service']} v{service['version']}")

if __name__ == "__main__":
    test_service_discovery() 