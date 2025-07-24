import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.main import app
from app.deps.db import get_db
from app.db.base import Base


# Setup for API tests
@pytest.fixture(scope="session")
def ac() -> TestClient:
    return TestClient(app=app)


# Setup for CRUD tests and API tests that need a mocked DB
@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.execute.return_value = MagicMock()
    session.execute.return_value.scalars.return_value = MagicMock()

    # Simulate a database of schools
    mock_schools_db = {}

    # Mock for get_school and delete_school
    def execute_side_effect(statement):
        if statement.whereclause is not None:
            # Extract school_id from the where clause
            # This assumes the where clause is in the format School.id == school_id
            school_id = None
            if hasattr(statement.whereclause, "right") and hasattr(
                statement.whereclause.right, "value"
            ):
                school_id = statement.whereclause.right.value
            elif (
                hasattr(statement.whereclause, "clauses")
                and len(statement.whereclause.clauses) > 0
                and hasattr(statement.whereclause.clauses[0], "right")
                and hasattr(statement.whereclause.clauses[0].right, "value")
            ):
                school_id = statement.whereclause.clauses[0].right.value

            mock_school = mock_schools_db.get(school_id)
            session.execute.return_value.scalars.return_value.first.return_value = (
                mock_school
            )
        else:
            # This is for get_schools
            session.execute.return_value.scalars.return_value.all.return_value = list(
                mock_schools_db.values()
            )
        return session.execute.return_value

    session.execute.side_effect = execute_side_effect

    # Mock for create_school
    async def mock_refresh(obj):
        obj.id = uuid4()
        obj.name = obj.name
        obj.address = obj.address
        mock_schools_db[obj.id] = obj

    session.refresh.side_effect = mock_refresh

    # Mock for delete_school
    async def mock_delete(obj):
        if obj.id in mock_schools_db:
            del mock_schools_db[obj.id]

    session.delete.side_effect = mock_delete

    return session


@pytest.fixture(autouse=True)
async def override_get_db(mock_db_session):
    async def _override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()
