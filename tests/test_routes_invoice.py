"""Tests for the Invoice API routes."""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from uuid import uuid4, UUID
from datetime import date

from app.main import app
from app.invoice.schema import InvoiceOut


def test_create_invoice(authenticated_client: TestClient, mock_db_session):
    """Test the creation of a new invoice via the API."""
    invoice_data = {
        "amount": 150.0,
        "due_date": str(date.today()),
        "status": "pending",
        "school_id": str(uuid4()),
    }
    response = authenticated_client.post("/invoices/", json=invoice_data)
    assert response.status_code == status.HTTP_200_OK
    invoice = InvoiceOut(**response.json())
    assert invoice.amount == invoice_data["amount"]
    assert invoice.school_id == UUID(invoice_data["school_id"])


def test_read_invoices(authenticated_client: TestClient, mock_db_session):
    """Test retrieving a list of invoices via the API."""
    response = authenticated_client.get("/invoices/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_read_invoice(authenticated_client: TestClient, mock_db_session):
    """Test retrieving a single invoice by ID via the API."""
    invoice_id = uuid4()
    response = authenticated_client.get(f"/invoices/{invoice_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_invoice(authenticated_client: TestClient, mock_db_session):
    """Test deleting an invoice by ID via the API."""
    invoice_id = uuid4()
    response = authenticated_client.delete(f"/invoices/{invoice_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_invoice_unauthenticated(client: TestClient):
    """Test that creating an invoice fails without authentication."""
    invoice_data = {
        "amount": 100.0,
        "due_date": str(date.today()),
        "status": "pending",
        "school_id": str(uuid4()),
    }
    response = client.post("/invoices/", json=invoice_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_invoices_unauthenticated(client: TestClient):
    """Test that reading invoices fails without authentication."""
    response = client.get("/invoices/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_invoice_unauthenticated(client: TestClient):
    """Test that reading a single invoice fails without authentication."""
    invoice_id = uuid4()
    response = client.get(f"/invoices/{invoice_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_invoice_unauthenticated(client: TestClient):
    """Test that deleting an invoice fails without authentication."""
    invoice_id = uuid4()
    response = client.delete(f"/invoices/{invoice_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
