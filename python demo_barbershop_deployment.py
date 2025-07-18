📦 **JALM FULL STACK — B.O.M. 2024-06-12**  
(root: `/jalm-stack/`)


| Компонент | Что делает | Артефакт | Source |
|-----------|------------|----------|--------|
| **Research Layer** | сбор исходных действий / паттернов | `research/*.csv` | этап 1 |
| **Core Templates** | готовые типовые решения (widget, booking, CRON и т.д.) | `catalog/*.template.json` | этап 6 (templates) |
| **Tula Registry** | микро-исполнители функций (FastAPI, Lambda, Go) | `tool_catalog/*.api.json` | этап 6 (tulas) |
| **Runner Engine** | среда выполнения tula/шаблонов, изоляция, шедулер | `catalog/core-runner.engine.json` | этап 6 |
| **Context7 Helper** | поиск готового кода | `scripts/collector.py / Context7 API` | этап 4 |
| **Packaging Wizard** | cookiecutter → Dockerfile → CI | `registry-wizard/` | этап 5 |
| **CLI** | однострочные `jalms up booking_light` | `cli/bin/jalm` |
| **External Aries** | Market place UI | `ui-market/` |
| **Runtime deps** | `docker-compose.yml` + `infra/postgres` + `redis` |


---


🚀 Локальный старт всего стека  
```
git clone git@github.com:jalm/jalm-stack.git
cd jalm-stack
docker compose up   # поднимается:
# - catalog (catalog-ui)
# - core-runner
# - postgres
# - redis
# - registry-wizard watcher
```


---


🔚 Чего не хватало  
- единого `docker-compose.yml` в корне (теперь есть)  
- единой `diagram-architecture.mermaid` (можно сгенерить из `.yaml`)  
- README-файла с cross-references (добавляется в корне)


→ стек полностью заложен.  ```markdown
# JALM-Stack README
Unified 6-layer meta-framework (research → runtime) for no-/low-code micro-assembly.


## 📦 Contents
- `/research/`         – raw actions, patterns, datasets
- `/templates/`        – cookiecutter micro-frontends & services
- `/tulas/`            – compiled function bundles
- `/core-runner/`      – execution engine
- `/tool_catalog/`     – registry JSON(indexes)
- `/docker-compose.yml` – one-liner runtime
- `Makefile`           – task flows
- `/docs/`             – API & architecture


---


## Quick-Start (local)
```bash
git clone https://github.com/jalm/stack.git
cd stack
docker compose up        # spins-up:  
# - catalog-ui (http://localhost:3000)
# - core-runner (port 8888)
# - postgres://localhost:5432/jalm
```


Access the **Builder Frontend** at http://localhost:3000  
Drag-in templates, hit “Deploy” → handled by `/core-runner`.


---


## 6-Stage Pipeline
1. **Collect**: interview → `research/raw_actions.csv` / `raw_patterns.csv`
2. **Cluster**: `research/grouped.json` (8 domains)
3. **Step-Map**: per-cluster micro-flow YAML cards `docs/step_cards/*.yaml`
4. **Context7**: auto-search snippets → `tool_candidates/`
5. **Wrap**: cookiecutter builds → `templates/` & `tulas/`)
6. **Publish**: registry files `tool_catalog/*.api.json` & `*.template.json`


Run each stage explicitly:
```bash
make stage-1   # Collect
make stage-2   # Cluster
...
make stage-6   # Publish
```


---


## Artifacts


| Stream       | Path                          | Purpose                                                |
|--------------|-------------------------------|--------------------------------------------------------|
| RESEARCH     | `research/raw_*.csv`          | Source material (actions & patterns)                   |
| TEMPLATES    | `templates/{name}/`           | Instant-fork widgets / services                        |
| TULAS        | `tulas/{name}/`               | micro-API bundles (docker-ready)                       |
| ENGINE       | `catalog/core-runner.engine.json` | single image ID for sandboxed execution            |
| REGISTRY     | `tool_catalog/*.[api/template].json` | searchable repo for CLI & frontend           |


---


## Dev Workflow (scenarios)


### 1. Add new business action  
```bash
echo 'pick_service,client,widget,daily,payment' \
  >> research/raw_actions.csv
make stage-2 stage-3 stage-4
```
A proposed CI step auto-wraps changes and opens a PR.


### 2. Experiment with template
```bash
make up template=booking_light
docker run -p 4000:80 jalm/templates_booking_light
```


### 3. Override engine layer
```bash
make kernel_build   # rebuilds core-runner
make kernel_push
docker compose up --force-recreate core-runner
```


---


## API Overview
| Component         | Endpoint                                      | Auth | Docs |
|-------------------|-----------------------------------------------|------|------|
| `catalog-ui`      | `GET /v1/templates`, `/v1/apis`               | none | Swagger |
| `core-runner`     | `POST /exec/{tula_id}`                        | JWT  | http://localhost:8888/docs |
| `registry webhook`| `POST /hooks/push` (GitHub Actions)           | secret | – |


---


## Environment (defaults)
```env
POSTGRES_URL=postgres://jalm:secret@db:5432/jalm
REDIS_URL=redis://redis:6379
REGISTRY_TOKEN=your_github_token
```


---


## Contributing
1. Add a支行big pattern as `/research/patterns_pr_<id>.csv`
2. Open PR → CI runs stages 2-6, produces preview branch.
3. Merge → registry is auto-updated.


License: MIT  
Discord: https://discord.gg/jalm-stack
```       Реальная трудоёмкость (человеко-часы)


| Участок                       | Новички | Сильная команда* |
|------------------------------|---------|------------------|
| **Research + data** (st.1–2) | 40ч     | 10ч              |
| **Context7 ingestion** (st.4)| 20ч     | 6ч               |
| **CI tasks automation**      | 80ч     | 25ч              |
| **core-runner**              | 120ч    | 35ч              |
| **packaging wizard**         | 60ч     | 20ч              |
| **registry + UI catalog**    | 90ч     | 25ч              |
| **quality, tests, swagger**  | 70ч     | 20ч              |
| **docs/docker-compose**      | 30ч     | 6ч               |
| **contingency**              | 40ч     | 10ч              |
| **Итого**                    | **530 ч** | **160 ч**        |


*«Сильная» = три разраба (full-staff), знающих JALM stack за 18 м. ➞ до релиза **1 неделя**.
