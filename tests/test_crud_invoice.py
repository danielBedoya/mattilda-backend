"""Tests for the CRUD operations of the Invoice model."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
from datetime import date

from app.crud.invoice import get_invoice, get_invoices, create_invoice, delete_invoice
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate


@pytest.fixture
def mock_db_session():
    """Fixture that provides a mocked AsyncSession for database interactions."""
    session = AsyncMock()
    session.execute.return_value = MagicMock()
    session.execute.return_value.scalars.return_value = MagicMock()
    return session


@pytest.mark.asyncio
async def test_get_invoice(mock_db_session):
    """Test retrieving a single invoice by its ID."""
    invoice_id = uuid4()
    mock_invoice = Invoice(
        id=invoice_id,
        amount=100.0,
        due_date=date.today(),
        status="pending",
        school_id=uuid4(),
    )
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_invoice

    invoice = await get_invoice(mock_db_session, invoice_id)

    assert invoice == mock_invoice
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_invoices(mock_db_session):
    """Test retrieving a list of invoices."""
    mock_invoices = [
        Invoice(
            id=uuid4(),
            amount=50.0,
            due_date=date.today(),
            status="pending",
            school_id=uuid4(),
        ),
        Invoice(
            id=uuid4(),
            amount=75.0,
            due_date=date.today(),
            status="paid",
            school_id=uuid4(),
        ),
    ]
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = (
        mock_invoices
    )

    invoices = await get_invoices(mock_db_session, skip=0, limit=10)

    assert invoices == mock_invoices
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_invoice(mock_db_session):
    """Test creating a new invoice."""
    invoice_create = InvoiceCreate(
        amount=120.0, due_date=date.today(), status="pending", school_id=uuid4()
    )

    created_invoice = await create_invoice(mock_db_session, invoice_create)

    assert created_invoice.amount == invoice_create.amount
    assert created_invoice.school_id == invoice_create.school_id
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(created_invoice)


@pytest.mark.asyncio
async def test_delete_invoice(mock_db_session):
    """Test deleting an existing invoice."""
    invoice_id = uuid4()
    mock_invoice = Invoice(
        id=invoice_id,
        amount=200.0,
        due_date=date.today(),
        status="pending",
        school_id=uuid4(),
    )
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_invoice

    deleted_invoice = await delete_invoice(mock_db_session, invoice_id)

    assert deleted_invoice == mock_invoice
    mock_db_session.delete.assert_called_once_with(mock_invoice)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_invoice_not_found(mock_db_session):
    """Test deleting an invoice that does not exist."""
    invoice_id = uuid4()
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

    deleted_invoice = await delete_invoice(mock_db_session, invoice_id)

    assert deleted_invoice is None
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()
