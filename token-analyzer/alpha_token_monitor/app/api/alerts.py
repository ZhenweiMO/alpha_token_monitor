from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.alert import Alert


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def list_alerts(db: Session = Depends(get_db)):
 return (
 db.query(Alert)
 .order_by(Alert.id.desc())
 .limit(200)
 .all()
 )
