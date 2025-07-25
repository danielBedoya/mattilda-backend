"""Tests for the CRUD operations of the School model."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from app.crud.school import get_school, get_schools, create_school, delete_school
from app.models.school import School
from app.models.student import Student
from app.models.invoice import Invoice
from app.schemas.school import SchoolCreate


@pytest.fixture
def mock_db_session():
    """Fixture that provides a mocked AsyncSession for database interactions."""
    session = AsyncMock()
    session.execute.return_value = MagicMock()
    session.execute.return_value.scalars.return_value = MagicMock()
    return session


@pytest.mark.asyncio
async def test_get_school(mock_db_session):
    """Test retrieving a single school by its ID."""
    school_id = uuid4()
    mock_school = School(id=school_id, name="Test School")
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = (
        mock_school
    )

    school = await get_school(mock_db_session, school_id)

    assert school == mock_school
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_schools(mock_db_session):
    """Test retrieving a list of schools."""
    mock_schools = [
        School(id=uuid4(), name="School 1"),
        School(id=uuid4(), name="School 2"),
    ]
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = (
        mock_schools
    )

    schools = await get_schools(mock_db_session, skip=0, limit=10)

    assert schools == mock_schools
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_school(mock_db_session):
    """Test creating a new school."""
    school_create = SchoolCreate(name="New School")

    created_school = await create_school(mock_db_session, school_create)

    assert created_school.name == school_create.name
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(created_school)


@pytest.mark.asyncio
async def test_delete_school(mock_db_session):
    """Test deleting an existing school."""
    school_id = uuid4()
    mock_school = School(id=school_id, name="School to Delete")
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = (
        mock_school
    )

    deleted_school = await delete_school(mock_db_session, school_id)

    assert deleted_school == mock_school
    mock_db_session.delete.assert_called_once_with(mock_school)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_school_not_found(mock_db_session):
    """Test deleting a school that does not exist."""
    school_id = uuid4()
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = None

    deleted_school = await delete_school(mock_db_session, school_id)

    assert deleted_school is None
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()
