import os
from dataclasses import dataclass
from functools import lru_cache
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    app_host: str
    app_port: int
    use_llm: bool
    llm_provider: str | None
    llm_model: str | None
    llm_api_key: str | None


def _read_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        app_name=os.getenv("APP_NAME", "North Star Support Bot"),
        app_env=os.getenv("APP_ENV", "development"),
        app_host=os.getenv("APP_HOST", "0.0.0.0"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        use_llm=_read_bool(os.getenv("USE_LLM"), default=False),
        llm_provider=os.getenv("LLM_PROVIDER") or None,
        llm_model=os.getenv("LLM_MODEL") or None,
        llm_api_key=os.getenv("LLM_API_KEY") or None,
    )
