import json
import os
import time
from typing import Optional
import httpx

CACHE_TTL_SEC = 3600
CACHE_PATH = "data/cache/fx_cny_rub.json"

CBR_DAILY_XML = "https://www.cbr.ru/scripts/XML_daily.asp"


async def fetch_cbr_cny_rub_rate() -> float:
    async with httpx.AsyncClient(timeout=10.0) as client:
        # CBR XML contains CNY nominal and value in RUB
        resp = await client.get(CBR_DAILY_XML)
        resp.raise_for_status()
        text = resp.text
        # naive parse
        if "ID=\"R01375\"" not in text and "Китайский юань" not in text:
            raise RuntimeError("CBR response missing CNY")
        # Extract <Valute ID="R01375"> ... <Nominal>10</Nominal> <Value>???</Value>
        import re
        nom_m = re.search(r"<Nominal>(\d+)</Nominal>\s*<Name>Китайский юань</Name>\s*<Value>([0-9,]+)</Value>", text)
        if not nom_m:
            # fallback try any CNY block
            nom_m = re.search(r"<Name>Китайский юань</Name>[\s\S]*?<Nominal>(\d+)</Nominal>[\s\S]*?<Value>([0-9,]+)</Value>", text)
        if not nom_m:
            raise RuntimeError("Cannot parse CNY rate from CBR")
        nominal = float(nom_m.group(1))
        value = float(nom_m.group(2).replace(',', '.'))
        return value / nominal


def load_cached_rate() -> Optional[float]:
    try:
        if not os.path.exists(CACHE_PATH):
            return None
        if time.time() - os.path.getmtime(CACHE_PATH) > CACHE_TTL_SEC:
            return None
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return float(data.get('cny_rub'))
    except Exception:
        return None


def save_cached_rate(rate: float) -> None:
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump({'cny_rub': rate, 'ts': time.time()}, f)


async def get_cny_rub_rate(source: str = 'cbr', manual: Optional[float] = None) -> float:
    if source == 'manual':
        if manual is None:
            raise ValueError("Не указан ручной курс fx_cny_rub при fx_source=manual")
        return float(manual)
    # cbr path
    cached = load_cached_rate()
    if cached is not None:
        return cached
    rate = await fetch_cbr_cny_rub_rate()
    save_cached_rate(rate)
    return rate