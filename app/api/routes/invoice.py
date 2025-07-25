from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.schemas.invoice import InvoiceCreate, InvoiceOut
from app.crud import invoice as crud_invoice
from app.deps.db import get_db
from app.deps.user import get_current_user
from app.models.user import User

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/", response_model=InvoiceOut)
async def create_invoice(
    invoice: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new invoice."""
    return await crud_invoice.create_invoice(db, invoice)


@router.get("/", response_model=List[InvoiceOut])
async def read_invoices(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a list of invoices."""
    return await crud_invoice.get_invoices(db, skip, limit)


@router.get("/{invoice_id}", response_model=InvoiceOut)
async def read_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single invoice by ID."""
    invoice = await crud_invoice.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.delete("/{invoice_id}", response_model=InvoiceOut)
async def delete_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an invoice by ID."""
    invoice = await crud_invoice.delete_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
