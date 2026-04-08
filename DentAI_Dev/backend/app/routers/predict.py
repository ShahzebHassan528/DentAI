from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.ml.predict import predict_image, predict_text, predict_combined
from app.schemas.predict import (
    ImagePredictResponse,
    TextPredictRequest,
    TextPredictResponse,
    CombinedPredictResponse,
)

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

    return result


@router.post(
    "/text",
    response_model=TextPredictResponse,
    summary="Diagnose from patient symptom description",
)
async def predict_from_text(body: TextPredictRequest):
    try:
        result = predict_text(body.symptoms)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

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

    return result
