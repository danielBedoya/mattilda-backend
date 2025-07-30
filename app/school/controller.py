from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.user import get_current_user
from app.user.model import User
from .schema import SchoolCreate, SchoolRead
from . import service as school_service
from typing import List
from uuid import UUID

router = APIRouter(prefix="/schools", tags=["Schools"])


@router.post("/", response_model=SchoolRead)
async def create_school(
    school: SchoolCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new school.

    Args:
        school (SchoolCreate): The school data to create.
        db (AsyncSession): The database session.

    Returns:
        SchoolRead: The created school.
    """
    return await school_service.create_school(db, school)


@router.get("/", response_model=List[SchoolRead])
async def read_schools(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of schools.

    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to retrieve.
        db (AsyncSession): The database session.

    Returns:
        List[SchoolRead]: A list of schools.
    """
    return await school_service.get_schools(db, skip=skip, limit=limit)


@router.get("/{school_id}", response_model=SchoolRead)
async def read_school(school_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single school by its ID.

    Args:
        school_id (UUID): The ID of the school to retrieve.
        db (AsyncSession): The database session.

    Returns:
        SchoolRead: The retrieved school.

    Raises:
        HTTPException: If the school is not found.
    """
    db_school = await school_service.get_school(db, school_id)
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")
    return db_school


@router.delete("/{school_id}", response_model=SchoolRead)
async def delete_school(school_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Delete a school by its ID.

    Args:
        school_id (UUID): The ID of the school to delete.
        db (AsyncSession): The database session.

    Returns:
        SchoolRead: The deleted school.

    Raises:
        HTTPException: If the school is not found.
    """
    db_school = await school_service.delete_school(db, school_id)
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")
    return db_school
