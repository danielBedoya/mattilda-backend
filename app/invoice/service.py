from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from .model import Invoice
from .schema import InvoiceCreate, InvoiceOut
import json
from app.deps.redis import redis_client


async def create_invoice(db: AsyncSession, invoice: InvoiceCreate) -> Invoice:
    """Creates a new invoice in the database."""
    db_invoice = Invoice(**invoice.model_dump())
    db.add(db_invoice)
    await db.commit()
    await db.refresh(db_invoice)
    # Invalidate cache for all invoices and specific invoice
    await redis_client.delete(f"invoice:{db_invoice.id}")
    await redis_client.delete(*await redis_client.keys("invoices:*"))
    return db_invoice


async def get_invoices(db: AsyncSession, skip: int = 0, limit: int = 10):
    """Retrieves a list of invoices from the database, with caching."""
    cache_key = f"invoices:skip={skip}:limit={limit}"
    cached_invoices = await redis_client.get(cache_key)
    if cached_invoices:
        return [InvoiceOut.model_validate_json(invoice) for invoice in json.loads(cached_invoices)]

    result = await db.execute(select(Invoice).offset(skip).limit(limit))
    db_invoices = result.scalars().all()
    if db_invoices:
        await redis_client.setex(cache_key, 3600, json.dumps([InvoiceOut.model_validate(invoice).model_dump_json() for invoice in db_invoices]))
    return db_invoices


async def get_invoice(db: AsyncSession, invoice_id: UUID):
    """Retrieves a single invoice by its ID, with caching."""
    cache_key = f"invoice:{invoice_id}"
    cached_invoice = await redis_client.get(cache_key)
    if cached_invoice:
        return InvoiceOut.model_validate_json(cached_invoice)

    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    db_invoice = result.scalar_one_or_none()
    if db_invoice:
        await redis_client.setex(cache_key, 3600, InvoiceOut.model_validate(db_invoice).model_dump_json())
    return db_invoice


async def delete_invoice(db: AsyncSession, invoice_id: UUID):
    """Deletes an invoice from the database by its ID."""
    invoice = await get_invoice(db, invoice_id)
    if invoice:
        await db.delete(invoice)
        await db.commit()
        # Invalidate cache for the deleted invoice and all invoices
        await redis_client.delete(f"invoice:{invoice_id}")
        await redis_client.delete(*await redis_client.keys("invoices:*"))
    return invoice
