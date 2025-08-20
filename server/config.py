from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "CargoOS 1688 — Ядро (RU)"
    cache_dir: str = "data/cache"
    offline_dir: str = "data/offline"
    exports_dir: str = "exports"
    config_dir: str = "config"
    selectors_file: str = "config/selectors.yaml"
    scoring_rules_file: str = "config/scoring_rules.yaml"
    tariffs_file: str = "config/tariffs.yaml"
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
    default_concurrency: int = 3
    default_timeout: float = 15.0
    short_cache_ttl_sec: int = 120

    class Config:
        env_prefix = "CARGOOS_"

settings = Settings()