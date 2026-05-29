from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.pre_tge_project import PreTgeProject
from app.models.signal import PreTgeSignal


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
def list_projects(db: Session = Depends(get_db)):
    return (
        db.query(PreTgeProject)
        .order_by(
            PreTgeProject.importance_score.desc(),
            PreTgeProject.id.desc(),
        )
        .limit(200)
        .all()
    )


@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = (
        db.query(PreTgeProject)
        .filter(PreTgeProject.id == project_id)
        .first()
    )

    if not project:
        return {"ok": False, "message": "not found"}

    signals = (
        db.query(PreTgeSignal)
        .filter(PreTgeSignal.project_id == project_id)
        .order_by(PreTgeSignal.id.desc())
        .limit(100)
        .all()
    )

    return {
        "project": project,
        "signals": signals,
    }
