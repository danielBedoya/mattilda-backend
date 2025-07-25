"""Tests for the Student API routes."""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from uuid import uuid4

from app.main import app
from app.schemas.student import StudentOut
from app.models.student import Student
from app.models.document_type import DocumentType


def test_read_students(authenticated_client: TestClient, mock_db_session):
    """Test retrieving a list of students via the API."""
    response = authenticated_client.get("/students/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_read_student(authenticated_client: TestClient, mock_db_session):
    """Test retrieving a single student by ID via the API."""
    student_id = uuid4()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    response = authenticated_client.get(f"/students/{student_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_student(authenticated_client: TestClient, mock_db_session):
    """Test deleting a student by ID via the API."""
    student_id = uuid4()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    response = authenticated_client.delete(f"/students/{student_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_student_unauthenticated(client: TestClient):
    """Test that creating a student fails without authentication."""
    student_data = {
        "name": "Unauthorized Student",
        "email": "unauth@example.com",
        "document_number": "12345",
        "address": "Unauth St",
        "phone": "555-0000",
        "document_type_id": str(uuid4()),
        "school_id": str(uuid4()),
    }
    response = client.post("/students/", json=student_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_students_unauthenticated(client: TestClient):
    """Test that reading students fails without authentication."""
    response = client.get("/students/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_student_unauthenticated(client: TestClient):
    """Test that reading a single student fails without authentication."""
    student_id = uuid4()
    response = client.get(f"/students/{student_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_student_unauthenticated(client: TestClient):
    """Test that deleting a student fails without authentication."""
    student_id = uuid4()
    response = client.delete(f"/students/{student_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
