from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
 database_url: str

 bscscan_api_key: str | None = None
 moralis_api_key: str | None = None

 telegram_bot_token: str | None = None
 telegram_chat_id: str | None = None

 bsc_chain: str = "bsc"

 outbound_proxy: str | None = None

 # Twitter crawler config
 twitter_crawler_enabled: bool = True
 twitter_crawl_interval: int = 15
 twitter_crawl_accounts: str = "binance_wallet"
 twitter_crawl_limit_per_run: int = 10
 twitter_match_keywords: str = "airdrop,空投,tge,pre-tge,booster"
 twitter_exclude_keywords: str = "test,fake,scam"

 model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
