import os
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Limits(BaseModel):
    per_call_timeout: int = Field(default=300, description="Per LLM call timeout in seconds")
    max_calls_per_brick: int = Field(default=8, description="Maximum LLM calls per brick")
    max_tokens_per_call: int = Field(default=8192, description="Maximum tokens per LLM call")
    max_brick_wall_time: int = Field(default=300, description="Maximum wall time per brick in seconds")
    max_file_changes: int = Field(default=6, description="Maximum file changes per brick")


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore"
    )
    
    zai_api_key: str = Field(default="", alias="Z_AI_API_KEY")
    zai_base_url: str = Field(default="https://open.bigmodel.cn/api/paas/v4", alias="Z_AI_BASE_URL")
    zai_model_name: str = Field(default="glm-4.7", alias="Z_AI_MODEL_NAME")
    limits: Limits = Field(default_factory=Limits)
    dry_run: bool = Field(default=False)
    logs_dir: str = Field(default="logs")
    runs_dir: str = Field(default="runs")
    stop_file: str = Field(default="STOP")


def get_config() -> Config:
    return Config()


def check_stop_file(config: Config) -> bool:
    return os.path.exists(config.stop_file)
