from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.school import School
from app.schemas.school import SchoolCreate
import uuid


async def get_school(db: AsyncSession, school_id: uuid.UUID):
    """
    Retrieve a single school by its ID.

    Args:
        db (AsyncSession): The database session.
        school_id (uuid.UUID): The ID of the school to retrieve.

    Returns:
        School: The retrieved school, or None if not found.
    """
    result = await db.execute(select(School).where(School.id == school_id))
    return result.scalars().first()


async def get_schools(db: AsyncSession, skip: int = 0, limit: int = 10):
    """
    Retrieve a list of schools.

    Args:
        db (AsyncSession): The database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to retrieve.

    Returns:
        List[School]: A list of schools.
    """
    result = await db.execute(select(School).offset(skip).limit(limit))
    return result.scalars().all()


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
    return db_school
