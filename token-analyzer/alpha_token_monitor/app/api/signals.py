from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.signal import PreTgeSignal


router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("")
def list_signals(db: Session = Depends(get_db)):
 return (
 db.query(PreTgeSignal)
 .order_by(PreTgeSignal.id.desc())
 .limit(200)
 .all()
 )
