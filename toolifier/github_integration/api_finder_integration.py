"""
Модуль интеграции GitHub Code Finder и API Wrapper Generator
"""

from clean_project.core import GitHubCodeFinder as GitHubCodeFinder
from clean_project.generator.api_wrapper_generator import generate_wrapper, FunctionSignature
from typing import List, Dict
import json

class APIFinderIntegration:
    def __init__(self, github_token: str):
        self.finder = GitHubCodeFinder(github_token)
        
    def find_and_wrap(self, query: str, lang: str = "python") -> List[Dict]:
        """
        Находит код по запросу и генерирует API endpoints
        
        Args:
            query: Поисковый запрос
            lang: Язык программирования
            
        Returns:
            List[Dict]: Список сгенерированных endpoints
        """
        # Поиск кода через GitHub Code Finder
        code_results = self.finder.find_github_code(query, lang)
        
        # Генерация API endpoints
        endpoints = []
        for result in code_results:
            signature = FunctionSignature(
                name=result["function_name"],
                description=result["description"],
                parameters=json.loads(result["parameters"]),
                returns=result["returns"],
                source_code=result["source_code"]
            )
            
            wrapper = generate_wrapper(signature)
            endpoints.append({
                "name": signature.name,
                "endpoint": f"/{signature.name}",
                "code": wrapper
            })
        
        return endpoints

if __name__ == "__main__":
    # Пример использования
    import os
    integrator = APIFinderIntegration(os.getenv("GITHUB_TOKEN"))
    print(integrator.find_and_wrap("parse csv python"))
