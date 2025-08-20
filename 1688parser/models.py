from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PriceTier(BaseModel):
	min_qty: int = Field(..., ge=1)
	max_qty: Optional[int] = Field(None, ge=1)
	price: float = Field(..., ge=0)
	currency: str = Field("CNY")


class Dimensions(BaseModel):
	length: Optional[float] = None
	width: Optional[float] = None
	height: Optional[float] = None
	unit: Optional[str] = None


class Weight(BaseModel):
	value: Optional[float] = None
	unit: Optional[str] = None


class SKU(BaseModel):
	sku_id: Optional[str] = None
	attrs: Dict[str, str] = Field(default_factory=dict)
	price: Optional[float] = None
	currency: Optional[str] = "CNY"
	stock: Optional[int] = None
	image: Optional[str] = None


class Images(BaseModel):
	cover: Optional[str] = None
	gallery: List[str] = Field(default_factory=list)
	variants: Dict[str, str] = Field(default_factory=dict)


class Product(BaseModel):
	offer_id: Optional[str] = None
	url: Optional[str] = None
	title: Optional[str] = None
	category: Optional[str] = None
	attributes: Dict[str, str] = Field(default_factory=dict)
	description_text: Optional[str] = None
	description_html: Optional[str] = None
	images: Images = Field(default_factory=Images)
	min_order: Optional[int] = None
	price_tiers: List[PriceTier] = Field(default_factory=list)
	sku_list: List[SKU] = Field(default_factory=list)
	weight: Weight = Field(default_factory=Weight)
	dimensions: Dimensions = Field(default_factory=Dimensions)
	package_info: Optional[str] = None
	origin_location: Optional[str] = None
	lead_time: Optional[str] = None
	stock: Optional[int] = None
	shop_name: Optional[str] = None
	shop_id: Optional[str] = None
	seller_company: Optional[str] = None
	seller_contact: Optional[str] = None
	ratings: Optional[float] = None
	sold_count: Optional[int] = None
	reviews_count: Optional[int] = None
	extra: Dict[str, Any] = Field(default_factory=dict)
