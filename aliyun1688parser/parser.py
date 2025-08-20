from __future__ import annotations

import json
import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from .models import Dimensions, Images, PriceTier, Product, SKU, Weight
from .http_client import fetch_page


def _extract_first(soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
	for selector in selectors:
		n = soup.select_one(selector)
		if n and n.get_text(strip=True):
			return n.get_text(strip=True)
	return None


def _extract_meta(soup: BeautifulSoup, names: List[str], prop: str = "content") -> Optional[str]:
	for name in names:
		el = soup.select_one(f'meta[name="{name}"]') or soup.select_one(f'meta[property="{name}"]')
		if el and el.get(prop):
			return el.get(prop)
	return None


def _extract_offer_id_from_url(url: str) -> Optional[str]:
	m = re.search(r"/offer/(\d+)\.html", url)
	if m:
		return m.group(1)
	m = re.search(r"offerId=(\d+)", url)
	if m:
		return m.group(1)
	return None


def _find_json_array(text: str, key: str) -> Optional[List[dict]]:
	pattern = rf'"{re.escape(key)}"\s*:\s*(\[.*?\])'
	m = re.search(pattern, text, flags=re.S)
	if not m:
		return None
	try:
		return json.loads(m.group(1))
	except Exception:  # noqa: BLE001
		return None


def _find_json_object(text: str, key: str) -> Optional[Dict]:
	# Build regex without f-string to safely include literal braces
	pattern = '"' + re.escape(key) + '"\\s*:\\s*(\{{\\s*[\\s\\S]*?\}})'
	m = re.search(pattern, text, flags=re.S)
	if not m:
		return None
	try:
		return json.loads(m.group(1))
	except Exception:  # noqa: BLE001
		return None


def _safe_float(v: Optional[str]) -> Optional[float]:
	if v is None:
		return None
	try:
		return float(v)
	except Exception:  # noqa: BLE001
		return None


def _collect_images(soup: BeautifulSoup) -> Images:
	images = Images()
	images.cover = _extract_meta(soup, ["og:image", "twitter:image"])
	# Gallery heuristics
	for sel in [
		".image-list img",
		".images img",
		".tab-content img",
		".mod-detail-gallery img",
		"img[data-img], img[data-lazyload], img[src]",
	]:
		for img in soup.select(sel):
			src = img.get("data-img") or img.get("data-lazyload") or img.get("src")
			if not src:
				continue
			src = src.strip()
			if not src or len(src) < 8:
				continue
			if src not in images.gallery:
				images.gallery.append(src)
	return images


def _parse_price_tiers(page_text: str) -> List[PriceTier]:
	result: List[PriceTier] = []
	# Try known keys
	for key in ["priceRanges", "salePriceRange", "priceRange"]:
		arr = _find_json_array(page_text, key)
		if not arr:
			continue
		for tier in arr:
			min_qty = int(tier.get("startQuantity") or tier.get("minQuantity") or tier.get("min") or 1)
			max_qty = tier.get("endQuantity") or tier.get("maxQuantity") or tier.get("max")
			price = tier.get("price") or tier.get("rangePrice") or tier.get("salePrice")
			if isinstance(price, list):
				price = price[0] if price else None
			try:
				result.append(PriceTier(min_qty=min_qty, max_qty=int(max_qty) if max_qty else None, price=float(price), currency="CNY"))
			except Exception:  # noqa: BLE001
				continue
	if result:
		return result
	# Fallback: parse simple price pattern
	for m in re.finditer(r"(\d+(?:\.\d+)?)\s*元", page_text):
		try:
			price_val = float(m.group(1))
			result.append(PriceTier(min_qty=1, max_qty=None, price=price_val, currency="CNY"))
		except Exception:  # noqa: BLE001
			pass
	return result


def _parse_min_order(text: str) -> Optional[int]:
	# Try a few patterns including Chinese labels
	for pat in [
		r"起订量\s*:?\s*(\d+)",
		r"最小起订\s*:?\s*(\d+)",
		r"Minimum Order\D+(\d+)",
	]:
		m = re.search(pat, text)
		if m:
			try:
				return int(m.group(1))
			except Exception:  # noqa: BLE001
				continue
	return None


def _parse_sku(page_text: str) -> List[SKU]:
	# Try to find skuMap (1688 often uses skuMap + skuProps)
	skus: List[SKU] = []
	# skuMap: {";颜色:红色;尺寸:M;": {price:..., skuId:..., canBookCount:...}}
	m = re.search(r'"skuMap"\s*:\s*(\{[\s\S]*?\})', page_text)
	props = _find_json_array(page_text, "skuProps")
	key_map: List[Dict[str, str]] = []
	if props:
		for p in props:
			name = p.get("prop") or p.get("name")
			for v in p.get("value") or p.get("values") or []:
				kv = {
					"name": name,
					"value": v.get("name") or v.get("value") or v.get("title"),
					"image": v.get("imageUrl") or v.get("image") or None,
				}
				key_map.append(kv)
	if m:
		try:
			sku_map = json.loads(m.group(1))
		except Exception:  # noqa: BLE001
			sku_map = {}
		for key, data in sku_map.items():
			attrs: Dict[str, str] = {}
			for part in key.split(";"):
				part = part.strip().strip(";")
				if not part:
					continue
				if ":" in part:
					k, v = part.split(":", 1)
					attrs[k.strip()] = v.strip()
			price = _safe_float(str(data.get("price") or data.get("discountPrice") or data.get("salePrice") or ""))
			stock = data.get("canBookCount") or data.get("stock")
			skus.append(
				SKU(
					sku_id=str(data.get("skuId")) if data.get("skuId") is not None else None,
					attrs=attrs,
					price=price,
					currency="CNY" if price is not None else None,
					stock=int(stock) if isinstance(stock, (int, float, str)) and str(stock).isdigit() else None,
				)
			)
	return skus


def _parse_attributes_table(soup: BeautifulSoup) -> Dict[str, str]:
	attrs: Dict[str, str] = {}
	for table_sel in [
		".attributes-list table",
		"table[class*=attributes]",
		".mod-detail-attributes table",
		".attr-list table",
	]:
		for row in soup.select(f"{table_sel} tr"):
			cells = [c.get_text(strip=True) for c in row.select("th,td")]
			if len(cells) >= 2:
				key = cells[0]
				val = "; ".join(cells[1:])
				if key and val and key not in attrs:
					attrs[key] = val
	return attrs


def _parse_weight_and_dimensions(attrs: Dict[str, str]) -> (Weight, Dimensions):
	weight = Weight()
	dim = Dimensions()
	weight_keys = ["重量", "毛重", "净重", "Weight"]
	dim_keys = ["尺寸", "包装尺寸", "外箱尺寸", "Dimension", "Size"]

	def _num_in(text: str) -> Optional[float]:
		m = re.search(r"(\d+(?:\.\d+)?)", text)
		return float(m.group(1)) if m else None

	for k, v in attrs.items():
		if any(wk in k for wk in weight_keys):
			weight.value = _num_in(v)
			if "kg" in v.lower():
				weight.unit = "kg"
			elif "g" in v.lower():
				weight.unit = "g"
		elif any(dk in k for dk in dim_keys):
			# Attempt to find L*W*H
			nums = re.findall(r"\d+(?:\.\d+)?", v)
			if len(nums) >= 3:
				dim.length = float(nums[0])
				dim.width = float(nums[1])
				dim.height = float(nums[2])
			if any(u in v.lower() for u in ["cm", "厘米"]):
				dim.unit = "cm"
			elif any(u in v.lower() for u in ["mm", "毫米"]):
				dim.unit = "mm"
	return weight, dim


def _maybe_fetch_description(page_text: str, timeout: int, proxies: Optional[Dict[str, str]]) -> (Optional[str], Optional[str]):
	# Try to find descUrl
	m = re.search(r'"descUrl"\s*:\s*"(https?:\\/\\/[^"\\]+)"', page_text)
	if not m:
		m = re.search(r'descUrl\s*=\s*"(https?://[^"]+)"', page_text)
	if not m:
		return None, None
	desc_url = m.group(1).replace("\\/", "/")
	try:
		desc_html = fetch_page(desc_url, timeout=timeout, proxies=proxies)
		# Extract plain text quickly
		soup = BeautifulSoup(desc_html, "lxml")
		desc_text = soup.get_text(" ", strip=True)
		return desc_text, str(soup)
	except Exception:  # noqa: BLE001
		return None, None


def parse_product(html: str, url: str, timeout: int = 25, proxies: Optional[Dict[str, str]] = None) -> Product:
	soup = BeautifulSoup(html, "lxml")
	text = soup.get_text("\n", strip=True)

	product = Product()
	product.url = url
	product.offer_id = _extract_offer_id_from_url(url)

	product.title = (
		_extract_meta(soup, ["og:title", "twitter:title"]) or _extract_first(soup, ["h1", ".title", ".d-title"]) or (soup.title.get_text(strip=True) if soup.title else None)
	)
	product.category = _extract_first(soup, [
		".breadcrumb a:last-child",
		".mod-breadcrumb a:last-child",
		".detail-breadcrumb a:last-child",
	])
	product.images = _collect_images(soup)

	# Prices and min order
	product.price_tiers = _parse_price_tiers(html)
	product.min_order = _parse_min_order(text)

	# Attributes and derived logistics fields
	product.attributes = _parse_attributes_table(soup)
	weight, dim = _parse_weight_and_dimensions(product.attributes)
	product.weight = weight
	product.dimensions = dim

	# SKU
	product.sku_list = _parse_sku(html)

	# Shop info heuristics
	product.shop_name = _extract_meta(soup, ["og:site_name"]) or _extract_first(soup, [
		".company-name, .shop-name, a[title*=店], a[title*=公司]",
	])
	# Try to discover seller/company in text blocks
	for label in ["公司名称", "Company Name", "商家名称", "店铺名称"]:
		m = re.search(label + r"\s*[:：]\s*([\S ]{3,60})", text)
		if m and not product.seller_company:
			product.seller_company = m.group(1).strip()

	# Description, if discoverable via descUrl
	desc_text, desc_html = _maybe_fetch_description(html, timeout=timeout, proxies=proxies)
	product.description_text = desc_text
	product.description_html = desc_html

	# Origin / location
	for label in ["发货地", "产地", "Origin", "发源地", "所在地"]:
		m = re.search(label + r"\s*[:：]\s*([\S ]{2,40})", text)
		if m and not product.origin_location:
			product.origin_location = m.group(1).strip()

	# Rating / social proof (best-effort)
	m = re.search(r"(\d+(?:\.\d)?)\s*/\s*5\s*分", text)
	if m:
		try:
			product.ratings = float(m.group(1))
		except Exception:  # noqa: BLE001
			pass
	for lab, field in [("已售", "sold_count"), ("评价", "reviews_count")]:
		m = re.search(lab + r"\D*(\d+)", text)
		if m:
			try:
				setattr(product, field, int(m.group(1)))
			except Exception:  # noqa: BLE001
				pass

	return product

