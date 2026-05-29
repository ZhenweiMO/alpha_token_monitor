from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.social_announcement import SocialAnnouncement
from app.models.pre_tge_project import PreTgeProject
from app.models.signal import PreTgeSignal
from app.services.social_parser import parse_social_content
from app.services.alert_service import create_alert
from app.services.scoring import alert_level_from_score


router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementCreate(BaseModel):
    platform: str = "twitter"
    account_name: str
    account_type: str | None = None
    post_id: str
    post_url: str | None = None
    content: str


@router.post("")
async def create_announcement(payload: AnnouncementCreate, db: Session = Depends(get_db)):
    parsed = parse_social_content(payload.content)

    existing = (
        db.query(SocialAnnouncement)
        .filter(
            SocialAnnouncement.platform == payload.platform,
            SocialAnnouncement.post_id == payload.post_id,
        )
        .first()
    )

    if existing:
        return {
            "announcement": existing,
            "project": None,
            "parsed": existing.raw_data,
            "duplicate": True,
        }

    item = SocialAnnouncement(
        platform=payload.platform,
        account_name=payload.account_name,
        account_type=payload.account_type,
        post_id=payload.post_id,
        post_url=payload.post_url,
        content=payload.content,
        parsed_project_name=parsed["parsed_project_name"],
        parsed_symbol=parsed["parsed_symbol"],
        parsed_chain=parsed["parsed_chain"],
        parsed_contract_address=parsed["parsed_contract_address"],
        parsed_event_type=parsed["parsed_event_type"],
        is_pre_tge=parsed["is_pre_tge"],
        is_binance_wallet_related=parsed["is_binance_wallet_related"],
        is_binance_alpha_related=parsed["is_binance_alpha_related"],
        is_airdrop_related=parsed["is_airdrop_related"],
        is_tge_related=parsed["is_tge_related"],
        importance_score=parsed["importance_score"],
        confidence_score=parsed["confidence_score"],
        raw_data=parsed,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    project = None
    signal = None

    should_create_project = (
        parsed["is_pre_tge"]
        or parsed["is_binance_wallet_related"]
        or parsed["is_binance_alpha_related"]
        or parsed["parsed_contract_address"]
    )

    if should_create_project:
        project_name = parsed["parsed_project_name"] or parsed["parsed_symbol"] or "unknown_pre_tge_project"

        project = PreTgeProject(
            project_name=project_name,
            expected_symbol=parsed["parsed_symbol"],
            chain=parsed["parsed_chain"] or "bsc",
            status="discovered_from_social",
            binance_wallet_related=parsed["is_binance_wallet_related"],
            binance_alpha_related=parsed["is_binance_alpha_related"],
            tge_announced=parsed["is_tge_related"],
            confidence_score=parsed["confidence_score"],
            importance_score=parsed["importance_score"],
            source=payload.account_name,
            source_url=payload.post_url,
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        signal = PreTgeSignal(
            project_id=project.id,
            signal_type=parsed["parsed_event_type"],
            signal_source=payload.account_name,
            title=f"{payload.account_name} announcement",
            description=payload.content,
            source_url=payload.post_url,
            importance_score=parsed["importance_score"],
            confidence_score=parsed["confidence_score"],
            raw_data=parsed,
        )

        db.add(signal)
        db.commit()
        db.refresh(signal)

        score = float(parsed["importance_score"] or 0)
        alert_level = alert_level_from_score(score)

        message = (
            f"📢 <b>{alert_level} Social Announcement Detected</b>\n\n"
            f"<b>Source:</b> {payload.account_name}\n"
            f"<b>Event:</b> {parsed['parsed_event_type']}\n"
            f"<b>Symbol:</b> {parsed['parsed_symbol'] or '-'}\n"
            f"<b>Contract:</b> <code>{parsed['parsed_contract_address'] or '-'}</code>\n"
            f"<b>Binance Wallet Related:</b> {parsed['is_binance_wallet_related']}\n"
            f"<b>Binance Alpha Related:</b> {parsed['is_binance_alpha_related']}\n"
            f"<b>Airdrop Related:</b> {parsed['is_airdrop_related']}\n"
            f"<b>TGE Related:</b> {parsed['is_tge_related']}\n"
            f"<b>Importance:</b> {parsed['importance_score']}\n\n"
            f"<b>Content:</b>\n{payload.content}\n\n"
            f"{payload.post_url or ''}"
        )

        await create_alert(
            db=db,
            title=f"Social announcement from {payload.account_name}",
            message=message,
            alert_type="social_announcement",
            alert_level=alert_level,
            score=score,
            project_id=project.id,
            signal_id=signal.id,
            send_telegram=True,
        )

    return {
        "announcement": item,
        "project": project,
        "signal": signal,
        "parsed": parsed,
        "duplicate": False,
    }


@router.get("")
def list_announcements(db: Session = Depends(get_db)):
    return (
        db.query(SocialAnnouncement)
        .order_by(SocialAnnouncement.id.desc())
        .limit(100)
        .all()
    )
