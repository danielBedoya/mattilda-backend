from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from .schema import StudentCreate, StudentOut
from . import service as student_service
from app.deps.db import get_db
from app.deps.user import get_current_user
from app.user.model import User


router = APIRouter(prefix="/students", tags=["students"])


@router.post("/", response_model=StudentOut)
async def create_student(
    student: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new student."""
    return await student_service.create_student(db, student)


@router.get("/", response_model=List[StudentOut])
async def read_students(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a list of students."""
    return await student_service.get_students(db, skip, limit)


@router.get("/{student_id}", response_model=StudentOut)
async def read_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single student by ID."""
    student = await student_service.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.delete("/{student_id}", response_model=StudentOut)
async def delete_student(
    student_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a student by ID."""
    student = await student_service.delete_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
