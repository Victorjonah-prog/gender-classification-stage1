from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from models import Profile


async def get_profile_by_name(db: AsyncSession, name: str):
    result = await db.execute(
        select(Profile).where(func.lower(Profile.name) == name.lower())
    )
    return result.scalars().first()


async def get_profile_by_id(db: AsyncSession, profile_id: str):
    result = await db.execute(
        select(Profile).where(Profile.id == profile_id)
    )
    return result.scalars().first()


async def get_all_profiles(db: AsyncSession, gender=None, country_id=None, age_group=None):
    query = select(Profile)

    if gender:
        query = query.where(func.lower(Profile.gender) == gender.lower())
    if country_id:
        query = query.where(func.lower(Profile.country_id) == country_id.lower())
    if age_group:
        query = query.where(func.lower(Profile.age_group) == age_group.lower())

    result = await db.execute(query)
    return result.scalars().all()


async def create_profile(db: AsyncSession, profile_data: dict):
    profile = Profile(**profile_data)
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def delete_profile(db: AsyncSession, profile: Profile):
    await db.delete(profile)
    await db.commit()