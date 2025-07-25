from sqlalchemy import Column, Float, Date, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import date
import uuid


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    amount = Column(Float, nullable=False)
    due_date = Column(Date, default=date.today)
    status = Column(String, default="pending")
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"))
    school = relationship("School", back_populates="invoices")
