from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.school import School
from app.schemas.school import SchoolCreate, SchoolRead
import uuid
import json
from app.deps.redis import redis_client


async def get_school(db: AsyncSession, school_id: uuid.UUID):
    """
    Retrieve a single school by its ID, with caching.

    Args:
        db (AsyncSession): The database session.
        school_id (uuid.UUID): The ID of the school to retrieve.

    Returns:
        School: The retrieved school, or None if not found.
    """
    cache_key = f"school:{school_id}"
    cached_school = await redis_client.get(cache_key)
    if cached_school:
        return SchoolRead.model_validate_json(cached_school)

    result = await db.execute(select(School).where(School.id == school_id))
    db_school = result.scalars().first()
    if db_school:
        await redis_client.setex(cache_key, 3600, SchoolRead.model_validate(db_school).model_dump_json())
    return db_school


async def get_schools(db: AsyncSession, skip: int = 0, limit: int = 10):
    """
    Retrieve a list of schools, with caching.

    Args:
        db (AsyncSession): The database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to retrieve.

    Returns:
        List[School]: A list of schools.
    """
    cache_key = f"schools:skip={skip}:limit={limit}"
    cached_schools = await redis_client.get(cache_key)
    if cached_schools:
        return [SchoolRead.model_validate_json(school) for school in json.loads(cached_schools)]

    result = await db.execute(select(School).offset(skip).limit(limit))
    db_schools = result.scalars().all()
    if db_schools:
        await redis_client.setex(cache_key, 3600, json.dumps([SchoolRead.model_validate(school).model_dump_json() for school in db_schools]))
    return db_schools


async def create_school(db: AsyncSession, school: SchoolCreate):
    """
    Create a new school.

    Args:
        db (AsyncSession): The database session.
        school (SchoolCreate): The school data to create.

    Returns:
        School: The created school.
    """
    db_school = School(**school.model_dump())
    db.add(db_school)
    await db.commit()
    await db.refresh(db_school)
    # Invalidate cache for all schools and specific school
    await redis_client.delete(f"school:{db_school.id}")
    # Invalidate all 'get_schools' caches (more robust invalidation might be needed for large datasets)
    for key in await redis_client.keys("schools:*"):
        await redis_client.delete(key)
    return db_school


async def delete_school(db: AsyncSession, school_id: uuid.UUID):
    """
    Delete a school by its ID.

    Args:
        db (AsyncSession): The database session.
        school_id (uuid.UUID): The ID of the school to delete.

    Returns:
        School: The deleted school, or None if not found.
    """
    result = await db.execute(select(School).where(School.id == school_id))
    db_school = result.scalars().first()
    if db_school:
        await db.delete(db_school)
        await db.commit()
        # Invalidate cache for the deleted school and all schools
        await redis_client.delete(f"school:{school_id}")
        for key in await redis_client.keys("schools:*"):
            await redis_client.delete(key)
    return db_school
