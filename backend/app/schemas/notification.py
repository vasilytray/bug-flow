# backend/app/schemas/notification.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from enum import StrEnum

from app.schemas.base import BaseSchema
from app.schemas.user import UserBase
from app.schemas.issue import IssueBase
from app.schemas.project import ProjectBase

class NotificationType(str, StrEnum):
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_MENTIONED = "issue_mentioned"
    COMMENT_ADDED = "comment_added"
    STATUS_CHANGED = "status_changed"
    DUE_DATE_APPROACHING = "due_date_approaching"
    PROJECT_INVITATION = "project_invitation"
    ISSUE_CREATED = "issue_created"

class NotificationStatus(str, StrEnum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

# Output schemas
class Notification(BaseSchema):
    id: uuid.UUID
    type: NotificationType
    status: NotificationStatus
    title: str
    message: Optional[str] = None
    data: Dict[str, Any]
    sender: Optional[UserBase] = None
    issue: Optional[IssueBase] = None
    project: Optional[ProjectBase] = None
    created_at: datetime
    read_at: Optional[datetime] = None

class NotificationSettings(BaseSchema):
    email_enabled: bool
    push_enabled: bool
    in_app_enabled: bool
    settings: Dict[str, Dict[str, bool]]

class NotificationUpdate(BaseSchema):
    status: Optional[NotificationStatus] = None