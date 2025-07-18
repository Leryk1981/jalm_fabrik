from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import tempfile
from saas_provisioner import SaasProvisioner
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import logging
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger("saas-api")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Инициализация оркестратора с путями к шаблонам
provisioner = SaasProvisioner(
    dockerfile_template_path="./Dockerfile.template",
    compose_template_path="./docker-compose.template.yml"
)

@app.post("/provision")
async def provision(jalm_file: UploadFile = File(...)):
    """
    Принимает JALM-конфиг (YAML-файл), разворачивает инстанс, возвращает URL.
    """
    try:
        logger.info("Получен запрос на деплой JALM-конфига: %s", jalm_file.filename)
        # Сохраняем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jalm") as tmp:
            content = await jalm_file.read()
            tmp.write(content)
            tmp_path = tmp.name
        logger.info("Временный JALM-файл сохранён: %s", tmp_path)
        # Запускаем оркестратор
        url = provisioner.provision(tmp_path)
        logger.info("Инстанс успешно развернут: %s", url)
        # Удаляем временный файл
        os.remove(tmp_path)
        return JSONResponse(content={"url": url})
    except Exception as e:
        logger.exception("Ошибка при деплое JALM-инстанса")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/llm-jalm")
async def llm_jalm(query: str = Body(..., embed=True)):
    """
    Принимает текстовый запрос пользователя, возвращает JALM-конфиг, сгенерированный через OpenRouter.
    """
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "sk-...")
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    prompt = f"""
    Ты — помощник для генерации JALM-конфига для SaaS-конструктора. Сгенерируй только валидный YAML по стандарту JALM, строго без markdown-обрамления, без пояснений, без тройных кавычек, без комментариев, без пустых ключей, без лишних или неиспользуемых полей. Только корректная структура JALM, пригодная для автоматического деплоя. Любые отклонения от стандарта запрещены.
    Запрос: {query}
    Ответ:
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "Referer": "http://localhost:8000/",
        "X-Title": "SaaS JALM Generator"
    }
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "Ты — генератор JALM-конфигов для SaaS."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800,
        "temperature": 0.2
    }
    try:
        logger.info("Запрос к OpenRouter для генерации JALM: %s", query)
        resp = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        jalm_yaml = result["choices"][0]["message"]["content"].strip()
        logger.info("JALM-конфиг успешно сгенерирован через LLM")
        return JSONResponse(content={"jalm": jalm_yaml})
    except HTTPError as e:
        logger.error('OpenRouter error: %s', e.response.text)
        logger.exception("Ошибка OpenRouter при генерации JALM")
        raise HTTPException(status_code=500, detail=f"LLM error: {e.response.text}")
    except Exception as e:
        logger.exception("Ошибка при генерации JALM через LLM")
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    logger.info("UI: Открыта главная страница")
    return templates.TemplateResponse("main.html", {"request": request, "jalm": None, "url": None, "error": None}, media_type="text/html; charset=utf-8")

@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, user_query: str = Form(...)):
    # Запрос к /llm-jalm
    try:
        logger.info("UI: Запрос на генерацию JALM через LLM: %s", user_query)
        # Прямой вызов функции llm_jalm
        response = await llm_jalm(query=user_query)
        import json
        body_bytes = bytes(response.body)
        jalm = json.loads(body_bytes.decode("utf-8"))["jalm"]
        return templates.TemplateResponse("main.html", {"request": request, "jalm": jalm, "url": None, "error": None}, media_type="text/html; charset=utf-8")
    except Exception as e:
        logger.exception("Ошибка в UI при генерации JALM через LLM")
        return templates.TemplateResponse("main.html", {"request": request, "jalm": None, "url": None, "error": str(e)}, media_type="text/html; charset=utf-8")

@app.post("/deploy", response_class=HTMLResponse)
async def deploy(request: Request, jalm_text: str = Form(...)):
    # Очищаем markdown-обрамление (```yaml и ```) если есть
    lines = jalm_text.splitlines()
    filtered = [line for line in lines if not line.strip().startswith('```')]
    clean_jalm = '\n'.join(filtered)
    import yaml
    # Серверная валидация YAML
    try:
        yaml.safe_load(clean_jalm)
    except yaml.YAMLError:
        logger.warning("Ошибка валидации YAML при деплое, деплой не выполнен")
        # Не показываем ошибку пользователю, просто не деплоим
        return templates.TemplateResponse("main.html", {"request": request, "jalm": clean_jalm, "url": None, "error": None}, media_type="text/html; charset=utf-8")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jalm") as tmp:
            tmp.write(clean_jalm.encode("utf-8"))
            tmp_path = tmp.name
        logger.info("Деплой JALM: временный файл %s", tmp_path)
        url = provisioner.provision(tmp_path)
        logger.info("Инстанс успешно развернут: %s", url)
        os.remove(tmp_path)
        return templates.TemplateResponse("main.html", {"request": request, "jalm": clean_jalm, "url": url, "error": None}, media_type="text/html; charset=utf-8")
    except Exception as e:
        logger.exception("Ошибка при деплое JALM-инстанса (UI)")
        return templates.TemplateResponse("main.html", {"request": request, "jalm": clean_jalm, "url": None, "error": str(e)}, media_type="text/html; charset=utf-8")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 