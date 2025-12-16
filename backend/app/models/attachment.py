# backend/app/models/attachment.py
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, CheckConstraint, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
import enum

from app.core.database import Base, generate_uuid

class FileType(str, enum.Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    LOG = "log"
    OTHER = "other"

class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    storage_path = Column(String(500), unique=True, nullable=False)
    storage_bucket = Column(String(100), default="attachments")
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"))
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    issue = relationship("Issue", back_populates="attachments")
    comment = relationship("Comment", back_populates="attachments")
    project = relationship("Project")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    previews = relationship("ImagePreview", back_populates="attachment", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint(
            "(issue_id IS NOT NULL AND comment_id IS NULL) OR (issue_id IS NULL AND comment_id IS NOT NULL)",
            name="check_attachment_reference"
        ),
        CheckConstraint("size_bytes > 0", name="check_positive_size"),
        Index('idx_attachments_issue', issue_id),
        Index('idx_attachments_comment', comment_id),
        Index('idx_attachments_project', project_id),
    )
    
    @validates('size_bytes')
    def validate_size(self, key, size):
        max_size = 50 * 1024 * 1024  # 50MB
        if size > max_size:
            raise ValueError(f'File size exceeds maximum of {max_size} bytes')
        return size
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.filename}', size={self.size_bytes})>"


class ImagePreview(Base):
    __tablename__ = "image_previews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    attachment_id = Column(UUID(as_uuid=True), ForeignKey("attachments.id", ondelete="CASCADE"), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    storage_path = Column(String(500), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    attachment = relationship("Attachment", back_populates="previews")
    
    __table_args__ = (
        Index('idx_image_previews_attachment', attachment_id),
    )
    
    def __repr__(self):
        return f"<ImagePreview(attachment_id={self.attachment_id}, {self.width}x{self.height})>"