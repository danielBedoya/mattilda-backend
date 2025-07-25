from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.models.student import Student
from app.schemas.student import StudentCreate

from sqlalchemy.orm import selectinload


async def create_student(db: AsyncSession, student: StudentCreate) -> Student:
    """
    Creates a new student in the database.
    """
    db_student = Student(**student.model_dump())
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    # Eagerly load the document_type relationship
    await db.execute(
        select(Student)
        .options(selectinload(Student.document_type))
        .where(Student.id == db_student.id)
    )
    return db_student


async def get_students(db: AsyncSession, skip: int = 0, limit: int = 10):
    """
    Retrieves a list of students from the database.
    """
    result = await db.execute(
        select(Student)
        .options(selectinload(Student.document_type))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_student(db: AsyncSession, student_id: UUID):
    """
    Retrieves a single student by their ID.
    """
    result = await db.execute(
        select(Student)
        .options(selectinload(Student.document_type))
        .where(Student.id == student_id)
    )
    return result.scalar_one_or_none()


async def delete_student(db: AsyncSession, student_id: UUID):
    """
    Deletes a student from the database by their ID.
    """
    student = await get_student(db, student_id)
    if student:
        await db.delete(student)
        await db.commit()
    return student
