from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentOut
import json
from app.deps.redis import redis_client


async def create_student(db: AsyncSession, student: StudentCreate) -> Student:
    """
    Creates a new student in the database.
    """
    db_student = Student(**student.model_dump())
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)

    # Eagerly load the document_type relationship to prevent validation errors
    result = await db.execute(
        select(Student)
        .options(selectinload(Student.document_type))
        .where(Student.id == db_student.id)
    )
    loaded_student = result.scalar_one_or_none()

    # Invalidate cache for all students and specific student
    if loaded_student:
        await redis_client.delete(f"student:{loaded_student.id}")
        await redis_client.delete(*await redis_client.keys("students:*"))
            
    return loaded_student


async def get_students(db: AsyncSession, skip: int = 0, limit: int = 10):
    """
    Retrieves a list of students from the database, with caching.
    """
    cache_key = f"students:skip={skip}:limit={limit}"
    cached_students = await redis_client.get(cache_key)
    if cached_students:
        return [StudentOut.model_validate_json(student) for student in json.loads(cached_students)]

    result = await db.execute(
        select(Student)
        .options(selectinload(Student.document_type))
        .offset(skip)
        .limit(limit)
    )
    db_students = result.scalars().all()
    if db_students:
        await redis_client.setex(cache_key, 3600, json.dumps([StudentOut.model_validate(student).model_dump_json() for student in db_students]))
    return db_students


async def get_student(db: AsyncSession, student_id: UUID):
    """
    Retrieves a single student by their ID, with caching.
    """
    cache_key = f"student:{student_id}"
    cached_student = await redis_client.get(cache_key)
    if cached_student:
        return StudentOut.model_validate_json(cached_student)

    result = await db.execute(
        select(Student)
        .options(selectinload(Student.document_type))
        .where(Student.id == student_id)
    )
    db_student = result.scalar_one_or_none()
    if db_student:
        await redis_client.setex(cache_key, 3600, StudentOut.model_validate(db_student).model_dump_json())
    return db_student


async def delete_student(db: AsyncSession, student_id: UUID):
    """
    Deletes a student from the database by their ID.
    """
    student = await get_student(db, student_id)
    if student:
        await db.delete(student)
        await db.commit()
        # Invalidate cache for the deleted student and all students
        await redis_client.delete(f"student:{student_id}")
        await redis_client.delete(*await redis_client.keys("students:*"))
    return student
