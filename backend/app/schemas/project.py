# backend/app/schemas/project.py
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.schemas.base import BaseSchema, TimestampSchema
from app.schemas.user import UserBase, UserRole

# Workflow schemas
class WorkflowStatus(BaseSchema):
    id: str
    name: str
    color: str
    is_initial: Optional[bool] = False
    is_final: Optional[bool] = False

class WorkflowTransition(BaseSchema):
    from_status: str
    to_statuses: List[str]

class IssueTypeConfig(BaseSchema):
    id: str
    name: str
    color: str
    icon: str

class PriorityConfig(BaseSchema):
    id: str
    name: str
    color: str
    level: int

class ProjectSettings(BaseSchema):
    workflow: Dict[str, Any]
    issue_types: List[IssueTypeConfig]
    priorities: List[PriorityConfig]

# Input schemas
class ProjectCreate(BaseSchema):
    name: str
    description: Optional[str] = None
    key: str
    is_public: bool = False
    settings: Optional[ProjectSettings] = None
    
    @field_validator('key')
    def validate_key(cls, v):
        if len(v) > 10:
            raise ValueError('Project key must be max 10 characters')
        if not v.isalnum():
            raise ValueError('Project key must be alphanumeric')
        return v.upper()

class ProjectUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_archived: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None

class ProjectInviteRequest(BaseSchema):
    email: str
    role: UserRole = UserRole.DEVELOPER

class ProjectMemberUpdate(BaseSchema):
    role: Optional[UserRole] = None
    permissions: Optional[Dict[str, Any]] = None

# Output schemas
class ProjectBase(BaseSchema):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    key: str
    is_public: bool
    is_archived: bool

class Project(ProjectBase, TimestampSchema):
    owner: UserBase
    settings: Dict[str, Any]
    members_count: int = 0
    issues_count: int = 0
    open_issues_count: int = 0

class ProjectMember(BaseSchema):
    id: uuid.UUID
    user: UserBase
    role: UserRole
    permissions: Dict[str, Any]
    joined_at: datetime
    invited_by: Optional[UserBase] = None

class ProjectWithMembers(Project):
    members: List[ProjectMember]

class ProjectInvitation(BaseSchema):
    id: uuid.UUID
    email: str
    role: UserRole
    invited_by: UserBase
    expires_at: datetime
    created_at: datetime
    accepted_at: Optional[datetime] = None

class ProjectStats(BaseSchema):
    total_issues: int
    open_issues: int
    closed_issues: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]
    by_status: Dict[str, int]