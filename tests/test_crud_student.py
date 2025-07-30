"""Tests for the CRUD operations of the Student model."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from app.student.service import get_student, get_students, create_student, delete_student
from app.student.model import Student
from app.document_type.model import DocumentType
from app.student.schema import StudentCreate


@pytest.fixture
def mock_db_session():
    """Fixture that provides a mocked AsyncSession for database interactions."""
    session = AsyncMock()
    session.execute.return_value = MagicMock()
    session.execute.return_value.scalars.return_value = MagicMock()
    return session


@pytest.mark.asyncio
async def test_get_student(mock_db_session):
    """Test retrieving a single student by their ID."""
    student_id = uuid4()
    mock_document_type = DocumentType(id=uuid4(), name="DNI")
    mock_student = Student(
        id=student_id,
        name="Test Student",
        email="test@example.com",
        document_number="12345",
        address="123 Test St",
        phone="555-1234",
        document_type_id=mock_document_type.id,
        school_id=uuid4(),
        document_type=mock_document_type,
    )
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_student

    student = await get_student(mock_db_session, student_id)

    assert student == mock_student
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_students(mock_db_session):
    """Test retrieving a list of students."""
    mock_document_type = DocumentType(id=uuid4(), name="DNI")
    mock_students = [
        Student(
            id=uuid4(),
            name="Student 1",
            email="student1@example.com",
            document_number="111",
            address="111 Test St",
            phone="555-1111",
            document_type_id=mock_document_type.id,
            school_id=uuid4(),
            document_type=mock_document_type,
        ),
        Student(
            id=uuid4(),
            name="Student 2",
            email="student2@example.com",
            document_number="222",
            address="222 Test St",
            phone="555-2222",
            document_type_id=mock_document_type.id,
            school_id=uuid4(),
            document_type=mock_document_type,
        ),
    ]
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = (
        mock_students
    )

    students = await get_students(mock_db_session, skip=0, limit=10)

    assert students == mock_students
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_student(mock_db_session):
    """Test creating a new student."""
    student_create = StudentCreate(
        name="New Student",
        email="new@example.com",
        document_number="333",
        address="333 New St",
        phone="555-3333",
        document_type_id=uuid4(),
        school_id=uuid4(),
    )

    mock_student_to_return = Student(
        id=uuid4(),
        name=student_create.name,
        email=student_create.email,
        document_number=student_create.document_number,
        address=student_create.address,
        phone=student_create.phone,
        document_type_id=student_create.document_type_id,
        school_id=student_create.school_id,
        document_type=DocumentType(id=student_create.document_type_id, name="DNI"),
    )
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_student_to_return

    created_student = await create_student(mock_db_session, student_create)

    assert created_student == mock_student_to_return
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_delete_student(mock_db_session):
    """Test deleting an existing student."""
    student_id = uuid4()
    mock_document_type = DocumentType(id=uuid4(), name="DNI")
    mock_student = Student(
        id=student_id,
        name="Student to Delete",
        email="delete@example.com",
        document_number="444",
        address="444 Delete St",
        phone="555-4444",
        document_type_id=mock_document_type.id,
        school_id=uuid4(),
        document_type=mock_document_type,
    )
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_student

    deleted_student = await delete_student(mock_db_session, student_id)

    assert deleted_student == mock_student
    mock_db_session.delete.assert_called_once_with(mock_student)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_student_not_found(mock_db_session):
    """Test deleting a student that does not exist."""
    student_id = uuid4()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    deleted_student = await delete_student(mock_db_session, student_id)

    assert deleted_student is None
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()
