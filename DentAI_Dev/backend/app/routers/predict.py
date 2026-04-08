import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.predict import predict_image, predict_text, predict_combined
from app.schemas.predict import (
    ImagePredictResponse,
    TextPredictRequest,
    TextPredictResponse,
    CombinedPredictResponse,
)
from app.core.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.cloudinary_service import upload_xray
from app.services.prediction_service import save_prediction

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


def _validate_image(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported image type '{file.content_type}'. "
                   f"Allowed: jpeg, png, webp, bmp."
        )


@router.post(
    "/image",
    response_model=ImagePredictResponse,
    summary="Diagnose from dental X-ray image",
)
async def predict_from_image(
    file: UploadFile = File(..., description="Dental X-ray image (JPEG/PNG/WebP/BMP, max 10 MB)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _validate_image(file)
    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large. Maximum size is 10 MB.")

    try:
        result = predict_image(image_bytes)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    # Upload to Cloudinary
    image_url = None
    try:
        image_url = upload_xray(image_bytes, filename=f"user_{current_user.id}_{uuid.uuid4().hex[:8]}")
    except Exception:
        pass  # Cloudinary upload failure should not block diagnosis

    # Save to DB
    await save_prediction(
        db,
        user_id=current_user.id,
        final_diagnosis=result["diagnosis"],
        confidence=result["confidence"],
        image_url=image_url,
        image_diagnosis=result["diagnosis"],
    )

    return result


@router.post(
    "/text",
    response_model=TextPredictResponse,
    summary="Diagnose from patient symptom description",
)
async def predict_from_text(
    body: TextPredictRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = predict_text(body.symptoms)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    await save_prediction(
        db,
        user_id=current_user.id,
        final_diagnosis=result["diagnosis"],
        confidence=result["confidence"],
        symptoms=body.symptoms,
        text_diagnosis=result["diagnosis"],
    )

    return result


@router.post(
    "/combined",
    response_model=CombinedPredictResponse,
    summary="Diagnose using late fusion of image + symptoms (0.6 / 0.4 weights)",
)
async def predict_combined_endpoint(
    file: Optional[UploadFile] = File(None, description="Dental X-ray image (optional)"),
    symptoms: Optional[str] = Form(None, min_length=3, max_length=2000,
                                   description="Symptom description (optional)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file is None and (symptoms is None or not symptoms.strip()):
        raise HTTPException(
            status_code=422,
            detail="Provide at least one of: image file or symptoms text."
        )

    image_bytes: Optional[bytes] = None
    if file is not None:
        _validate_image(file)
        image_bytes = await file.read()
        if len(image_bytes) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="Image too large. Maximum size is 10 MB.")

    try:
        result = predict_combined(image_bytes, symptoms)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    # Upload image to Cloudinary if provided
    image_url = None
    if image_bytes is not None:
        try:
            image_url = upload_xray(image_bytes, filename=f"user_{current_user.id}_{uuid.uuid4().hex[:8]}")
        except Exception:
            pass

    await save_prediction(
        db,
        user_id=current_user.id,
        final_diagnosis=result["final_diagnosis"],
        confidence=result["confidence"],
        image_url=image_url,
        symptoms=symptoms,
        image_diagnosis=result.get("image_diagnosis"),
        text_diagnosis=result.get("text_diagnosis"),
    )

    return result


@router.get(
    "/history",
    summary="Get current user's prediction history",
)
async def prediction_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.prediction_service import get_user_predictions
    predictions = await get_user_predictions(db, current_user.id)
    return predictions
