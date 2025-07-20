"""
Skin-As-Code система для JALM Full Stack

Три доски архитектуры:
1. TemplateRegistry - глобальный магазин шаблонных блоков
2. SkinAssembler - bundler для сборки интерфейсов  
3. SkinStore - git-репозиторий скинов

Использование:
npm run create-skin -- client=acme color=2f7cff
"""

from .template_registry import TemplateRegistry
from .skin_assembler import SkinAssembler
from .skin_store import SkinStore
from .cli import SkinCLI

__version__ = "1.0.0"
__author__ = "JALM Foundation"

__all__ = [
    "TemplateRegistry",
    "SkinAssembler", 
    "SkinStore",
    "SkinCLI"
] 