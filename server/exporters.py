import os
import csv
import json
from typing import List
from .models import SupplierItem

HEADERS = {
    "title": "Название",
    "url": "Ссылка",
    "image_urls": "Фото",
    "price_min_cny": "Мин цена CNY",
    "price_max_cny": "Макс цена CNY",
    "moq": "MOQ",
    "shop_name": "Компания",
    "location": "Локация",
    "tags": "Теги",
    "is_factory": "Завод",
    "is_factory_confidence": "Уверенность",
    "audited": "Аудит",
    "certifications": "Сертификаты",
    "evidence": "Доказательства",
    "years_active": "Лет на рынке",
    "score": "Скор",
}


def to_records(items: List[SupplierItem]):
    rows = []
    for it in items:
        rows.append({
            "title": it.title,
            "url": it.url,
            "image_urls": ", ".join(it.image_urls or []),
            "price_min_cny": it.price_min_cny,
            "price_max_cny": it.price_max_cny,
            "moq": it.moq,
            "shop_name": it.shop_name,
            "location": it.location,
            "tags": ", ".join(it.tags or []),
            "is_factory": "Да" if it.is_factory else "Нет",
            "is_factory_confidence": round(float(it.is_factory_confidence), 2),
            "audited": "Да" if it.audited else "Нет",
            "certifications": ", ".join(it.certifications or []),
            "evidence": ", ".join(it.evidence or []),
            "years_active": it.years_active,
            "score": round(float(it.score), 1),
        })
    return rows


def export_suppliers_to_excel(items: List[SupplierItem]) -> str:
    # Export as CSV compatible with Excel
    os.makedirs("exports", exist_ok=True)
    path = os.path.join("exports", "suppliers.csv")
    records = to_records(items)
    columns = list(HEADERS.keys())
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[HEADERS[c] for c in columns])
        writer.writeheader()
        for r in records:
            writer.writerow({HEADERS[k]: r.get(k) for k in columns})
    return path


def export_to_csv_json(items: List[SupplierItem], fmt: str) -> str:
    os.makedirs("exports", exist_ok=True)
    if fmt == "json":
        path = os.path.join("exports", "suppliers.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([it.model_dump() for it in items], f, ensure_ascii=False, indent=2)
        return path
    if fmt == "csv":
        return export_suppliers_to_excel(items)
    raise ValueError("Формат не поддерживается: " + fmt)