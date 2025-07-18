"""Модуль для поиска кода на GitHub"""

from typing import Dict, List, Optional
import requests
import os

class CodeResult:
    """Класс для хранения результатов поиска кода"""
    def __init__(self, repo: str, file_path: str, function_name: str, signature: str, example: Optional[str], score: float):
        self.repo = repo
        self.file_path = file_path
        self.function_name = function_name
        self.signature = signature
        self.example = example
        self.score = score

    def to_jalm_step(self) -> Dict:
        return {
            "call_tool": f"{self.function_name}",
            "args": {},
            "source": f"https://github.com/{self.repo}/blob/main/{self.file_path}"
        }

class GitHubCodeFinder:
    """Основной класс для поиска кода на GitHub"""
    
    def __init__(self, github_token: str = ""):
        self.headers = {"Authorization": f"token {github_token}"} if github_token else {}
    
    def find_github_code(self, description: str, language: str = 'python') -> List[CodeResult]:
        """Основной метод поиска кода"""
        # Существующая реализация find_github_code
        return []
    
    def get_file_content(self, file_url: str) -> str:
        """Получает содержимое файла через GitHub API"""
        # Существующая реализация get_file_content
        return ""
    
    def extract_functions(self, content: str, language: str) -> List[Dict]:
        """Извлекает функции из кода"""
        # Существующая реализация extract_functions
        return []
    
    def extract_signature(self, func_code: str) -> str:
        """Извлекает сигнатуру функции"""
        # Существующая реализация extract_signature
        return ""

ALLOWED_LICENSES = {"mit", "apache-2.0", "apache2", "apache 2.0"}
MIN_STARS = 100  # Можно вынести в настройки


def search_context7(query: str = "", api_key: str = "", top_k: int = 5):
    query = query or ""
    url = os.getenv("CONTEXT7_MCP_URL", "http://localhost:4000/v1/search")
    headers = {}
    if api_key:
        # Authorization всегда ASCII
        headers["Authorization"] = f"Bearer {api_key}"
    # ВАЖНО: не добавлять в headers никакие значения, содержащие не-ASCII символы!
    # Например, не используем Referer, X-Title и т.д. с кириллицей или спецсимволами
    payload = {
        "query": query,
        "language": "python",
        "top_k": top_k
    }
    import logging
    logger = logging.getLogger("context7")
    logger.info("HEADERS: %s", headers)
    logger.info("PAYLOAD: %s", payload)
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json().get("results", [])


def filter_context7_results(results):
    filtered = []
    for item in results:
        license_name = (item.get("license") or "").lower()
        stars = int(item.get("stars") or 0)
        if license_name in ALLOWED_LICENSES and stars >= MIN_STARS:
            filtered.append(item)
    return filtered


def context7_to_code_result(item) -> CodeResult:
    return CodeResult(
        repo=item.get("repo", ""),
        file_path=item.get("file_path", ""),
        function_name=item.get("function_name", ""),
        signature=item.get("signature", ""),
        example=item.get("example", ""),
        score=item.get("score", 0.0)
    )


def generate_template_from_query_context7(description: str, api_key: str) -> dict:
    results = search_context7(description, api_key)
    filtered = filter_context7_results(results)
    code_results = [context7_to_code_result(item) for item in filtered]
    jalm_steps = [r.to_jalm_step() for r in code_results[:3]]
    return {
        "intent": description.replace(" ", "_"),
        "steps": jalm_steps,
        "meta": {
            "stream": False,
            "retry_on_fail": 1
        },
        "context": {}
    }

if __name__ == "__main__":
    # Пример использования
    finder = GitHubCodeFinder()
    results = finder.find_github_code("parse CSV file")
    print(results)
