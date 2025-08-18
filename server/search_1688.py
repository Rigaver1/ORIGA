import asyncio
import os
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx
from bs4 import BeautifulSoup
from .models import SupplierItem, SearchParams
from .utils import parse_price_range_cn, parse_moq_cn
from .scoring import score_supplier
from .config import settings


def normalize_item(raw: Dict[str, Any]) -> SupplierItem:
    price_min, price_max = parse_price_range_cn(raw.get('price_text') or '')
    moq = parse_moq_cn(raw.get('moq_text') or '')
    title = (raw.get('title') or '').strip()
    tags = raw.get('tags') or []
    audited = any(tag in (tags or []) for tag in ["实地认证", "实力商家"])
    years_active = raw.get('years_active')
    is_factory, conf, _trust, score, evidence = score_supplier(title, tags, years_active, audited)

    return SupplierItem(
        title=title or raw.get('url', '—'),
        url=raw.get('url') or '',
        image_urls=raw.get('image_urls') or [],
        price_min_cny=price_min,
        price_max_cny=price_max,
        moq=moq,
        shop_name=raw.get('shop_name'),
        location=raw.get('location'),
        tags=tags,
        is_factory=is_factory,
        is_factory_confidence=conf,
        audited=audited,
        certifications=raw.get('certifications') or [],
        evidence=evidence,
        years_active=years_active,
        score=score,
    )


async def fetch_page(client: httpx.AsyncClient, url: str, cookie: Optional[str]) -> str:
    headers = {
        "User-Agent": settings.user_agent,
        "Accept-Language": "zh-CN,zh;q=0.9,ru;q=0.8",
    }
    if cookie:
        headers["Cookie"] = cookie
    r = await client.get(url, headers=headers)
    if r.status_code in (403, 429):
        raise RuntimeError(f"Anti-bot status: {r.status_code}")
    r.raise_for_status()
    return r.text


def parse_search_html(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    cards: List[Dict[str, Any]] = []
    for a in soup.select('a'):
        href = a.get('href') or ''
        text = a.get_text(strip=True)
        if 'detail' in href and text:
            cards.append({
                'title': text,
                'url': href,
                'image_urls': [],
                'price_text': None,
                'moq_text': None,
                'shop_name': None,
                'location': None,
                'tags': [],
                'years_active': None,
            })
            if len(cards) >= 5:
                break
    return cards


async def search_1688_list(params: SearchParams) -> List[SupplierItem]:
    if params.offline_demo or not params.online:
        items = list(await _offline_items())
        return _apply_filters(items, params)

    base_url = "https://s.1688.com/selloffer/offer_search.htm"
    query = params.q
    pages = max(1, params.pages)

    results: List[SupplierItem] = []

    timeout = httpx.Timeout(params.timeout)
    limits = httpx.Limits(max_connections=params.concurrency)
    proxies = params.proxy
    async with httpx.AsyncClient(timeout=timeout, limits=limits, proxies=proxies) as client:
        sem = asyncio.Semaphore(params.concurrency)

        async def fetch_and_parse(page: int):
            async with sem:
                url = f"{base_url}?keywords={query}&page={page}"
                try:
                    html = await fetch_page(client, url, params.cookie)
                except Exception:
                    return []
                raw_cards = parse_search_html(html)
                return [normalize_item(r) for r in raw_cards]

        tasks = [fetch_and_parse(p + 1) for p in range(pages)]
        for coro in asyncio.as_completed(tasks):
            batch = await coro
            results.extend(batch)

    results = _apply_filters(results, params)
    results.sort(key=lambda x: (-(x.score or 0.0), (x.price_min_cny or 1e12)))
    return results


async def search_1688_stream(params: SearchParams) -> AsyncGenerator[Dict[str, str], None]:
    if params.offline_demo or not params.online:
        async for evt in search_1688_offline_stream(params):
            yield evt
        return

    base_url = "https://s.1688.com/selloffer/offer_search.htm"
    query = params.q
    pages = max(1, params.pages)

    timeout = httpx.Timeout(params.timeout)
    limits = httpx.Limits(max_connections=params.concurrency)
    proxies = params.proxy
    async with httpx.AsyncClient(timeout=timeout, limits=limits, proxies=proxies) as client:
        sem = asyncio.Semaphore(params.concurrency)

        async def fetch_and_parse(page: int):
            async with sem:
                url = f"{base_url}?keywords={query}&page={page}"
                try:
                    html = await fetch_page(client, url, params.cookie)
                except Exception:
                    return []
                raw_cards = parse_search_html(html)
                return [normalize_item(r) for r in raw_cards]

        tasks = [fetch_and_parse(p + 1) for p in range(pages)]
        for coro in asyncio.as_completed(tasks):
            batch = await coro
            for it in _apply_filters(batch, params):
                yield {"type": "item", "data": it.model_dump_json()}


async def search_1688_offline_stream(params: SearchParams) -> AsyncGenerator[Dict[str, str], None]:
    items = list(await _offline_items())
    items = _apply_filters(items, params)
    for it in items:
        yield {"type": "item", "data": it.model_dump_json()}


async def _offline_items() -> List[SupplierItem]:
    path = os.path.join(settings.offline_dir, "snapshot.html")
    if not os.path.exists(path):
        # Fallback sample data
        sample = [
            normalize_item({
                'title': '源头工厂 塑料瓶 OEM ODM',
                'url': 'https://detail.1688.com/offer/123.html',
                'image_urls': [],
                'price_text': '￥1.20-2.10',
                'moq_text': '起订量 500 个',
                'shop_name': '义乌市XX塑料制品厂',
                'location': '义乌',
                'tags': ['源头工厂', '支持OEM'],
                'years_active': 5,
            }),
            normalize_item({
                'title': '贸易公司 批发 帽子',
                'url': 'https://detail.1688.com/offer/456.html',
                'image_urls': [],
                'price_text': '1.28 起',
                'moq_text': 'MOQ 1000',
                'shop_name': '广州XX贸易公司',
                'location': '广州',
                'tags': ['批发'],
                'years_active': 2,
            }),
        ]
        return sample
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    raw_cards = parse_search_html(html)
    return [normalize_item(r) for r in raw_cards]


def _apply_filters(items: List[SupplierItem], params: SearchParams) -> List[SupplierItem]:
    out: List[SupplierItem] = []
    for it in items:
        if params.only_factories and not it.is_factory:
            continue
        if params.audited_only and not it.audited:
            continue
        if params.moq_max is not None and it.moq is not None and it.moq > params.moq_max:
            continue
        if params.price_min is not None and (it.price_min_cny or 0) < params.price_min:
            continue
        if params.price_max is not None and (it.price_max_cny or it.price_min_cny or 0) > params.price_max:
            continue
        out.append(it)
    out.sort(key=lambda x: (-(x.score or 0.0), (x.price_min_cny or 1e12)))
    return out