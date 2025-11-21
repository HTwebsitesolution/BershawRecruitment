from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model_short: str = "gpt-4o-mini"  # for short form drafting (cheap/fast)
    openai_model_long: str = "gpt-4o"  # for endorsements (higher quality)
    openai_timeout: float = Field(default=60.0, alias="OPENAI_TIMEOUT", description="Timeout for OpenAI API calls in seconds")
    
    # Database settings
    # Can use SQLite for testing or PostgreSQL for production
    database_url: str = Field(
        default="sqlite:///./recruit_assist.db",  # SQLite for quick testing
        # default="postgresql://postgres:postgres@localhost:5432/recruit_assist",  # PostgreSQL for production
        alias="DATABASE_URL",
        description="Database URL (SQLite or PostgreSQL)"
    )
    debug: bool = Field(default=False, alias="DEBUG", description="Enable debug mode (SQL logging)")
    
    # Calendar integration settings
    calendly_api_key: str = Field(default="", alias="CALENDLY_API_KEY", description="Calendly API key")
    calendly_username: str = Field(default="bershaw-recruitment", alias="CALENDLY_USERNAME", description="Calendly username")
    calendly_event_type: str = Field(default="interview", alias="CALENDLY_EVENT_TYPE", description="Calendly event type")
    
    google_calendar_api_key: str = Field(default="", alias="GOOGLE_CALENDAR_API_KEY", description="Google Calendar API key")
    google_calendar_id: str = Field(default="", alias="GOOGLE_CALENDAR_ID", description="Google Calendar ID")
    
    microsoft_graph_client_id: str = Field(default="", alias="MICROSOFT_GRAPH_CLIENT_ID", description="Microsoft Graph Client ID")
    microsoft_graph_client_secret: str = Field(default="", alias="MICROSOFT_GRAPH_CLIENT_SECRET", description="Microsoft Graph Client Secret")
    
    # AI Interviewer settings
    hirevue_api_key: str = Field(default="", alias="HIREVUE_API_KEY", description="HireVue API key")
    hirevue_api_secret: str = Field(default="", alias="HIREVUE_API_SECRET", description="HireVue API secret")
    
    myinterview_api_key: str = Field(default="", alias="MYINTERVIEW_API_KEY", description="MyInterview API key")
    
    # LinkedIn API settings
    linkedin_api_key: str = Field(default="", alias="LINKEDIN_API_KEY", description="LinkedIn API key")
    linkedin_api_secret: str = Field(default="", alias="LINKEDIN_API_SECRET", description="LinkedIn API secret")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()
