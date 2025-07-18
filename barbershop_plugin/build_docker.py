#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path

def build_docker_image():
    """Сборка Docker образа"""
    print("🐳 Сборка Docker образа...")
    
    try:
        # Проверка Docker
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        
        # Сборка образа
        cmd = ["docker", "build", "-t", "barbershop-plugin:latest", "."]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Docker образ успешно собран!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        return False
    except FileNotFoundError:
        print("❌ Docker не найден")
        return False

if __name__ == "__main__":
    build_docker_image()
