from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class SchoolBase(BaseModel):
    name: str
    address: Optional[str] = None


class SchoolCreate(SchoolBase):
    pass


class SchoolRead(SchoolBase):
    id: UUID

    class Config:
        from_attributes = True
