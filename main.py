from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional
import uuid6

from database import get_db, engine, Base
from models import Profile
from schemas import CreateProfileRequest, ProfileFull, ProfileSummary
from crud import (
    get_profile_by_name, get_profile_by_id,
    get_all_profiles, create_profile, delete_profile
)
from external import fetch_all

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message}
    )


# ── POST /api/profiles ────────────────────────────────────────────────────────
@app.post("/api/profiles")
async def create_profile_endpoint(
    body: CreateProfileRequest,
    db: AsyncSession = Depends(get_db)
):
    if not body.name or body.name.strip() == "":
        return error_response(400, "Missing or empty name")

    if not isinstance(body.name, str):
        return error_response(422, "Name must be a string")

    # Check if profile already exists
    existing = await get_profile_by_name(db, body.name)
    if existing:
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Profile already exists",
                "data": ProfileFull.from_orm(existing).model_dump()
            }
        )

    # Fetch from all 3 APIs
    try:
        api_data = await fetch_all(body.name)
    except ValueError as e:
        return error_response(502, str(e))
    except Exception:
        return error_response(500, "Internal server error")

    # Build profile
    profile_data = {
        "id": str(uuid6.uuid7()),
        "name": body.name.lower(),
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **api_data
    }

    profile = await create_profile(db, profile_data)

    return JSONResponse(
        status_code=201,
        content={
            "status": "success",
            "data": ProfileFull.from_orm(profile).model_dump()
        }
    )


# ── GET /api/profiles ─────────────────────────────────────────────────────────
@app.get("/api/profiles")
async def list_profiles(
    gender: Optional[str] = Query(default=None),
    country_id: Optional[str] = Query(default=None),
    age_group: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    profiles = await get_all_profiles(db, gender, country_id, age_group)

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "count": len(profiles),
            "data": [ProfileSummary.from_orm(p).model_dump() for p in profiles]
        }
    )


# ── GET /api/profiles/{id} ────────────────────────────────────────────────────
@app.get("/api/profiles/{profile_id}")
async def get_profile(profile_id: str, db: AsyncSession = Depends(get_db)):
    profile = await get_profile_by_id(db, profile_id)
    if not profile:
        return error_response(404, "Profile not found")

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": ProfileFull.from_orm(profile).model_dump()
        }
    )


# ── DELETE /api/profiles/{id} ─────────────────────────────────────────────────
@app.delete("/api/profiles/{profile_id}")
async def delete_profile_endpoint(profile_id: str, db: AsyncSession = Depends(get_db)):
    profile = await get_profile_by_id(db, profile_id)
    if not profile:
        return error_response(404, "Profile not found")

    await delete_profile(db, profile)
    return JSONResponse(status_code=204, content=None)