import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    is_active = Column(Boolean, default=True)

    # Relationship
    supplier = relationship("Supplier", back_populates="products")

    def __repr__(self):
        return f"<Product {self.name}>"
