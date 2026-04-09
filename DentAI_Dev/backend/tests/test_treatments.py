"""
Tests for GET /treatments/{condition}
"""

import pytest
from httpx import AsyncClient

VALID_CONDITIONS = ["cavity", "healthy", "impacted", "infection", "other"]


@pytest.mark.asyncio
@pytest.mark.parametrize("condition", VALID_CONDITIONS)
async def test_valid_condition_returns_200(client: AsyncClient, condition: str):
    resp = await client.get(f"/treatments/{condition}")
    assert resp.status_code == 200
    data = resp.json()
    assert "condition" in data
    assert "treatments" in data
    assert "prevention" in data
    assert isinstance(data["treatments"], list)
    assert len(data["treatments"]) > 0
    assert isinstance(data["prevention"], list)
    assert len(data["prevention"]) > 0


@pytest.mark.asyncio
async def test_treatment_response_shape(client: AsyncClient):
    resp = await client.get("/treatments/cavity")
    assert resp.status_code == 200
    data = resp.json()

    # Each treatment must have name + description + when
    for t in data["treatments"]:
        assert "name" in t
        assert "description" in t
        assert "when" in t


@pytest.mark.asyncio
async def test_unknown_condition_returns_404(client: AsyncClient):
    resp = await client.get("/treatments/unknown_condition")
    assert resp.status_code == 404
    assert "detail" in resp.json()


@pytest.mark.asyncio
async def test_condition_case_insensitive(client: AsyncClient):
    # Router lowercases the key, so CAVITY should work
    resp = await client.get("/treatments/CAVITY")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_empty_condition_returns_404(client: AsyncClient):
    # Effectively hits /treatments/ which won't match the param route
    resp = await client.get("/treatments/   ")
    assert resp.status_code == 404
