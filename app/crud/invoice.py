from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate


async def create_invoice(db: AsyncSession, invoice: InvoiceCreate) -> Invoice:
    db_invoice = Invoice(**invoice.model_dump())
    db.add(db_invoice)
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice


async def get_invoices(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Invoice).offset(skip).limit(limit))
    return result.scalars().all()


async def get_invoice(db: AsyncSession, invoice_id: UUID):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    return result.scalar_one_or_none()


async def delete_invoice(db: AsyncSession, invoice_id: UUID):
    invoice = await get_invoice(db, invoice_id)
    if invoice:
        await db.delete(invoice)
        await db.commit()
    return invoice
