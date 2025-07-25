from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.schemas.student import StudentCreate, StudentOut
from app.crud import student as crud_student
from app.deps.db import get_db


router = APIRouter(prefix="/students", tags=["students"])


@router.post("/", response_model=StudentOut)
async def create_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    return await crud_student.create_student(db, student)


@router.get("/", response_model=List[StudentOut])
async def read_students(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await crud_student.get_students(db, skip, limit)


@router.get("/{student_id}", response_model=StudentOut)
async def read_student(student_id: UUID, db: AsyncSession = Depends(get_db)):
    student = await crud_student.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.delete("/{student_id}", response_model=StudentOut)
async def delete_student(student_id: UUID, db: AsyncSession = Depends(get_db)):
    student = await crud_student.delete_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
