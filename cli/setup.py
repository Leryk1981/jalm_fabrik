#!/usr/bin/env python3
"""
Setup для JALM CLI
"""

from setuptools import setup, find_packages
import os

# Читаем README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "JALM CLI - Командная строка для управления JALM Full Stack"

setup(
    name="jalm-cli",
    version="1.0.0",
    description="CLI для управления JALM Full Stack экосистемой",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="JALM Foundation",
    author_email="info@jalm.org",
    url="https://github.com/jalm-foundation/jalm-full-stack",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "pyyaml>=5.4.0",
        "click>=8.0.0",
        "rich>=10.0.0",
        "tabulate>=0.8.9"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "jalm=cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    keywords="jalm, cli, saas, microservices, docker",
    project_urls={
        "Bug Reports": "https://github.com/jalm-foundation/jalm-full-stack/issues",
        "Source": "https://github.com/jalm-foundation/jalm-full-stack",
        "Documentation": "https://jalm.org/docs",
    },
) 