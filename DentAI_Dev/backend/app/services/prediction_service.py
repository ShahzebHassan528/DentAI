from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.prediction import Prediction


async def save_prediction(
    db: AsyncSession,
    user_id: int,
    final_diagnosis: str,
    confidence: float,
    image_url: str | None = None,
    symptoms: str | None = None,
    image_diagnosis: str | None = None,
    text_diagnosis: str | None = None,
) -> Prediction:
    prediction = Prediction(
        user_id=user_id,
        image_url=image_url,
        symptoms=symptoms,
        image_diagnosis=image_diagnosis,
        text_diagnosis=text_diagnosis,
        final_diagnosis=final_diagnosis,
        confidence=confidence,
    )
    db.add(prediction)
    await db.flush()
    return prediction


async def get_user_predictions(db: AsyncSession, user_id: int) -> list[Prediction]:
    result = await db.execute(
        select(Prediction)
        .where(Prediction.user_id == user_id)
        .order_by(Prediction.created_at.desc())
    )
    return result.scalars().all()
