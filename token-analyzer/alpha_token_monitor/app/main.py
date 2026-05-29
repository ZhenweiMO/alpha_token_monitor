from fastapi import FastAPI

from app.db import Base, engine

# import models
from app.models.pre_tge_project import PreTgeProject
from app.models.token_candidate import ProjectTokenCandidate
from app.models.watch_address import WatchAddress
from app.models.wallet_transfer import WatchedAddressTokenTransfer
from app.models.social_announcement import SocialAnnouncement
from app.models.signal import PreTgeSignal
from app.models.alert import Alert

# import routers
from app.api.watch_addresses import router as watch_addresses_router
from app.api.announcements import router as announcements_router
from app.api.projects import router as projects_router
from app.api.signals import router as signals_router
from app.api.transfers import router as transfers_router
from app.api.alerts import router as alerts_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
 title="Alpha Token Monitor",
 description="Pre-TGE Binance Wallet / Binance Alpha token monitor MVP",
 version="0.1.0",
)


app.include_router(watch_addresses_router)
app.include_router(announcements_router)
app.include_router(projects_router)
app.include_router(signals_router)
app.include_router(transfers_router)
app.include_router(alerts_router)


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
