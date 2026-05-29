from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.watch_address import WatchAddress


router = APIRouter(prefix="/watch-addresses", tags=["watch-addresses"])


class WatchAddressCreate(BaseModel):
    chain: str = "bsc"
    address: str
    label: str | None = None
    label_type: str | None = None
    confidence_score: float = 0
    evidence: str | None = None
    source_url: str | None = None


@router.post("")
def create_watch_address(payload: WatchAddressCreate, db: Session = Depends(get_db)):
    address = payload.address.lower()

    existing = (
        db.query(WatchAddress)
        .filter(
            WatchAddress.chain == payload.chain,
            WatchAddress.address == address,
        )
        .first()
    )

    if existing:
        return existing

    item = WatchAddress(
        chain=payload.chain,
        address=address,
        label=payload.label,
        label_type=payload.label_type,
        confidence_score=payload.confidence_score,
        evidence=payload.evidence,
        source_url=payload.source_url,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get("")
def list_watch_addresses(db: Session = Depends(get_db)):
    return (
        db.query(WatchAddress)
        .order_by(WatchAddress.id.desc())
        .all()
    )


@router.patch("/{address_id}/deactivate")
def deactivate_watch_address(address_id: int, db: Session = Depends(get_db)):
    item = db.query(WatchAddress).filter(WatchAddress.id == address_id).first()

    if not item:
        return {"ok": False, "message": "not found"}

    item.is_active = False
    db.commit()
    db.refresh(item)

    return item


@router.patch("/{address_id}/activate")
def activate_watch_address(address_id: int, db: Session = Depends(get_db)):
    item = db.query(WatchAddress).filter(WatchAddress.id == address_id).first()

    if not item:
        return {"ok": False, "message": "not found"}

    item.is_active = True
    db.commit()
    db.refresh(item)

    return item
