from datetime import datetime
from .models import DDPInput, DDPResult
from .fx import get_cny_rub_rate


def round2(x: float) -> float:
    return float(round(x, 2))


async def calculate_ddp_async(req: DDPInput) -> DDPResult:
    rate = await get_cny_rub_rate(req.fx_source, req.fx_cny_rub)

    goods_cny = req.exw_or_fob_cny * req.qty
    goods_rub = goods_cny * rate

    freight_rub = req.freight_total_rub + req.freight_total_cny * rate
    inland_rub = req.inland_ru_rub + req.inland_cn_cny * rate

    insurance_rub = goods_rub * (req.insurance_pct / 100.0)
    duty_rub = goods_rub * (req.duty_rate_pct / 100.0)
    vat_rub = (goods_rub + duty_rub + freight_rub) * (req.vat_rate_pct / 100.0)

    total_rub = goods_rub + freight_rub + inland_rub + insurance_rub + duty_rub + vat_rub
    per_unit_rub = total_rub / max(1, req.qty)

    return DDPResult(
        fx_used_cny_rub=round2(rate),
        goods_rub=round2(goods_rub),
        freight_rub=round2(freight_rub),
        inland_rub=round2(inland_rub),
        insurance_rub=round2(insurance_rub),
        duty_rub=round2(duty_rub),
        vat_rub=round2(vat_rub),
        total_rub=round2(total_rub),
        per_unit_rub=round2(per_unit_rub),
        mode=req.mode,
        ts=datetime.utcnow()
    )