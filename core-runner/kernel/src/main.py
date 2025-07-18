#!/usr/bin/env python3
"""
JALM Core Runner - Исполнительное ядро для JALM Full Stack
Этап 5 Core Spec: собрать «ядро» как готовую пачку
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import yaml

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger("jalm-core-runner")

app = FastAPI(
    title="JALM Core Runner",
    description="Исполнительное ядро для JALM Full Stack",
    version="1.0.0"
)

class JALMStep(BaseModel):
    """Модель JALM-шага"""
    id: str
    layer: str
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class JALMExecution(BaseModel):
    """Модель JALM-выполнения"""
    execution_id: str
    jalm_config: Dict[str, Any]
    steps: List[JALMStep]
    status: str  # pending, running, completed, failed
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_time: Optional[float] = None

class ExecutionRequest(BaseModel):
    """Модель запроса на выполнение"""
    jalm_config: Dict[str, Any]
    timeout: Optional[int] = 300  # секунды

class CoreRunner:
    """Основной класс исполнительного ядра"""
    
    def __init__(self):
        self.executions: Dict[str, JALMExecution] = {}
        self.worker_pool = ThreadPoolExecutor(max_workers=10)
        self.supported_layers = {
            "io-http": self._execute_http,
            "io-db": self._execute_db,
            "io-file": self._execute_file,
            "compute-script": self._execute_script,
            "render-html": self._execute_render,
            "notify-mq": self._execute_notify
        }
    
    async def execute_jalm(self, jalm_config: Dict[str, Any], timeout: int = 300) -> str:
        """Выполнение JALM-конфига"""
        execution_id = str(uuid.uuid4())
        
        # Создаём запись выполнения
        execution = JALMExecution(
            execution_id=execution_id,
            jalm_config=jalm_config,
            steps=[],
            status="pending",
            created_at=datetime.now()
        )
        
        self.executions[execution_id] = execution
        
        # Запускаем выполнение в фоне
        asyncio.create_task(self._run_execution(execution_id, timeout))
        
        return execution_id
    
    async def _run_execution(self, execution_id: str, timeout: int):
        """Выполнение JALM в фоновом режиме"""
        execution = self.executions[execution_id]
        execution.status = "running"
        execution.started_at = datetime.now()
        
        try:
            steps = execution.jalm_config.get("steps", [])
            
            for step_config in steps:
                step = JALMStep(
                    id=step_config.get("id", str(uuid.uuid4())),
                    layer=step_config.get("layer", "compute-script"),
                    input=step_config.get("input", {})
                )
                
                # Выполняем шаг
                start_time = datetime.now()
                try:
                    result = await self._execute_step(step)
                    step.output = result
                except Exception as e:
                    step.error = str(e)
                    logger.error(f"Ошибка выполнения шага {step.id}: {e}")
                
                step.execution_time = (datetime.now() - start_time).total_seconds()
                execution.steps.append(step)
                
                # Если шаг завершился с ошибкой, останавливаем выполнение
                if step.error:
                    execution.status = "failed"
                    break
            
            if execution.status != "failed":
                execution.status = "completed"
            
        except Exception as e:
            execution.status = "failed"
            logger.error(f"Ошибка выполнения JALM {execution_id}: {e}")
        
        finally:
            execution.completed_at = datetime.now()
            if execution.started_at:
                execution.total_time = (execution.completed_at - execution.started_at).total_seconds()
    
    async def _execute_step(self, step: JALMStep) -> Dict[str, Any]:
        """Выполнение отдельного шага"""
        layer = step.layer
        if layer not in self.supported_layers:
            raise ValueError(f"Неподдерживаемый слой: {layer}")
        
        executor = self.supported_layers[layer]
        return await executor(step.input)
    
    async def _execute_http(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение HTTP-запросов"""
        import requests
        
        method = input_data.get("method", "GET")
        url = input_data.get("url")
        headers = input_data.get("headers", {})
        body = input_data.get("body")
        timeout = input_data.get("timeout", 30)
        
        if not url:
            raise ValueError("URL обязателен для HTTP-запросов")
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=body,
            timeout=timeout
        )
        
        return {
            "status": response.status_code,
            "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            "headers": dict(response.headers)
        }
    
    async def _execute_db(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение операций с БД"""
        # В реальной реализации здесь будет подключение к БД
        # Пока возвращаем мок-данные
        query = input_data.get("query", "")
        params = input_data.get("params", {})
        
        logger.info(f"Выполнение DB запроса: {query} с параметрами {params}")
        
        return {
            "rows": [{"id": 1, "name": "test"}],
            "row_count": 1,
            "execution_time": 0.001
        }
    
    async def _execute_file(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение файловых операций"""
        operation = input_data.get("operation", "read")
        path = input_data.get("path")
        
        if not path:
            raise ValueError("Путь обязателен для файловых операций")
        
        if operation == "read":
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"content": content}
        
        elif operation == "write":
            content = input_data.get("content", "")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True}
        
        else:
            raise ValueError(f"Неподдерживаемая операция: {operation}")
    
    async def _execute_script(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение скриптов"""
        script = input_data.get("script", "")
        language = input_data.get("language", "py")
        variables = input_data.get("variables", {})
        
        if not script:
            raise ValueError("Скрипт обязателен")
        
        # Создаём временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
            f.write(script)
            temp_file = f.name
        
        try:
            # Выполняем скрипт
            if language == "py":
                result = subprocess.run(
                    ["python", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env={**os.environ, **variables}
                )
            elif language == "js":
                result = subprocess.run(
                    ["node", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    env={**os.environ, **variables}
                )
            else:
                raise ValueError(f"Неподдерживаемый язык: {language}")
            
            return {
                "result": result.stdout.strip(),
                "error": result.stderr.strip() if result.stderr else None,
                "return_code": result.returncode
            }
        
        finally:
            os.unlink(temp_file)
    
    async def _execute_render(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение рендеринга"""
        template = input_data.get("template", "")
        data = input_data.get("data", {})
        render_type = input_data.get("type", "html")
        
        if render_type == "html":
            # Простой рендеринг HTML
            result = template.format(**data)
            return {"content": result, "type": "html"}
        
        elif render_type == "json":
            # Рендеринг JSON
            return {"content": json.dumps(data, ensure_ascii=False), "type": "json"}
        
        else:
            raise ValueError(f"Неподдерживаемый тип рендеринга: {render_type}")
    
    async def _execute_notify(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение уведомлений"""
        notification_type = input_data.get("type", "email")
        
        if notification_type == "email":
            # Мок отправки email
            return {"success": True, "message": "Email отправлен"}
        
        elif notification_type == "webhook":
            # Отправка webhook
            url = input_data.get("url")
            data = input_data.get("data", {})
            
            if not url:
                raise ValueError("URL обязателен для webhook")
            
            import requests
            response = requests.post(url, json=data, timeout=10)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code
            }
        
        else:
            raise ValueError(f"Неподдерживаемый тип уведомления: {notification_type}")
    
    def get_execution(self, execution_id: str) -> Optional[JALMExecution]:
        """Получение информации о выполнении"""
        return self.executions.get(execution_id)
    
    def list_executions(self) -> List[JALMExecution]:
        """Список всех выполнений"""
        return list(self.executions.values())

# Инициализация ядра
core_runner = CoreRunner()

# API endpoints
@app.post("/exec", response_model=Dict[str, str])
async def execute_jalm(request: ExecutionRequest, background_tasks: BackgroundTasks):
    """Запуск выполнения JALM-конфига"""
    try:
        execution_id = await core_runner.execute_jalm(
            request.jalm_config,
            request.timeout
        )
        logger.info(f"Запущено выполнение JALM: {execution_id}")
        return {"execution_id": execution_id}
    except Exception as e:
        logger.exception("Ошибка запуска выполнения JALM")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/exec/{execution_id}")
async def get_execution(execution_id: str):
    """Получение статуса выполнения"""
    execution = core_runner.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Выполнение не найдено")
    
    return execution

@app.get("/exec")
async def list_executions():
    """Список всех выполнений"""
    return core_runner.list_executions()

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "supported_layers": list(core_runner.supported_layers.keys())
    }

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "JALM Core Runner",
        "version": "1.0.0",
        "description": "Исполнительное ядро для JALM Full Stack"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888) 