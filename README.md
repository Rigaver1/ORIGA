# CargoOS 1688 — Ядро (RU)

Запуск одним действием:

```bash
bash run.sh
```

Откройте `http://localhost:8000/` для UI.

API:
- GET `/health` → `{ ok: true }`
- GET `/search_1688` — поиск (онлайн/офлайн)
- GET `/search_1688/stream` — потоковые результаты (SSE)
- POST `/export/xlsx` — экспорт Excel
- POST `/export/{json|csv}` — экспорт JSON/CSV
- POST `/rfq` — генерация RFQ (ru/en/cn)
- POST `/calc/ddp` — расчёт DDP в ₽

Конфигурация в `config/`.