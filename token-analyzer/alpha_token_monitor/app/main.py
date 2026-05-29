from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from app.db import Base, engine

# import models
from app.models.pre_tge_project import PreTgeProject
from app.models.token_candidate import ProjectTokenCandidate
from app.models.watch_address import WatchAddress
from app.models.wallet_transfer import WatchedAddressTokenTransfer
from app.models.social_announcement import SocialAnnouncement
from app.models.signal import PreTgeSignal
from app.models.alert import Alert
from app.models.twitter_crawl_state import TwitterCrawlState

# import routers
from app.api.watch_addresses import router as watch_addresses_router
from app.api.announcements import router as announcements_router
from app.api.projects import router as projects_router
from app.api.signals import router as signals_router
from app.api.transfers import router as transfers_router
from app.api.alerts import router as alerts_router
from app.api.twitter import router as twitter_router

# import services
from app.config import settings
from app.services.twitter_crawler import run_twitter_crawler


Base.metadata.create_all(bind=engine)

# 定时任务scheduler
scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动定时任务
    if settings.twitter_crawler_enabled:
        # 添加Twitter爬虫定时任务，每N分钟运行一次
        scheduler.add_job(
            run_twitter_crawler,
            "interval",
            minutes=settings.twitter_crawl_interval,
            id="twitter_crawler_job",
            replace_existing=True
        )
        scheduler.start()
        print(f"[INFO] Twitter爬虫定时任务已启动，每{settings.twitter_crawl_interval}分钟运行一次")

        # 启动时先运行一次
        await run_twitter_crawler()

    yield

    # 关闭定时任务
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title="Alpha Token Monitor",
    description="Pre-TGE Binance Wallet / Binance Alpha token monitor MVP",
    version="0.2.0",
    lifespan=lifespan
)


app.include_router(watch_addresses_router)
app.include_router(announcements_router)
app.include_router(projects_router)
app.include_router(signals_router)
app.include_router(transfers_router)
app.include_router(alerts_router)
app.include_router(twitter_router)


@app.get("/health")
def health():
 return {"status": "ok"}


@app.get("/")
def root():
 return {
 "name": "Alpha Token Monitor",
 "version": "0.1.0",
 "docs": "/docs",
 }
