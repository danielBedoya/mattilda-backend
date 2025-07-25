from pydantic import BaseModel, EmailStr
from uuid import UUID


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    document_number: str
    address: str
    phone: str
    document_type_id: UUID
    school_id: UUID


class StudentCreate(StudentBase):
    pass


class DocumentTypeOut(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class StudentOut(StudentBase):
    id: UUID
    document_type: DocumentTypeOut

    class Config:
        from_attributes = True
