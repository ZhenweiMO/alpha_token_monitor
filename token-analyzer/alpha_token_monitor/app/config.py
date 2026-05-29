from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
 database_url: str

 bscscan_api_key: str | None = None
 moralis_api_key: str | None = None

 telegram_bot_token: str | None = None
 telegram_chat_id: str | None = None

 bsc_chain: str = "bsc"

 outbound_proxy: str | None = None

 model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
