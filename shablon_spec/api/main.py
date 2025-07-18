"""
Shablon Spec API Server
FastAPI сервер для управления шаблонами JALM
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import json
import os
import sys
from pathlib import Path
import hashlib

app = FastAPI(
    title="Shablon Spec API",
    description="API для управления шаблонами JALM",
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
class TemplateMetadata(BaseModel):
    id: str
    version: str
    hash: str
    description: str
    category: str
    tags: List[str]
    author: str
    file: str
    dependencies: Dict[str, Any]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    runtime: Dict[str, Any]

class TemplateExecutionRequest(BaseModel):
    template_id: str
    version: Optional[str] = None
    hash: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class TemplateExecutionResponse(BaseModel):
    template_id: str
    result: Dict[str, Any]
    execution_time: float
    status: str

class TemplateValidationRequest(BaseModel):
    jalm_content: str

class TemplateValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []

# Загрузка реестра шаблонов
def load_registry() -> Dict[str, Any]:
    """Загружает реестр шаблонов из JSON файла"""
    registry_path = Path(__file__).parent.parent / "registry" / "templates.json"
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"templates": [], "metadata": {"total_templates": 0}}

# Загрузка шаблона
def load_template(template_id: str, version: Optional[str] = None, 
                 hash: Optional[str] = None) -> tuple[Dict[str, Any], str]:
    """Загружает шаблон по ID, версии или хешу"""
    registry = load_registry()
    
    # Поиск шаблона
    target_template = None
    for template in registry["templates"]:
        if template["id"] == template_id:
            if version and template["version"] == version:
                target_template = template
                break
            elif hash and template["hash"] == hash:
                target_template = template
                break
            elif not version and not hash:
                target_template = template
                break
    
    if not target_template:
        raise HTTPException(status_code=404, detail=f"Шаблон {template_id} не найден")
    
    # Загрузка JALM файла
    template_file = Path(__file__).parent.parent / "templates" / target_template["file"]
    
    if not template_file.exists():
        raise HTTPException(status_code=500, detail=f"Файл {target_template['file']} не найден")
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            jalm_content = f.read()
        return target_template, jalm_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки шаблона: {str(e)}")

# Валидация JALM синтаксиса
def validate_jalm_syntax(jalm_content: str) -> TemplateValidationResponse:
    """Простая валидация JALM синтаксиса"""
    errors = []
    warnings = []
    
    lines = jalm_content.split('\n')
    
    # Проверка BEGIN/END
    begin_count = sum(1 for line in lines if line.strip().startswith('BEGIN'))
    end_count = sum(1 for line in lines if line.strip().startswith('END'))
    
    if begin_count != end_count:
        errors.append(f"Несоответствие BEGIN/END: {begin_count} BEGIN, {end_count} END")
    
    # Проверка IMPORT
    import_lines = [line for line in lines if line.strip().startswith('IMPORT')]
    if not import_lines:
        warnings.append("Шаблон не содержит импортов")
    
    # Проверка RUN
    run_lines = [line for line in lines if line.strip().startswith('RUN')]
    if not run_lines:
        warnings.append("Шаблон не содержит команд RUN")
    
    # Проверка WHEN
    when_lines = [line for line in lines if line.strip().startswith('WHEN')]
    if not when_lines:
        warnings.append("Шаблон не содержит условий WHEN")
    
    return TemplateValidationResponse(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )

# Генерация хеша
def generate_hash(content: str) -> str:
    """Генерирует хеш для контента"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:40]

# API endpoints
@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "Shablon Spec API",
        "version": "1.0.0",
        "description": "API для управления шаблонами JALM"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    registry = load_registry()
    return {
        "status": "healthy",
        "total_templates": registry["metadata"]["total_templates"],
        "categories": registry["metadata"]["categories"],
        "last_updated": registry["metadata"]["last_updated"]
    }

@app.get("/templates", response_model=List[TemplateMetadata])
async def list_templates(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    tag: Optional[str] = Query(None, description="Фильтр по тегу"),
    author: Optional[str] = Query(None, description="Фильтр по автору")
):
    """Список всех шаблонов с возможностью фильтрации"""
    registry = load_registry()
    templates = registry["templates"]
    
    # Фильтрация
    if category:
        templates = [t for t in templates if t.get("category") == category]
    if tag:
        templates = [t for t in templates if tag in t.get("tags", [])]
    if author:
        templates = [t for t in templates if t.get("author") == author]
    
    return templates

@app.get("/templates/{template_id}", response_model=TemplateMetadata)
async def get_template(
    template_id: str,
    version: Optional[str] = Query(None, description="Версия шаблона"),
    hash: Optional[str] = Query(None, description="Хеш шаблона")
):
    """Получение метаданных шаблона"""
    registry = load_registry()
    
    for template in registry["templates"]:
        if template["id"] == template_id:
            if version and template["version"] == version:
                return template
            elif hash and template["hash"] == hash:
                return template
            elif not version and not hash:
                return template
    
    raise HTTPException(status_code=404, detail=f"Шаблон {template_id} не найден")

@app.get("/templates/{template_id}/content")
async def get_template_content(
    template_id: str,
    version: Optional[str] = Query(None, description="Версия шаблона"),
    hash: Optional[str] = Query(None, description="Хеш шаблона")
):
    """Получение содержимого шаблона"""
    try:
        template, content = load_template(template_id, version, hash)
        return {
            "template_id": template_id,
            "metadata": template,
            "content": content,
            "hash": generate_hash(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/templates/{template_id}/execute", response_model=TemplateExecutionResponse)
async def execute_template(
    template_id: str,
    request: TemplateExecutionRequest
):
    """Выполнение шаблона (имитация)"""
    import time
    
    start_time = time.time()
    
    try:
        template, content = load_template(template_id, request.version, request.hash)
        
        # Имитация выполнения шаблона
        # В реальной реализации здесь была бы интеграция с core-runner
        
        execution_time = time.time() - start_time
        
        return TemplateExecutionResponse(
            template_id=template_id,
            result={
                "status": "executed",
                "template": template["id"],
                "version": template["version"],
                "execution_id": f"exec_{int(time.time())}",
                "message": "Шаблон выполнен успешно (имитация)"
            },
            execution_time=execution_time,
            status="success"
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return TemplateExecutionResponse(
            template_id=template_id,
            result={"error": str(e)},
            execution_time=execution_time,
            status="error"
        )

@app.post("/templates/validate", response_model=TemplateValidationResponse)
async def validate_template(request: TemplateValidationRequest):
    """Валидация JALM синтаксиса"""
    return validate_jalm_syntax(request.jalm_content)

@app.post("/templates/upload")
async def upload_template(
    file: UploadFile = File(...),
    template_id: Optional[str] = Query(None, description="ID шаблона"),
    version: Optional[str] = Query(None, description="Версия шаблона")
):
    """Загрузка нового шаблона"""
    try:
        content = await file.read()
        jalm_content = content.decode('utf-8')
        
        # Валидация
        validation = validate_jalm_syntax(jalm_content)
        if not validation.is_valid:
            return {
                "status": "error",
                "errors": validation.errors,
                "warnings": validation.warnings
            }
        
        # Генерация хеша
        template_hash = generate_hash(jalm_content)
        
        return {
            "status": "success",
            "template_id": template_id or file.filename.replace('.jalm', ''),
            "version": version or "1.0.0",
            "hash": template_hash,
            "file_size": len(content),
            "validation": validation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")

@app.get("/categories")
async def get_categories():
    """Получение списка категорий"""
    registry = load_registry()
    return {
        "categories": registry["metadata"]["categories"],
        "total": len(registry["metadata"]["categories"])
    }

@app.get("/categories/{category}/templates")
async def get_templates_by_category(category: str):
    """Получение шаблонов по категории"""
    registry = load_registry()
    templates = [t for t in registry["templates"] if t.get("category") == category]
    
    return {
        "category": category,
        "templates": templates,
        "count": len(templates)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 