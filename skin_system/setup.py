#!/usr/bin/env python3
"""
Setup script для Skin-As-Code системы
"""

from setuptools import setup, find_packages
import os

# Чтение README
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Чтение requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="skin-system",
    version="1.0.0",
    author="JALM Foundation",
    author_email="info@jalm.dev",
    description="Skin-As-Code система для JALM Full Stack",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jalm-foundation/skin-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: User Interfaces",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "flake8>=6.1.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "pylint>=3.0.3",
            "mypy>=1.7.1",
            "pre-commit>=3.6.0",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "skin-system=skin_system.cli:main",
            "create-skin=skin_system.cli:create_skin_command",
            "list-skins=skin_system.cli:list_skins_command",
            "validate-skin=skin_system.cli:validate_skin_command",
        ],
    },
    include_package_data=True,
    package_data={
        "skin_system": [
            "skins/default/*",
            "registry/*.json",
            "templates/*.html",
            "static/css/*.css",
            "static/js/*.js",
        ],
    },
    keywords="skin, ui, jalm, template, interface, generator",
    project_urls={
        "Bug Reports": "https://github.com/jalm-foundation/skin-system/issues",
        "Source": "https://github.com/jalm-foundation/skin-system",
        "Documentation": "https://docs.jalm.dev/skin-system",
    },
) 