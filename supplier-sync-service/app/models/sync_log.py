import uuid
from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class SupplierSyncLog(Base):
    __tablename__ = "supplier_sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    sync_type = Column(String, nullable=False)  # 'scheduled', 'manual'
    status = Column(String, nullable=False)  # 'success', 'failed', 'partial'
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    products_added = Column(Integer, default=0)
    products_updated = Column(Integer, default=0)
    products_deactivated = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationship
    supplier = relationship("Supplier")

    def __repr__(self):
        return f"<SupplierSyncLog {self.id} - {self.supplier.name if self.supplier else 'Unknown'} - {self.status}>"
