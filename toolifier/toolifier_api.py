from fastapi import FastAPI, Request
from pydantic import BaseModel
from agents.toolifier.tool_api_catalog_gen import generate_tool_api_catalog
from agents.toolifier.jalm_manifest_gen import generate_jalm_manifest

app = FastAPI()

class ToolifyRequest(BaseModel):
    agent_name: str
    intent_name: str
    method: str
    url: str
    params: list

@app.post("/toolify")
def toolify(request: ToolifyRequest):
    catalog = generate_tool_api_catalog(
        intent_name=request.intent_name,
        method=request.method,
        url=request.url,
        params=request.params
    )
    manifest = generate_jalm_manifest(
        agent_name=request.agent_name,
        intent_names=[request.intent_name]
    )
    return {
        "tool_api_catalog.json": catalog,
        f"{request.agent_name}.jalm.json": manifest
    }