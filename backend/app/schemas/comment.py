# backend/app/schemas/comment.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

from app.schemas.base import BaseSchema, TimestampSchema
from app.schemas.user import UserBase
from app.schemas.issue import IssueBase

# Input schemas
class CommentCreate(BaseSchema):
    content: str
    is_internal: bool = False
    attachments: List[uuid.UUID] = []  # attachment IDs
    
    @field_validator('content')
    def validate_content(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Comment cannot be empty')
        return v

class CommentUpdate(BaseSchema):
    content: Optional[str] = None
    is_internal: Optional[bool] = None

# Output schemas
class CommentBase(BaseSchema):
    id: uuid.UUID
    content: str
    content_html: Optional[str] = None
    is_internal: bool

class Comment(CommentBase, TimestampSchema):
    issue: IssueBase
    author: UserBase
    
    # For response
    can_edit: bool = False
    can_delete: bool = False

class CommentWithAttachments(Comment):
    attachments: List["Attachment"] = []  # будет определен позже

class Activity(BaseSchema):
    id: uuid.UUID
    activity_type: str
    data: Dict[str, Any]
    user: UserBase
    issue: Optional[IssueBase] = None
    created_at: datetime