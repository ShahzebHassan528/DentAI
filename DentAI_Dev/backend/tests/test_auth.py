"""
Tests for /auth endpoints:
  POST /auth/register
  POST /auth/login
  POST /auth/refresh
  GET  /auth/me
"""

import pytest
from httpx import AsyncClient


# ─────────────────────────────────────────────
# Register
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_patient_success(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "name": "Alice",
        "email": "alice@test.com",
        "password": "SecurePass1!",
        "role": "patient",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_register_doctor_success(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "name": "Dr. Bob",
        "email": "bob_doctor@test.com",
        "password": "SecurePass1!",
        "role": "doctor",
    })
    assert resp.status_code == 201
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "name": "Duplicate",
        "email": "duplicate@test.com",
        "password": "SecurePass1!",
        "role": "patient",
    }
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient):
    # Missing password
    resp = await client.post("/auth/register", json={
        "name": "No Pass",
        "email": "nopass@test.com",
        "role": "patient",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_role(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "name": "Bad Role",
        "email": "badrole@test.com",
        "password": "SecurePass1!",
        "role": "admin",          # invalid — only patient / doctor
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email_format(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "name": "Bad Email",
        "email": "not-an-email",
        "password": "SecurePass1!",
        "role": "patient",
    })
    assert resp.status_code == 422


# ─────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # Register first, then login
    await client.post("/auth/register", json={
        "name": "Login User",
        "email": "login_user@test.com",
        "password": "SecurePass1!",
        "role": "patient",
    })
    resp = await client.post("/auth/login", json={
        "email": "login_user@test.com",
        "password": "SecurePass1!",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/auth/register", json={
        "name": "Wrong Pass",
        "email": "wrongpass@test.com",
        "password": "CorrectPass1!",
        "role": "patient",
    })
    resp = await client.post("/auth/login", json={
        "email": "wrongpass@test.com",
        "password": "WrongPass999!",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient):
    resp = await client.post("/auth/login", json={
        "email": "nobody@test.com",
        "password": "Whatever1!",
    })
    assert resp.status_code == 401


# ─────────────────────────────────────────────
# Token refresh
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient):
    reg = await client.post("/auth/register", json={
        "name": "Refresh User",
        "email": "refresh@test.com",
        "password": "SecurePass1!",
        "role": "patient",
    })
    refresh_token = reg.json()["refresh_token"]

    resp = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    resp = await client.post("/auth/refresh", json={"refresh_token": "totally.invalid.token"})
    assert resp.status_code == 401


# ─────────────────────────────────────────────
# /me
# ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient, patient_headers: dict):
    resp = await client.get("/auth/me", headers=patient_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "email" in data
    assert "role" in data


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/auth/me")
    # HTTPBearer returns 403 when header is missing, 401 when token is invalid
    assert resp.status_code in (401, 403)
