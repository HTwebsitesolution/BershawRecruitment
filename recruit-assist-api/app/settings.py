from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model_short: str = "gpt-4o-mini"  # for short form drafting (cheap/fast)
    openai_model_long: str = "gpt-4o"  # for endorsements (higher quality)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()
