import yaml
import os
import subprocess
from typing import Dict, Any

class SaasProvisioner:
    def __init__(self, dockerfile_template_path: str, compose_template_path: str):
        self.dockerfile_template_path = dockerfile_template_path
        self.compose_template_path = compose_template_path

    def parse_jalm(self, jalm_path: str) -> Dict[str, Any]:
        """
        Читает и парсит JALM-конфиг (YAML).
        """
        with open(jalm_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data

    def render_template(self, template_path: str, params: Dict[str, Any], output_path: str) -> None:
        """
        Подставляет параметры в шаблон и сохраняет результат.
        """
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        for key, value in params.items():
            template = template.replace(f"__{key.upper()}__", str(value))
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template)

    def launch_instance(self, instance_name: str, instance_dir: str) -> str:
        """
        Запускает контейнер через docker-compose. Возвращает URL инстанса.
        """
        # Запуск контейнера
        try:
            subprocess.run([
                "docker-compose", "up", "-d"
            ], cwd=instance_dir, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ошибка запуска docker-compose: {e}")
        # Генерация URL (пример)
        return f"https://{instance_name}.mycalendar.app"

    def provision(self, jalm_path: str, base_instances_dir: str = "instances") -> str:
        """
        Основной метод: парсит JALM, подставляет параметры, запускает контейнер, возвращает URL.
        """
        jalm = self.parse_jalm(jalm_path)
        context = jalm.get("context", {})
        instance_name = context.get("domain", "demo").split(".")[0]
        instance_dir = os.path.join(base_instances_dir, instance_name)
        os.makedirs(instance_dir, exist_ok=True)
        # Подготовка параметров
        params = {
            "calendars": context.get("calendars", 1),
            "lang": context.get("lang", "ru"),
            "domain": context.get("domain", "demo.mycalendar.app")
        }
        # Рендер Dockerfile и docker-compose.yml
        self.render_template(self.dockerfile_template_path, params, os.path.join(instance_dir, "Dockerfile"))
        self.render_template(self.compose_template_path, params, os.path.join(instance_dir, "docker-compose.yml"))
        # Запуск контейнера
        url = self.launch_instance(instance_name, instance_dir)
        return url

# Пример использования:
if __name__ == "__main__":
    provisioner = SaasProvisioner(
        dockerfile_template_path="./Dockerfile.template",
        compose_template_path="./docker-compose.template.yml"
    )
    url = provisioner.provision("./config.jalm")
    print(f"Инстанс доступен по адресу: {url}") 