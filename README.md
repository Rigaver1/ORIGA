# 1688 Product Parser (CLI)

CLI-инструмент для парсинга карточек товаров 1688 и извлечения ключевых данных для карго-менеджера.

## Установка

```bash
python -m pip install -e .
# Опционально для браузерного режима:
python -m pip install .[browser]
# Установка браузера (если планируете --browser):
python -m playwright install --with-deps chromium
```

## Использование

```bash
1688parser URL [URL ...]
```

Опции:
- `--browser` — включить рендеринг через Playwright
- `--timeout` — таймаут в секундах (по умолчанию 25)
- `--proxy` — HTTP(S) прокси `http://user:pass@host:port`
- `--from-file` — файл со списком URL
- `--out` — файл для вывода JSON
- `--ndjson` — построчный вывод
- `--verbose` — подробный лог

## Поля
- Идентификаторы: `offer_id`, `url`
- Товар: `title`, `category`, `attributes`, `description_text`, `description_html`, `images`
- Цены: `min_order`, `price_tiers`, `sku_list`
- Упаковка: `weight`, `dimensions`, `package_info`, `origin_location`, `lead_time`, `stock`
- Продавец: `shop_name`, `shop_id`, `seller_company`, `seller_contact`
- Доказательства: `ratings`, `sold_count`, `reviews_count`

## Лицензия
MIT