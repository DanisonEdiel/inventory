import uuid
from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    
    # Additional fields for supplier sync
    external_id = Column(String, nullable=True, index=True)
    api_code = Column(String, nullable=True)
    last_sync_at = Column(String, nullable=True)
    sync_metadata = Column(JSON, nullable=True)
    
    # Relationship
    products = relationship("Product", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier {self.name}>"
