from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.alert import Alert


async def send_telegram_message(text: str) -> bool:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return False

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    async with httpx.AsyncClient(timeout=20, proxy=settings.outbound_proxy) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()

        return True


async def create_alert(
    db: Session,
    title: str,
    message: str,
    alert_type: str,
    alert_level: str,
    score: float = 0,
    project_id: int | None = None,
    token_candidate_id: int | None = None,
    signal_id: int | None = None,
    send_telegram: bool = True,
) -> Alert:
    alert = Alert(
        project_id=project_id,
        token_candidate_id=token_candidate_id,
        signal_id=signal_id,
        alert_level=alert_level,
        alert_type=alert_type,
        title=title,
        message=message,
        score=score,
        is_sent=False,
        sent_channels=[],
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    sent_channels = []

    if send_telegram:
        ok = await send_telegram_message(message)
        if ok:
            sent_channels.append("telegram")
            alert.is_sent = True
            alert.sent_channels = sent_channels
            alert.sent_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)

    return alert
