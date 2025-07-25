from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid


class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    document_number = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    document_type_id = Column(
        UUID(as_uuid=True), ForeignKey("document_types.id"), nullable=False
    )
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"))

    school = relationship("School", back_populates="students")
    document_type = relationship("DocumentType")
