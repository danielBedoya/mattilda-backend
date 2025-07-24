import pytest
from fastapi.testclient import TestClient
from fastapi import status
from uuid import uuid4

from app.main import app
from app.schemas.school import SchoolRead


def test_create_school(ac: TestClient, mock_db_session):
    school_data = {"name": "Test School API"}
    response = ac.post("/schools/", json=school_data)
    assert response.status_code == status.HTTP_200_OK
    school = SchoolRead(**response.json())
    assert school.name == school_data["name"]


def test_read_schools(ac: TestClient, mock_db_session):
    response = ac.get("/schools/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_read_school(ac: TestClient, mock_db_session):
    school_id = uuid4()
    response = ac.get(f"/schools/{school_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_school(ac: TestClient, mock_db_session):
    school_id = uuid4()
    response = ac.delete(f"/schools/{school_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
