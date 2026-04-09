"""
Tests for /reports endpoints:
  POST /reports/       — doctor adds/updates note
  GET  /reports/{id}   — get report for a prediction
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.conftest import _TestSession

from app.models.prediction import Prediction
from app.models.user import User, UserRole
from app.core.security import hash_password


# ── Helper: insert a prediction row directly into the test DB ─────────────────
async def _create_prediction(user_id: int, diagnosis: str = "cavity") -> int:
    async with _TestSession() as session:
        pred = Prediction(
            user_id=user_id,
            final_diagnosis=diagnosis,
            confidence=0.88,
            image_diagnosis=diagnosis,
        )
        session.add(pred)
        await session.commit()
        await session.refresh(pred)
        return pred.id


# ── Helper: get patient user id from DB by email ──────────────────────────────
async def _get_user_id(email: str) -> int:
    from sqlalchemy import select
    async with _TestSession() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return user.id if user else None


# ─────────────────────────────────────────────
# Auth guards
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_note_requires_auth(client: AsyncClient):
    resp = await client.post("/reports/", json={"prediction_id": 1, "doctor_notes": "looks fine"})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_add_note_patient_forbidden(client: AsyncClient, patient_headers: dict):
    resp = await client.post(
        "/reports/",
        json={"prediction_id": 1, "doctor_notes": "some note"},
        headers=patient_headers,
    )
    assert resp.status_code == 403


# ─────────────────────────────────────────────
# Add note
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_note_nonexistent_prediction(client: AsyncClient, doctor_headers: dict):
    resp = await client.post(
        "/reports/",
        json={"prediction_id": 999999, "doctor_notes": "this prediction does not exist"},
        headers=doctor_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_add_note_success(client: AsyncClient, patient_headers: dict, doctor_headers: dict):
    # Get patient user id
    patient_id = await _get_user_id("patient_fixture@test.com")
    assert patient_id is not None

    pred_id = await _create_prediction(patient_id, "cavity")

    resp = await client.post(
        "/reports/",
        json={"prediction_id": pred_id, "doctor_notes": "Cavity confirmed. Schedule filling."},
        headers=doctor_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_add_note_upsert(client: AsyncClient, patient_headers: dict, doctor_headers: dict):
    """Adding a note twice on the same prediction should update, not duplicate."""
    patient_id = await _get_user_id("patient_fixture@test.com")
    pred_id = await _create_prediction(patient_id, "infection")

    await client.post(
        "/reports/",
        json={"prediction_id": pred_id, "doctor_notes": "First note."},
        headers=doctor_headers,
    )
    resp = await client.post(
        "/reports/",
        json={"prediction_id": pred_id, "doctor_notes": "Updated note."},
        headers=doctor_headers,
    )
    assert resp.status_code == 200

    # Verify via GET that only one report exists with updated text
    get_resp = await client.get(f"/reports/{pred_id}", headers=doctor_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["report"]["doctor_notes"] == "Updated note."


# ─────────────────────────────────────────────
# Get report
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_report_no_note(client: AsyncClient, patient_headers: dict, doctor_headers: dict):
    """Prediction with no report → returns {"report": null}."""
    patient_id = await _get_user_id("patient_fixture@test.com")
    pred_id = await _create_prediction(patient_id, "healthy")

    resp = await client.get(f"/reports/{pred_id}", headers=patient_headers)
    assert resp.status_code == 200
    assert resp.json()["report"] is None


@pytest.mark.asyncio
async def test_get_report_requires_auth(client: AsyncClient):
    resp = await client.get("/reports/1")
    assert resp.status_code in (401, 403)


# ─────────────────────────────────────────────
# Input validation
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_note_missing_fields(client: AsyncClient, doctor_headers: dict):
    resp = await client.post("/reports/", json={"prediction_id": 1}, headers=doctor_headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_add_note_invalid_prediction_id_type(client: AsyncClient, doctor_headers: dict):
    resp = await client.post(
        "/reports/",
        json={"prediction_id": "not-an-int", "doctor_notes": "test"},
        headers=doctor_headers,
    )
    assert resp.status_code == 422
