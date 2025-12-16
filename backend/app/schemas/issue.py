# backend/app/schemas/issue.py
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import StrEnum

from app.schemas.base import BaseSchema, TimestampSchema
from app.schemas.user import UserBase
from app.schemas.project import ProjectBase

class IssueType(str, StrEnum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    IMPROVEMENT = "improvement"

class IssuePriority(str, StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class IssueLinkType(str, StrEnum):
    BLOCKS = "blocks"
    IS_BLOCKED_BY = "is_blocked_by"
    DUPLICATES = "duplicates"
    IS_DUPLICATED_BY = "is_duplicated_by"
    RELATES_TO = "relates_to"
    PARENT = "parent"
    CHILD = "child"

# Input schemas
class IssueCreate(BaseSchema):
    title: str
    description: Optional[str] = None
    type: IssueType = IssueType.BUG
    priority: IssuePriority = IssuePriority.MEDIUM
    assignee_id: Optional[uuid.UUID] = None
    estimate_hours: Optional[int] = None
    due_date: Optional[datetime] = None
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    
    @field_validator('title')
    def validate_title(cls, v):
        if len(v) < 5:
            raise ValueError('Title must be at least 5 characters')
        if len(v) > 500:
            raise ValueError('Title must be max 500 characters')
        return v
    
    @field_validator('estimate_hours')
    def validate_estimate(cls, v):
        if v is not None and v < 0:
            raise ValueError('Estimate hours cannot be negative')
        return v

class IssueUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[IssueType] = None
    status: Optional[str] = None
    priority: Optional[IssuePriority] = None
    assignee_id: Optional[uuid.UUID] = None
    estimate_hours: Optional[int] = None
    spent_hours: Optional[int] = None
    due_date: Optional[datetime] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    @field_validator('spent_hours')
    def validate_spent_hours(cls, v):
        if v is not None and v < 0:
            raise ValueError('Spent hours cannot be negative')
        return v

class IssueFilter(BaseSchema):
    status: Optional[List[str]] = None
    type: Optional[List[IssueType]] = None
    priority: Optional[List[IssuePriority]] = None
    assignee_id: Optional[List[uuid.UUID]] = None
    reporter_id: Optional[List[uuid.UUID]] = None
    tags: Optional[List[str]] = None
    is_closed: Optional[bool] = None
    search: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None

class IssueLinkCreate(BaseSchema):
    target_issue_id: uuid.UUID
    link_type: IssueLinkType
    
    @field_validator('target_issue_id')
    def validate_target_issue(cls, v, info):
        if 'source_issue_id' in info.data and v == info.data['source_issue_id']:
            raise ValueError('Cannot link issue to itself')
        return v

# Output schemas
class IssueBase(BaseSchema):
    id: uuid.UUID
    key: str
    title: str
    type: IssueType
    status: str
    priority: IssuePriority
    is_closed: bool

class TagBase(BaseSchema):
    id: uuid.UUID
    name: str
    color: str
    description: Optional[str] = None

class IssueLink(BaseSchema):
    id: uuid.UUID
    link_type: IssueLinkType
    source_issue: IssueBase
    target_issue: IssueBase
    created_by: UserBase
    created_at: datetime

class Issue(IssueBase, TimestampSchema):
    description: Optional[str] = None
    description_html: Optional[str] = None
    estimate_hours: Optional[int] = None
    spent_hours: int = 0
    due_date: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    custom_fields: Dict[str, Any] = {}
    
    project: ProjectBase
    assignee: Optional[UserBase] = None
    reporter: UserBase
    
    tags: List[TagBase] = []
    outgoing_links: List[IssueLink] = []
    incoming_links: List[IssueLink] = []
    
    # Computed fields
    comments_count: int = 0
    attachments_count: int = 0
    history_count: int = 0

class IssueWithStats(Issue):
    time_estimate: Optional[int] = None  # в часах
    time_spent: int = 0
    time_remaining: Optional[int] = None
    overdue: bool = False
    days_open: Optional[int] = None

class IssueHistory(BaseSchema):
    id: uuid.UUID
    changed_field: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_data: Optional[Dict[str, Any]] = None
    changed_by: UserBase
    created_at: datetime

class IssueSearchResult(BaseSchema):
    issues: List[Issue]
    total: int
    facets: Dict[str, Dict[str, int]] = {}