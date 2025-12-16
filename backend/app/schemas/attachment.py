# backend/app/schemas/attachment.py
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
import uuid
from enum import StrEnum

from app.schemas.base import BaseSchema
from app.schemas.user import UserBase

class FileType(str, StrEnum):
    IMAGE = "image"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    LOG = "log"
    OTHER = "other"

# Input schemas
class AttachmentCreate(BaseSchema):
    filename: str
    original_name: str
    mime_type: str
    size_bytes: int
    description: Optional[str] = None
    
    @field_validator('size_bytes')
    def validate_size(cls, v):
        max_size = 50 * 1024 * 1024  # 50MB
        if v > max_size:
            raise ValueError(f'File size exceeds maximum of {max_size} bytes')
        return v

# Output schemas
class AttachmentBase(BaseSchema):
    id: uuid.UUID
    filename: str
    original_name: str
    mime_type: str
    file_type: FileType
    size_bytes: int
    description: Optional[str] = None

class Attachment(AttachmentBase):
    storage_path: str
    storage_bucket: str
    uploaded_by: UserBase
    created_at: datetime
    
    # Preview URLs
    download_url: Optional[str] = None
    preview_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # Metadata
    issue_id: Optional[uuid.UUID] = None
    comment_id: Optional[uuid.UUID] = None
    project_id: uuid.UUID

class ImagePreview(BaseSchema):
    id: uuid.UUID
    width: int
    height: int
    url: str

# Update forward ref для CommentWithAttachments
from app.schemas.comment import CommentWithAttachments
CommentWithAttachments.model_rebuild()