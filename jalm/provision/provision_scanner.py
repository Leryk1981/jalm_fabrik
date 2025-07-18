#!/usr/bin/env python3
"""
JALM Provision Scanner
Анализирует Intent-DSL и генерирует provision.yaml
"""

import re
import yaml
from typing import Dict, Any, List, Set
from pathlib import Path

class ProvisionScanner:
    def __init__(self):
        self.provision_template = {
            "app_id": "",
            "env": "prod infra/docker/compose",
            "dependencies": {
                "datastore": {},
                "api_layer": [],
                "tula_spec": [],
                "shablon_spec": []
            },
            "storage": {
                "files": {
                    "type": "local",
                    "mount": "/app/FILES"
                }
            },
            "net": {
                "ingress": "nginx",
                "domain": "{tenant}.run"
            },
            "health": {
                "endpoint": "/health",
                "timeout": "3s"
            },
            "meta": {
                "provisioner": "jalm-fullstack",
                "force_service_discovery": True
            }
        }
    
    def scan_intent(self, jalm_content: str, app_id: str = None) -> Dict[str, Any]:
        """
        Анализирует Intent-DSL и генерирует provision.yaml
        """
        provision = self.provision_template.copy()
        
        # Установка app_id
        if app_id:
            provision["app_id"] = app_id
        else:
            # Извлечение из BEGIN directive
            begin_match = re.search(r'BEGIN\s+(\w+)', jalm_content)
            if begin_match:
                provision["app_id"] = f"{begin_match.group(1)}_app_v1"
            else:
                provision["app_id"] = "jalm_app_v1"
        
        # Анализ зависимостей
        self._analyze_dependencies(jalm_content, provision)
        
        # Анализ инфраструктуры
        self._analyze_infrastructure(jalm_content, provision)
        
        # Анализ сети
        self._analyze_network(jalm_content, provision)
        
        return provision
    
    def _analyze_dependencies(self, jalm_content: str, provision: Dict[str, Any]) -> None:
        """
        Анализирует зависимости из Intent-DSL
        """
        lines = jalm_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Анализ IMPORT директив
            if line.startswith('IMPORT'):
                self._parse_import_directive(line, provision)
            
            # Анализ CREATE директив
            elif line.startswith('CREATE'):
                self._parse_create_directive(line, provision)
            
            # Анализ EXPOSE директив
            elif line.startswith('EXPOSE'):
                self._parse_expose_directive(line, provision)
    
    def _parse_import_directive(self, line: str, provision: Dict[str, Any]) -> None:
        """
        Парсит IMPORT директиву
        """
        # IMPORT slot_validator tula:hash~ab12fe
        # IMPORT booking_widget v1.3.2
        # IMPORT notify_system v1.0.0
        
        parts = line.split()
        if len(parts) >= 2:
            service_name = parts[1]
            
            # Определение типа сервиса
            if 'tula:' in line or any(part in line for part in ['v1.', 'v2.', 'hash~']):
                # Tula Spec функция
                service_info = {
                    "service": service_name,
                    "version": self._extract_version(line),
                    "expose": "internal",
                    "source": "tula_spec"
                }
                provision["dependencies"]["tula_spec"].append(service_info)
                
                # Добавление в api_layer для совместимости
                provision["dependencies"]["api_layer"].append(service_info)
            else:
                # Shablon Spec шаблон
                service_info = {
                    "service": service_name,
                    "version": self._extract_version(line),
                    "expose": "internal",
                    "source": "shablon_spec"
                }
                provision["dependencies"]["shablon_spec"].append(service_info)
    
    def _parse_create_directive(self, line: str, provision: Dict[str, Any]) -> None:
        """
        Парсит CREATE директиву
        """
        # CREATE database bookings
        # CREATE table users
        # CREATE index idx_slots
        
        if 'database' in line.lower():
            provision["dependencies"]["datastore"] = {
                "type": "postgresql:15",
                "tier": "managed",
                "region": "us-east-1",
                "replicas": 1
            }
        elif 'table' in line.lower():
            if not provision["dependencies"]["datastore"]:
                provision["dependencies"]["datastore"] = {
                    "type": "postgresql:15",
                    "tier": "managed"
                }
    
    def _parse_expose_directive(self, line: str, provision: Dict[str, Any]) -> None:
        """
        Парсит EXPOSE директиву
        """
        # EXPOSE /widget
        # EXPOSE /api
        
        if '/widget' in line:
            provision["net"]["ingress"] = "nginx"
            provision["net"]["widget_endpoint"] = "/widget"
        elif '/api' in line:
            provision["net"]["api_endpoint"] = "/api"
    
    def _extract_version(self, line: str) -> str:
        """
        Извлекает версию из строки
        """
        # Ищем версию в формате v1.3.2 или hash~ab12fe
        version_match = re.search(r'(?:v(\d+\.\d+\.\d+)|hash~([a-f0-9]+))', line)
        if version_match:
            if version_match.group(1):
                return f"v{version_match.group(1)}"
            else:
                return f"hash~{version_match.group(2)}"
        return "latest"
    
    def _analyze_infrastructure(self, jalm_content: str, provision: Dict[str, Any]) -> None:
        """
        Анализирует требования к инфраструктуре
        """
        content_lower = jalm_content.lower()
        
        # Определение окружения
        if 'prod' in content_lower or 'production' in content_lower:
            provision["env"] = "prod infra/aws/ecs"
        elif 'dev' in content_lower or 'development' in content_lower:
            provision["env"] = "dev infra/docker/compose"
        else:
            provision["env"] = "prod infra/docker/compose"
        
        # Определение требований к хранилищу
        if 'file' in content_lower or 'upload' in content_lower:
            provision["storage"]["files"] = {
                "type": "aws-s3",
                "bucket": f"{provision['app_id']}-files",
                "mount": "/uploads"
            }
    
    def _analyze_network(self, jalm_content: str, provision: Dict[str, Any]) -> None:
        """
        Анализирует сетевые требования
        """
        content_lower = jalm_content.lower()
        
        # Определение домена
        if 'domain' in content_lower:
            domain_match = re.search(r'domain[:\s]+([^\s]+)', content_lower)
            if domain_match:
                provision["net"]["domain"] = domain_match.group(1)
        
        # Определение каналов связи
        channels = []
        if 'web' in content_lower:
            channels.append("web")
        if 'email' in content_lower:
            channels.append("email")
        if 'sms' in content_lower:
            channels.append("sms")
        if 'telegram' in content_lower:
            channels.append("telegram")
            provision["dependencies"]["api_layer"].append({
                "service": "telegram_bot",
                "version": "1.0.0",
                "expose": "external",
                "secrets": ["${{secrets.TELEGRAM_TOKEN}}"]
            })
        
        if channels:
            provision["net"]["channels"] = channels
    
    def generate_provision_yaml(self, jalm_path: str, output_path: str = None) -> str:
        """
        Генерирует provision.yaml из JALM файла
        """
        # Чтение JALM файла
        with open(jalm_path, 'r', encoding='utf-8') as f:
            jalm_content = f.read()
        
        # Сканирование и генерация provision
        provision = self.scan_intent(jalm_content)
        
        # Определение пути вывода
        if not output_path:
            jalm_file = Path(jalm_path)
            output_path = jalm_file.parent / "provision.yaml"
        
        # Запись provision.yaml
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(provision, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return str(output_path)

# Пример использования
if __name__ == "__main__":
    scanner = ProvisionScanner()
    
    # Пример JALM файла
    sample_jalm = """
BEGIN booking-flow
  IMPORT slot_validator tula:hash~ab12fe
  IMPORT booking_widget v1.3.2
  IMPORT notify_system v1.0.0
  
  CREATE database bookings
  EXPOSE /widget
  
  WHEN client REQUESTS slot
    RUN slot_uuid := slot_validator.create(slot)
    IF slot_uuid.status == "valid" THEN
      PARALLEL
        RUN widget := booking_widget.create(calendar_id, user_id),
        RUN notify_system.send("Слот подтвержден", "web", user_email, "confirmed")
      system.log("evt: booked")
    ELSE
      client.notify("choose_other")
  ON ERROR rollbackBooking
END
"""
    
    # Генерация provision.yaml
    provision = scanner.scan_intent(sample_jalm, "booking_app_v1")
    
    print("Generated provision.yaml:")
    print(yaml.dump(provision, default_flow_style=False, allow_unicode=True, sort_keys=False)) 