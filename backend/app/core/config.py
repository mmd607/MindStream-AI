from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./ai_project_architect.db")
    ai_provider: str = os.getenv("AI_PROVIDER", "mock").lower()
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_model: str = os.getenv("LLM_MODEL", "")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

