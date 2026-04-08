from pydantic import BaseModel, Field
from typing import Optional


class TextPredictRequest(BaseModel):
    symptoms: str = Field(..., min_length=3, max_length=2000,
                          description="Patient symptom description in plain text")


class ImagePredictResponse(BaseModel):
    diagnosis: str
    confidence: float
    probabilities: dict[str, float]


class TextPredictResponse(BaseModel):
    diagnosis: str
    confidence: float
    probabilities: dict[str, float]


class CombinedPredictResponse(BaseModel):
    final_diagnosis: str
    confidence: float
    image_diagnosis: Optional[str]
    text_diagnosis: Optional[str]
    probabilities: dict[str, float]
    mode: str  # "combined" | "image_only" | "text_only"
