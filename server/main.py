from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import ORJSONResponse, FileResponse
from sse_starlette.sse import EventSourceResponse
from typing import List, Optional

from .models import SupplierItem, SearchParams, RFQRequest, RFQResponse, DDPInput, DDPResult
from .search_1688 import search_1688_list, search_1688_stream, search_1688_offline_stream
from .exporters import export_suppliers_to_excel, export_to_csv_json
from .rfq import generate_rfq
from .ddp import calculate_ddp_async
from .config import settings

app = FastAPI(title="CargoOS 1688 — Ядро (RU)", default_response_class=ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Serve frontend and exports
app.mount("/static", StaticFiles(directory="web", html=False), name="static")
app.mount("/exports", StaticFiles(directory="exports", html=False), name="exports")

@app.get("/")
async def root_index():
    return FileResponse("web/index.html")


@app.get("/docs-ru")
async def docs_ru():
    return FileResponse("server/api_docs_ru.md")


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/search_1688", response_model=List[SupplierItem])
async def search_endpoint(
    q: str = Query(..., description="CN-запрос"),
    mode: str = Query("fast", pattern="^(fast|precise)$"),
    pages: int = Query(1, ge=1, le=20),
    online: bool = Query(True),
    only_factories: bool = Query(True),
    audited_only: bool = Query(True),
    min_years: int = Query(0, ge=0, le=30),
    moq_max: Optional[int] = Query(None, ge=1),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    region: Optional[str] = Query(None),
    concurrency: int = Query(3, ge=1, le=10),
    timeout: float = Query(15.0, ge=1.0, le=60.0),
    proxy: Optional[str] = Query(None),
    cookie: Optional[str] = Query(None),
    render: bool = Query(False),
    offline_demo: bool = Query(False)
):
    params = SearchParams(
        q=q,
        mode=mode,
        pages=pages,
        only_factories=only_factories,
        audited_only=audited_only,
        min_years=min_years,
        moq_max=moq_max,
        price_min=price_min,
        price_max=price_max,
        region=region,
        concurrency=concurrency,
        timeout=timeout,
        proxy=proxy,
        cookie=cookie,
        online=online,
        render=render,
        offline_demo=offline_demo
    )
    items = await search_1688_list(params)
    return items


@app.get("/search_1688/stream")
async def search_stream(
    q: str,
    pages: int = 1,
    concurrency: int = 3,
    timeout: float = 15.0,
    proxy: Optional[str] = None,
    cookie: Optional[str] = None,
    render: bool = False,
    offline_demo: bool = False,
    mode: str = "fast",
    only_factories: bool = True,
    audited_only: bool = True,
    min_years: int = 0,
    moq_max: Optional[int] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    region: Optional[str] = None
):
    params = SearchParams(
        q=q,
        mode=mode,
        pages=pages,
        only_factories=only_factories,
        audited_only=audited_only,
        min_years=min_years,
        moq_max=moq_max,
        price_min=price_min,
        price_max=price_max,
        region=region,
        concurrency=concurrency,
        timeout=timeout,
        proxy=proxy,
        cookie=cookie,
        online=True,
        render=render,
        offline_demo=offline_demo
    )

    async def event_generator():
        yield {"event": "status", "data": "start"}
        agen = search_1688_offline_stream(params) if offline_demo else search_1688_stream(params)
        async for evt in agen:
            yield {"event": evt["type"], "data": evt["data"]}
        yield {"event": "status", "data": "done"}

    return EventSourceResponse(event_generator())


@app.post("/export/xlsx")
async def export_xlsx(items: List[SupplierItem] = Body(...)):
    # Fallback to CSV path when Excel engine unavailable; still return path
    try:
        path = export_suppliers_to_excel(items)
    except Exception:
        path = export_to_csv_json(items, "csv")
    return {"path": path}


@app.post("/export/{fmt}")
async def export_other(fmt: str, items: List[SupplierItem] = Body(...)):
    path = export_to_csv_json(items, fmt)
    return {"path": path}


@app.post("/rfq", response_model=RFQResponse)
async def rfq_endpoint(req: RFQRequest):
    return generate_rfq(req)


@app.post("/calc/ddp", response_model=DDPResult)
async def calc_ddp(req: DDPInput):
    return await calculate_ddp_async(req)