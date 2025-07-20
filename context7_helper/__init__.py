"""
Context7 Helper - автоматический поиск готового кода через Context7 API

Этот модуль интегрируется с Context7 для автоматического поиска
готовых реализаций функций и генерации tool_candidates для JALM Full Stack.

Основные компоненты:
- Context7APIClient - клиент для работы с Context7 API
- CodeSearcher - поисковик кода по запросам
- ToolCandidateGenerator - генератор tool_candidates
- IntegrationManager - интеграция с Research Layer и CLI
"""

__version__ = "1.0.0"
__author__ = "JALM Foundation"
__description__ = "Context7 Helper для автоматического поиска кода"

from .client import Context7APIClient, Context7Result
from .searcher import CodeSearcher, SearchQuery
from .generator import ToolCandidateGenerator, ToolCandidate
from .integration import IntegrationManager

__all__ = [
    "Context7APIClient",
    "Context7Result",
    "CodeSearcher", 
    "SearchQuery",
    "ToolCandidateGenerator",
    "ToolCandidate",
    "IntegrationManager"
] 