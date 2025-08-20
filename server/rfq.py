import os
from typing import List
from .models import RFQRequest, RFQResponse

TEMPLATES = {
    "ru": (
        "Тема: Запрос коммерческого предложения (RFQ)\n\n"
        "Здравствуйте!\n\n"
        "Мы заинтересованы в товаре: {title}.\n"
        "Ссылка/фото: {url_or_img}\n"
        "Цена (по карточке): {price_range}\n"
        "MOQ (по карточке): {moq}\n"
        "Условия: {incoterms}\n"
        "Требуемые сертификаты: {certs}\n"
        "Планируемый объём: {qty}\n\n"
        "Просим прислать актуальную цену, сроки производства и логистики, варианты упаковки.\n"
        "Спасибо!"
    ),
    "en": (
        "Subject: RFQ\n\n"
        "Hello,\n\n"
        "We are interested in: {title}.\n"
        "Link/photo: {url_or_img}\n"
        "Price (card): {price_range}\n"
        "MOQ (card): {moq}\n"
        "Incoterms: {incoterms}\n"
        "Required certificates: {certs}\n"
        "Planned quantity: {qty}\n\n"
        "Please provide current price, lead time, logistics options, and packaging.\n"
        "Thank you."
    ),
    "cn": (
        "主题：询价（RFQ）\n\n"
        "您好！\n\n"
        "我们对以下产品感兴趣：{title}。\n"
        "链接/图片：{url_or_img}\n"
        "参考价格：{price_range}\n"
        "最小起订量：{moq}\n"
        "贸易条款：{incoterms}\n"
        "所需认证：{certs}\n"
        "预计数量：{qty}\n\n"
        "请提供最新价格、生产周期、物流方案以及包装信息。谢谢！"
    ),
}


def generate_rfq(req: RFQRequest) -> RFQResponse:
    os.makedirs("exports", exist_ok=True)
    lang = req.lang.lower()
    if lang not in TEMPLATES:
        raise ValueError("Неподдерживаемый язык")
    url_or_img = req.url or (req.image_url or "—")
    body = TEMPLATES[lang].format(
        title=req.title,
        url_or_img=url_or_img,
        price_range=req.price_range or "—",
        moq=req.moq or "—",
        incoterms=req.incoterms or "—",
        certs=', '.join(req.required_certs) if req.required_certs else "—",
        qty=req.qty or "—",
    )
    if req.custom_note:
        body += "\n\n" + req.custom_note
    path = os.path.join("exports", f"rfq_{lang}.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(body)
    preview = body.splitlines()
    preview = '\n'.join(preview[:6])
    return RFQResponse(path=path, preview=preview)