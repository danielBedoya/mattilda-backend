"""Tests for the School API routes."""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from uuid import uuid4

from app.main import app
from app.school.schema import SchoolRead


def test_create_school(authenticated_client: TestClient, mock_db_session):
    """Test the creation of a new school via the API."""
    school_data = {"name": "Test School API"}
    response = authenticated_client.post("/schools/", json=school_data)
    assert response.status_code == status.HTTP_200_OK
    school = SchoolRead(**response.json())
    assert school.name == school_data["name"]


def test_read_schools(authenticated_client: TestClient, mock_db_session):
    """Test retrieving a list of schools via the API."""
    response = authenticated_client.get("/schools/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_read_school(authenticated_client: TestClient, mock_db_session):
    """Test retrieving a single school by ID via the API."""
    school_id = uuid4()
    response = authenticated_client.get(f"/schools/{school_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_school(authenticated_client: TestClient, mock_db_session):
    """Test deleting a school by ID via the API."""
    school_id = uuid4()
    response = authenticated_client.delete(f"/schools/{school_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
