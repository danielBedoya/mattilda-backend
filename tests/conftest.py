"""Pytest fixtures and configurations for testing the FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.main import app
from app.deps.db import get_db
from app.deps.user import get_current_user
from app.db.base import Base
from tests.mocks import MockUser, MockDocumentType


# Setup for API tests
@pytest.fixture(scope="session")
def client() -> TestClient:
    """Provides a TestClient for making requests to the FastAPI application."""
    return TestClient(app=app)


@pytest.fixture(scope="function")
def authenticated_client(client: TestClient):
    """Provides an authenticated TestClient for making requests to protected endpoints."""
    # Register a user (this will still interact with the mocked DB)
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }
    client.post("/auth/register", json=register_data)

    # Directly mock the login response to provide an access token
    # This bypasses the actual login logic and ensures a token is always available for tests
    token = "mock_access_token"
    client.headers["Authorization"] = f"Bearer {token}"
    return client


# Setup for CRUD tests and API tests that need a mocked DB
@pytest.fixture
def mock_db_session():
    """Provides a mocked AsyncSession for database interactions in tests."""
    session = AsyncMock()
    session.execute.return_value = MagicMock()
    session.execute.return_value.scalars.return_value = MagicMock()

    # Simulate a database of schools, users, students, and document types
    mock_schools_db = {}
    mock_users_db = {}
    mock_students_db = {}
    mock_document_types_db = {}

    # Add a default document type for testing
    default_document_type = MockDocumentType()
    mock_document_types_db[default_document_type.id] = default_document_type

    # Pre-hash a password for the test user
    from app.core.security import get_password_hash

    test_hashed_password = get_password_hash("testpassword")

    # Mock for db.execute
    def execute_side_effect(statement):
        # Check if the statement is for the User model
        if "users" in str(statement.compile()):
            mock_result = MagicMock()

            def scalar_side_effect():
                username = None
                if (
                    statement.whereclause is not None
                    and hasattr(statement.whereclause, "right")
                    and hasattr(statement.whereclause.right, "value")
                ):
                    username = statement.whereclause.right.value

                if username in mock_users_db:
                    return mock_users_db[username]
                else:
                    return None

            mock_result.scalar.side_effect = scalar_side_effect
            mock_result.scalar_one_or_none.side_effect = scalar_side_effect
            return mock_result
        # Check if the statement is for the Student model
        elif "students" in str(statement.compile()):
            mock_result = MagicMock()
            if statement.whereclause is not None:
                student_id = None
                if hasattr(statement.whereclause, "right") and hasattr(
                    statement.whereclause.right, "value"
                ):
                    student_id = statement.whereclause.right.value
                elif (
                    hasattr(statement.whereclause, "clauses")
                    and len(statement.whereclause.clauses) > 0
                    and hasattr(statement.whereclause.clauses[0], "right")
                    and hasattr(statement.whereclause.clauses[0].right, "value")
                ):
                    student_id = statement.whereclause.clauses[0].right.value

                mock_student = mock_students_db.get(student_id)
                if mock_student:
                    mock_student.document_type = (
                        mock_document_types_db.get(mock_student.document_type_id)
                        or default_document_type
                    )
                mock_result.scalar_one_or_none.return_value = mock_student
                return mock_result
            else:
                students_list = list(mock_students_db.values())
                for student in students_list:
                    student.document_type = (
                        mock_document_types_db.get(student.document_type_id)
                        or default_document_type
                    )
                mock_result.scalars.return_value.all.return_value = students_list
                return mock_result
        else:
            # Existing logic for schools
            if statement.whereclause is not None:
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
                session.execute.return_value.scalars.return_value.all.return_value = (
                    list(mock_schools_db.values())
                )
            return session.execute.return_value

    session.execute.side_effect = execute_side_effect

    # Mock for db.add
    async def mock_add(obj):
        if hasattr(obj, "username"):  # It's a User object
            mock_users_db[obj.username] = MockUser(
                obj.username, obj.email, test_hashed_password
            )
        elif hasattr(obj, "email") and hasattr(
            obj, "document_number"
        ):  # It's a Student object
            obj.document_type = (
                mock_document_types_db.get(obj.document_type_id)
                or default_document_type
            )
            mock_students_db[obj.id] = obj

    session.add.side_effect = mock_add

    # Mock for db.refresh
    async def mock_refresh(obj):
        if hasattr(obj, "username"):  # It's a User object
            obj.id = uuid4()  # Assign a UUID for user as well
        elif hasattr(obj, "email") and hasattr(
            obj, "document_number"
        ):  # It's a Student object
            obj.id = obj.id or uuid4()
            obj.document_type = (
                mock_document_types_db.get(obj.document_type_id)
                or default_document_type
            )
        elif hasattr(obj, "name"):  # It's a School object
            obj.id = uuid4()
            obj.name = obj.name
            obj.address = obj.address

    session.refresh.side_effect = mock_refresh

    # Mock for delete
    async def mock_delete(obj):
        if (
            hasattr(obj, "email")
            and hasattr(obj, "document_number")
            and obj.id in mock_students_db
        ):
            del mock_students_db[obj.id]
        elif hasattr(obj, "name") and obj.id in mock_schools_db:
            del mock_schools_db[obj.id]

    session.delete.side_effect = mock_delete

    return session


@pytest.fixture(autouse=True)
async def override_get_db(mock_db_session):
    """Overrides the get_db dependency to use the mocked database session."""

    async def _override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def override_get_current_user_dependency():
    """Overrides the get_current_user dependency to return a mock user for authenticated tests."""

    async def _override_get_current_user():
        return MockUser(
            username="testuser",
            email="test@example.com",
            hashed_password="mock_hashed_password",
        )

    app.dependency_overrides[get_current_user] = _override_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="function")
def authenticated_client(client: TestClient, override_get_current_user_dependency):
    """Provides an authenticated TestClient for making requests to protected endpoints."""
    # The override_get_current_user_dependency fixture handles the user mocking.
    # We just need to set a dummy token for the client.
    token = "mock_access_token"
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
    client.headers.pop("Authorization", None)  # Clean up headers after test
