from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.wallet_transfer import WatchedAddressTokenTransfer


router = APIRouter(prefix="/transfers", tags=["transfers"])


@router.get("")
def list_transfers(db: Session = Depends(get_db)):
 return (
 db.query(WatchedAddressTokenTransfer)
 .order_by(WatchedAddressTokenTransfer.id.desc())
 .limit(200)
 .all()
 )
