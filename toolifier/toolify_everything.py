import argparse
import json
from pathlib import Path
from agents.toolifier.tool_api_catalog_gen import generate_tool_api_catalog
from agents.toolifier.jalm_manifest_gen import generate_jalm_manifest

def save_json(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_tool_api_jalm_catalog(jalm_path, intent_name, method, url):
    if Path(jalm_path).exists():
        catalog = json.loads(Path(jalm_path).read_text(encoding="utf-8"))
    else:
        catalog = {
            "intent": "описать_инструменты",
            "context": {"назначение": "все разрешённые tool_api для агента"},
            "tool_api": [],
            "control": {},
            "meta": {"форма": "капсула_действия"}
        }
    catalog["tool_api"] = [e for e in catalog["tool_api"] if e["name"] != intent_name]
    catalog["tool_api"].append({
        "name": intent_name,
        "description": f"Агент выполняет действие по интенту: {intent_name}",
        "endpoint": url,
        "method": method
    })
    save_json(catalog, jalm_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True)
    parser.add_argument("--intent", required=True)
    parser.add_argument("--method", default="POST")
    parser.add_argument("--url", required=True)
    parser.add_argument("--input_schema", required=True, help="JSON string")
    parser.add_argument("--output_schema", required=True, help="JSON string")
    args = parser.parse_args()

    input_schema = json.loads(args.input_schema)
    output_schema = json.loads(args.output_schema)

    # 1. Генерация tool_api_catalog/<intent>.api.json
    full_catalog = {
        "name": args.intent,
        "intent": args.intent,
        "endpoint": args.url,
        "method": args.method,
        "input_schema": input_schema,
        "output_schema": output_schema,
        "notes": "",
        "origin": "generated"
    }
    save_json(full_catalog, f"barberflow/tool_api_catalog/{args.intent}.api.json")

    # 2. Обновление tool_api_catalog.jalm.json
    update_tool_api_jalm_catalog("barberflow/tool_api_catalog/tool_api_catalog.jalm.json",
                                  args.intent, args.method, args.url)

    # 3. Генерация .jalm.json манифеста агента
    manifest = generate_jalm_manifest(args.agent, [args.intent])
    save_json(manifest, f"barberflow/agents/{args.agent}.jalm.json")

    print("[OK] tool_api and jalm manifest created.")

if __name__ == "__main__":
    main()