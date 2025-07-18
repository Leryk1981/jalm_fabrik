"""
Tula Spec API Server
FastAPI сервер для управления функциями JALM
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import json
import os
import sys
import importlib.util
from pathlib import Path

# Добавляем путь к функциям
sys.path.append(str(Path(__file__).parent.parent / "functions"))

app = FastAPI(
    title="Tula Spec API",
    description="API для управления функциями JALM",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class FunctionMetadata(BaseModel):
    id: str
    version: str
    hash: str
    description: str
    tags: List[str]
    author: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    implementation: Dict[str, Any]
    dependencies: List[str]
    runtime: Dict[str, Any]

class FunctionExecutionRequest(BaseModel):
    function_id: str
    version: Optional[str] = None
    hash: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class FunctionExecutionResponse(BaseModel):
    function_id: str
    result: Dict[str, Any]
    execution_time: float
    status: str

# Загрузка реестра функций
def load_registry() -> Dict[str, Any]:
    """Загружает реестр функций из JSON файла"""
    registry_path = Path(__file__).parent.parent / "registry" / "functions.json"
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"functions": [], "metadata": {"total_functions": 0}}

# Загрузка функции
def load_function(function_id: str, version: Optional[str] = None, 
                 hash: Optional[str] = None) -> Any:
    """Загружает функцию по ID, версии или хешу"""
    registry = load_registry()
    
    # Поиск функции
    target_function = None
    for func in registry["functions"]:
        if func["id"] == function_id:
            if version and func["version"] == version:
                target_function = func
                break
            elif hash and func["hash"] == hash:
                target_function = func
                break
            elif not version and not hash:
                target_function = func
                break
    
    if not target_function:
        raise HTTPException(status_code=404, detail=f"Функция {function_id} не найдена")
    
    # Загрузка модуля
    impl = target_function["implementation"]
    module_path = Path(__file__).parent.parent / "functions" / impl["file"]
    
    if not module_path.exists():
        raise HTTPException(status_code=500, detail=f"Файл {impl['file']} не найден")
    
    try:
        spec = importlib.util.spec_from_file_location(impl["file"], module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, target_function
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки функции: {str(e)}")

# API endpoints
@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "Tula Spec API",
        "version": "1.0.0",
        "description": "API для управления функциями JALM"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    registry = load_registry()
    return {
        "status": "healthy",
        "total_functions": registry["metadata"]["total_functions"],
        "last_updated": registry["metadata"]["last_updated"]
    }

@app.get("/functions", response_model=List[FunctionMetadata])
async def list_functions(
    tag: Optional[str] = Query(None, description="Фильтр по тегу"),
    author: Optional[str] = Query(None, description="Фильтр по автору")
):
    """Список всех функций с возможностью фильтрации"""
    registry = load_registry()
    functions = registry["functions"]
    
    # Фильтрация
    if tag:
        functions = [f for f in functions if tag in f.get("tags", [])]
    if author:
        functions = [f for f in functions if f.get("author") == author]
    
    return functions

@app.get("/functions/{function_id}", response_model=FunctionMetadata)
async def get_function(
    function_id: str,
    version: Optional[str] = Query(None, description="Версия функции"),
    hash: Optional[str] = Query(None, description="Хеш функции")
):
    """Получение метаданных функции"""
    registry = load_registry()
    
    for func in registry["functions"]:
        if func["id"] == function_id:
            if version and func["version"] == version:
                return func
            elif hash and func["hash"] == hash:
                return func
            elif not version and not hash:
                return func
    
    raise HTTPException(status_code=404, detail=f"Функция {function_id} не найдена")

@app.post("/functions/{function_id}/execute", response_model=FunctionExecutionResponse)
async def execute_function(
    function_id: str,
    request: FunctionExecutionRequest
):
    """Выполнение функции"""
    import time
    
    start_time = time.time()
    
    try:
        # Загрузка функции
        module, metadata = load_function(
            function_id, 
            request.version, 
            request.hash
        )
        
        # Получение функции
        func_name = metadata["implementation"]["function"]
        if not hasattr(module, func_name):
            raise HTTPException(
                status_code=500, 
                detail=f"Функция {func_name} не найдена в модуле"
            )
        
        func = getattr(module, func_name)
        
        # Выполнение функции
        if isinstance(request.params, dict) and len(request.params) == 1:
            # Если один параметр, передаем его значение
            param_value = list(request.params.values())[0]
            result = func(param_value)
        else:
            # Иначе передаем все параметры как kwargs
            result = func(**request.params)
        
        execution_time = time.time() - start_time
        
        return FunctionExecutionResponse(
            function_id=function_id,
            result=result,
            execution_time=execution_time,
            status="success"
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return FunctionExecutionResponse(
            function_id=function_id,
            result={"error": str(e)},
            execution_time=execution_time,
            status="error"
        )

@app.get("/functions/{function_id}/info")
async def get_function_info(function_id: str):
    """Получение информации о функции"""
    try:
        module, metadata = load_function(function_id)
        
        if hasattr(module, 'get_info'):
            info = module.get_info()
            return {
                "metadata": metadata,
                "info": info
            }
        else:
            return {
                "metadata": metadata,
                "info": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 