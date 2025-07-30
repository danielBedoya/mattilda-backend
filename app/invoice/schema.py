from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
from typing import Literal


class InvoiceBase(BaseModel):
    amount: float
    due_date: date = Field(default_factory=date.today)
    status: Literal["pending", "paid", "cancelled"] = "pending"
    school_id: UUID


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceOut(InvoiceBase):
    id: UUID

    class Config:
        from_attributes = True
