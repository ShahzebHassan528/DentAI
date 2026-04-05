from datetime import datetime, timezone
from sqlalchemy import String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    symptoms: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_diagnosis: Mapped[str | None] = mapped_column(String(100), nullable=True)
    text_diagnosis: Mapped[str | None] = mapped_column(String(100), nullable=True)
    final_diagnosis: Mapped[str] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="predictions")
    report: Mapped["Report | None"] = relationship(back_populates="prediction")
