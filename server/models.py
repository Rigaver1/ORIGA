from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class SupplierItem(BaseModel):
    title: str
    url: str
    image_urls: List[str] = Field(default_factory=list)
    price_min_cny: Optional[float] = None
    price_max_cny: Optional[float] = None
    moq: Optional[int] = None
    shop_name: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_factory: bool = False
    is_factory_confidence: float = 0.0
    audited: bool = False
    certifications: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    years_active: Optional[int] = None
    contacts: Optional[str] = None
    pack: Optional[str] = None
    score: float = 0.0
    captured_at: datetime = Field(default_factory=datetime.utcnow)


class SearchParams(BaseModel):
    q: str
    mode: Literal["fast", "precise"] = "fast"
    pages: int = 1
    only_factories: bool = True
    audited_only: bool = True
    min_years: int = 0
    moq_max: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    region: Optional[str] = None
    concurrency: int = 3
    timeout: float = 15.0
    proxy: Optional[str] = None
    cookie: Optional[str] = None
    online: bool = True
    render: bool = False
    offline_demo: bool = False


class RFQRequest(BaseModel):
    lang: Literal["ru", "en", "cn"]
    title: str
    url: Optional[str] = None
    image_url: Optional[str] = None
    price_range: Optional[str] = None
    moq: Optional[int] = None
    incoterms: Optional[str] = None
    required_certs: List[str] = Field(default_factory=list)
    qty: Optional[int] = None
    custom_note: Optional[str] = None


class RFQResponse(BaseModel):
    path: str
    preview: str


class DDPInput(BaseModel):
    exw_or_fob_cny: float
    qty: int
    cbm_total: Optional[float] = None
    gw_total: Optional[float] = None
    duty_rate_pct: float
    vat_rate_pct: float
    freight_total_cny: float = 0.0
    freight_total_rub: float = 0.0
    inland_cn_cny: float = 0.0
    inland_ru_rub: float = 0.0
    insurance_pct: float = 0.0
    mode: Literal["air", "air_express", "sea_lcl", "rail_lcl", "fcl20", "fcl40", "fcl40hq"] = "sea_lcl"
    fx_source: Literal["cbr", "manual"] = "cbr"
    fx_cny_rub: Optional[float] = None


class DDPResult(BaseModel):
    fx_used_cny_rub: float
    goods_rub: float
    freight_rub: float
    inland_rub: float
    insurance_rub: float
    duty_rub: float
    vat_rub: float
    total_rub: float
    per_unit_rub: float
    mode: str
    ts: datetime