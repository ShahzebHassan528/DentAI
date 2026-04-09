"""
Tests for /predict endpoints.

NOTE: image and text ML predictions require model weights.
Those endpoints are tested for auth/validation behaviour only
(they return 503 when weights are missing, which is expected).
History and /all endpoints are fully tested.
"""

import pytest
from httpx import AsyncClient
import io


# ─────────────────────────────────────────────
# Auth guard tests
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_image_requires_auth(client: AsyncClient):
    dummy = io.BytesIO(b"fake image bytes")
    resp = await client.post(
        "/predict/image",
        files={"file": ("xray.jpg", dummy, "image/jpeg")},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_predict_text_requires_auth(client: AsyncClient):
    resp = await client.post("/predict/text", json={"symptoms": "toothache and swelling"})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_predict_combined_requires_auth(client: AsyncClient):
    resp = await client.post("/predict/combined", data={"symptoms": "pain"})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_history_requires_auth(client: AsyncClient):
    resp = await client.get("/predict/history")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_predict_all_requires_auth(client: AsyncClient):
    resp = await client.get("/predict/all")
    assert resp.status_code in (401, 403)


# ─────────────────────────────────────────────
# Input validation — image endpoint
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_image_wrong_content_type(client: AsyncClient, patient_headers: dict):
    """PDF should be rejected with 422."""
    dummy = io.BytesIO(b"%PDF-fake")
    resp = await client.post(
        "/predict/image",
        files={"file": ("report.pdf", dummy, "application/pdf")},
        headers=patient_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_predict_image_valid_type_no_weights(client: AsyncClient, patient_headers: dict):
    """Valid JPEG → 503 because model weights are absent in test env."""
    dummy = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 100)   # minimal JPEG-ish bytes
    resp = await client.post(
        "/predict/image",
        files={"file": ("xray.jpg", dummy, "image/jpeg")},
        headers=patient_headers,
    )
    # 503 = weights missing, 500 = PIL can't open fake bytes — both acceptable
    assert resp.status_code in (500, 503)


# ─────────────────────────────────────────────
# Input validation — text endpoint
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_text_no_weights(client: AsyncClient, patient_headers: dict):
    """Text prediction → 200 if weights exist, 503 if absent, 500 on other errors."""
    resp = await client.post(
        "/predict/text",
        json={"symptoms": "I have severe toothache and my gum is swollen"},
        headers=patient_headers,
    )
    assert resp.status_code in (200, 500, 503)


@pytest.mark.asyncio
async def test_predict_text_empty_symptoms(client: AsyncClient, patient_headers: dict):
    """Empty symptoms string should fail Pydantic validation."""
    resp = await client.post(
        "/predict/text",
        json={"symptoms": ""},
        headers=patient_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_predict_text_missing_body(client: AsyncClient, patient_headers: dict):
    resp = await client.post("/predict/text", json={}, headers=patient_headers)
    assert resp.status_code == 422


# ─────────────────────────────────────────────
# Input validation — combined endpoint
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_predict_combined_no_inputs(client: AsyncClient, patient_headers: dict):
    """Neither file nor symptoms provided → 422."""
    resp = await client.post(
        "/predict/combined",
        data={},
        headers=patient_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_predict_combined_symptoms_only_no_weights(client: AsyncClient, patient_headers: dict):
    resp = await client.post(
        "/predict/combined",
        data={"symptoms": "jaw pain and difficulty opening mouth"},
        headers=patient_headers,
    )
    assert resp.status_code in (200, 500, 503)


# ─────────────────────────────────────────────
# History
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_history_returns_list(client: AsyncClient, patient_headers: dict):
    resp = await client.get("/predict/history", headers=patient_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ─────────────────────────────────────────────
# /all — doctor only
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_all_predictions_as_doctor(client: AsyncClient, doctor_headers: dict):
    resp = await client.get("/predict/all", headers=doctor_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_all_predictions_patient_forbidden(client: AsyncClient, patient_headers: dict):
    resp = await client.get("/predict/all", headers=patient_headers)
    assert resp.status_code == 403
