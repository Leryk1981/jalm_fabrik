"""
Setup script для Context7 Helper
"""

from setuptools import setup, find_packages
from pathlib import Path

# Чтение README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="context7-helper",
    version="1.0.0",
    author="JALM Foundation",
    author_email="info@jalm.foundation",
    description="Автоматический поиск кода через Context7 API для JALM Full Stack",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jalm/context7-helper",
    packages=find_packages(),
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
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pathlib2>=2.3.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "context7=context7_helper.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 