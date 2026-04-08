from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from app.models.report import Report
from app.models.prediction import Prediction

router = APIRouter()


class AddNoteRequest(BaseModel):
    prediction_id: int
    doctor_notes: str


@router.post("/", summary="Doctor adds or updates notes on a prediction")
async def add_note(
    body: AddNoteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.doctor:
        raise HTTPException(status_code=403, detail="Doctor role required.")

    # Verify prediction exists
    pred = await db.get(Prediction, body.prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found.")

    # Upsert report
    result = await db.execute(select(Report).where(Report.prediction_id == body.prediction_id))
    report = result.scalar_one_or_none()

    if report:
        report.doctor_notes = body.doctor_notes
        report.doctor_id = current_user.id
    else:
        report = Report(
            prediction_id=body.prediction_id,
            doctor_id=current_user.id,
            doctor_notes=body.doctor_notes,
        )
        db.add(report)

    await db.flush()
    return {"success": True, "message": "Notes saved."}


@router.get("/{prediction_id}", summary="Get report for a prediction")
async def get_report(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Report).where(Report.prediction_id == prediction_id))
    report = result.scalar_one_or_none()
    if not report:
        return {"report": None}
    return {
        "report": {
            "id": report.id,
            "doctor_notes": report.doctor_notes,
            "reviewed_at": report.reviewed_at.isoformat(),
        }
    }
