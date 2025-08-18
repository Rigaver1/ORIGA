import yaml
from typing import Dict, Any, List, Tuple
from .config import settings

DEFAULT_RULES = {
    "threshold": 0.6,
    "fit": {
        "positive": {
            "源头工厂": 1.0,
            "工厂直供": 0.9,
            "生产加工": 0.8,
            "自有工厂": 1.0,
            "支持OEM": 0.6,
            "支持ODM": 0.6,
            "可定制": 0.4
        },
        "negative": {
            "贸易": -0.6,
            "批发": -0.4,
            "代理": -0.6
        }
    },
    "trust": {
        "audited": 0.2,
        "years_weight": 0.02
    }
}


def load_rules() -> Dict[str, Any]:
    try:
        with open(settings.scoring_rules_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return DEFAULT_RULES


def score_supplier(title: str, tags: List[str], years_active: int | None, audited: bool) -> Tuple[bool, float, float, float, List[str]]:
    rules = load_rules()
    pos_map = rules.get("fit", {}).get("positive", {})
    neg_map = rules.get("fit", {}).get("negative", {})
    threshold = float(rules.get("threshold", 0.6))
    trust = rules.get("trust", {})

    evidence: List[str] = []
    fit_score = 0.0
    text = (title or "") + " " + " ".join(tags or [])
    for k, w in pos_map.items():
        if k in text:
            fit_score += float(w)
            evidence.append(f"+{k}")
    for k, w in neg_map.items():
        if k in text:
            fit_score += float(w)
            evidence.append(f"{k}")

    audited_bonus = float(trust.get("audited", 0.0)) if audited else 0.0
    years_bonus = float(trust.get("years_weight", 0.0)) * (years_active or 0)
    fit_norm = max(0.0, min(1.0, (fit_score + 1.0) / 2.0))
    confidence = max(0.0, min(1.0, fit_norm))
    is_factory = confidence >= threshold

    # Final score 0..100
    score = (confidence + audited_bonus + years_bonus)
    score = max(0.0, min(1.0, score)) * 100.0

    return is_factory, confidence, audited_bonus, score, evidence