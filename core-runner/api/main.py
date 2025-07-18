"""
Core Runner API Server
FastAPI сервер для выполнения JALM-интентов
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import json
import os
import sys
import uuid
from pathlib import Path
import asyncio

# Добавляем путь к ядру
sys.path.append(str(Path(__file__).parent.parent / "kernel" / "src"))

# Импорт ядра исполнения
try:
    from main import JALMExecutor
except ImportError:
    # Fallback если ядро недоступно
    class JALMExecutor:
        def __init__(self):
            self.executions = {}
        
        async def execute(self, intent_content: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
            execution_id = str(uuid.uuid4())
            self.executions[execution_id] = {
                "status": "completed",
                "result": {"message": "Mock execution", "intent": intent_content},
                "params": params or {}
            }
            return {"execution_id": execution_id, "status": "completed"}

app = FastAPI(
    title="Core Runner API",
    description="API для выполнения JALM-интентов",
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

# Инициализация исполнителя
executor = JALMExecutor()

# Модели данных
class ExecutionRequest(BaseModel):
    intent_content: str = Field(..., description="JALM intent content")
    params: Dict[str, Any] = Field(default_factory=dict, description="Execution parameters")
    timeout: Optional[int] = Field(30, description="Execution timeout in seconds")

class ExecutionResponse(BaseModel):
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ExecutionStatus(BaseModel):
    execution_id: str
    status: str
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

# API endpoints
@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "Core Runner API",
        "version": "1.0.0",
        "description": "API для выполнения JALM-интентов",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "core-runner",
        "version": "1.0.0",
        "active_executions": len(executor.executions)
    }

@app.post("/execute", response_model=ExecutionResponse)
async def execute_intent(request: ExecutionRequest):
    """Выполнение JALM-интента"""
    try:
        # Выполнение интента
        result = await executor.execute(request.intent_content, request.params)
        
        return ExecutionResponse(
            execution_id=result["execution_id"],
            status=result["status"],
            result=result.get("result")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка выполнения: {str(e)}")

@app.get("/exec/{execution_id}", response_model=ExecutionStatus)
async def get_execution_status(execution_id: str):
    """Получение статуса выполнения"""
    if execution_id not in executor.executions:
        raise HTTPException(status_code=404, detail="Выполнение не найдено")
    
    execution = executor.executions[execution_id]
    
    return ExecutionStatus(
        execution_id=execution_id,
        status=execution["status"],
        result=execution.get("result"),
        error=execution.get("error"),
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )

@app.get("/exec")
async def list_executions():
    """Список всех выполнений"""
    return {
        "executions": [
            {
                "execution_id": exec_id,
                "status": exec_data["status"],
                "created_at": "2024-01-01T00:00:00Z"
            }
            for exec_id, exec_data in executor.executions.items()
        ],
        "total": len(executor.executions)
    }

@app.delete("/exec/{execution_id}")
async def cancel_execution(execution_id: str):
    """Отмена выполнения"""
    if execution_id not in executor.executions:
        raise HTTPException(status_code=404, detail="Выполнение не найдено")
    
    executor.executions[execution_id]["status"] = "cancelled"
    
    return {"message": "Выполнение отменено", "execution_id": execution_id}

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 