# CargoOS 1688 — Ядро (RU)

## Эндпоинты

- GET `/health`
  - Ответ: `{ ok: true }`

- GET `/search_1688`
  - Параметры:
    - `q` (строка, обяз.) — CN-запрос
    - `mode` (fast|precise) — режим парсинга
    - `pages` (1..20)
    - `online` (true|false) — онлайн/оффлайн
    - `only_factories` (bool, по умолч. true)
    - `audited_only` (bool, по умолч. true)
    - `min_years` (int)
    - `moq_max` (int)
    - `price_min`, `price_max` (float)
    - `region` (строка)
    - `concurrency` (1..10)
    - `timeout` (сек)
    - `proxy` (строка)
    - `cookie` (строка)
    - `render` (bool) — рендер динамики (фолбэк)
    - `offline_demo` (bool) — офлайн-снимок
  - Ответ: `list[SupplierItem]`

- GET `/search_1688/stream`
  - Возвращает SSE-стрим событий `item` с элементами `SupplierItem` в JSON

- POST `/export/xlsx`
  - Тело: `list[SupplierItem]`
  - Ответ: `{ path: "exports/suppliers.xlsx" }`

- POST `/export/{json|csv}`
  - Тело: `list[SupplierItem]`
  - Ответ: `{ path: "exports/…" }`

- POST `/rfq`
  - Тело: `{ lang, title, url?, image_url?, price_range?, moq?, incoterms?, required_certs[], qty?, custom_note? }`
  - Ответ: `{ path, preview }`

- POST `/calc/ddp`
  - Тело: `DDPInput`
  - Ответ: `DDPResult`

## Модели

- `SupplierItem`:
  - `title`, `url`, `image_urls[]`, `price_min_cny`, `price_max_cny`, `moq`, `shop_name`, `location`, `tags[]`, `is_factory`, `is_factory_confidence`, `audited`, `certifications[]`, `evidence[]`, `years_active`, `contacts?`, `pack?`, `score`, `captured_at`

- `SearchParams` — соответствует параметрам фильтров

- `DDPInput`:
  - `exw_or_fob_cny`, `qty`, `cbm_total?`, `gw_total?`, `duty_rate_pct`, `vat_rate_pct`, `freight_total_cny`, `freight_total_rub`, `inland_cn_cny`, `inland_ru_rub`, `insurance_pct`, `mode`, `fx_source`, `fx_cny_rub?`

- `DDPResult`:
  - `fx_used_cny_rub`, `goods_rub`, `freight_rub`, `inland_rub`, `insurance_rub`, `duty_rub`, `vat_rub`, `total_rub`, `per_unit_rub`, `mode`, `ts`

## Правила и скоринг «завод»

`config/scoring_rules.yaml` — YAML с весами позитивных/негативных маркеров, порогом `threshold`, блоки `fit` и `trust`.

## Нормализация данных 1688

- `parse_price_range_cn(text)` → (min, max|None)
- `parse_moq_cn(text)` → int|None

## Кэш курсов валют

- Источник: ЦБ РФ, кэш: 1 час, путь: `data/cache/fx_cny_rub.json`

## Офлайн-демо

- HTML-снимок: `data/offline/snapshot.html` (опционально)
- Флаг: `offline_demo=true` или `online=false`