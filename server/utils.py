import re
from typing import Optional, Tuple

PRICE_NEGOTIABLE_MARKERS = ["价格面议", "面议"]


def parse_price_range_cn(text: str) -> Tuple[Optional[float], Optional[float]]:
    if not text:
        return None, None
    txt = text.strip().replace("￥", "").replace(",", "")
    for marker in PRICE_NEGOTIABLE_MARKERS:
        if marker in txt:
            return None, None
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*[-~]\s*([0-9]+(?:\.[0-9]+)?)", txt)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:起|起步|以上)?", txt)
    if m:
        return float(m.group(1)), None
    return None, None


def parse_moq_cn(text: str) -> Optional[int]:
    if not text:
        return None
    txt = text.strip()
    m = re.search(r"(?:MOQ|起订量|起批量)\s*([0-9]+)", txt, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"([0-9]+)\s*(?:个|件|只|套|箱|袋)", txt)
    if m:
        return int(m.group(1))
    return None