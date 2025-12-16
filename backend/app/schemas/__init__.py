# backend/app/schemas/__init__.py
from app.schemas.base import *
from app.schemas.user import *
from app.schemas.project import *
from app.schemas.issue import *
from app.schemas.comment import *
from app.schemas.attachment import *
from app.schemas.notification import *
from app.schemas.search import *

__all__ = [
    # Base
    "BaseSchema", "IDSchema", "TimestampSchema", "PaginationParams", "PaginatedResponse",
    
    # User
    "UserRole", "UserCreate", "UserUpdate", "UserLogin", "UserChangePassword",
    "UserBase", "User", "UserWithToken", "UserProfile", "Token", "TokenPayload",
    
    # Project
    "ProjectCreate", "ProjectUpdate", "ProjectInviteRequest", "ProjectMemberUpdate",
    "ProjectBase", "Project", "ProjectWithMembers", "ProjectMember", "ProjectInvitation",
    "ProjectStats", "ProjectSettings",
    
    # Issue
    "IssueType", "IssuePriority", "IssueLinkType",
    "IssueCreate", "IssueUpdate", "IssueFilter", "IssueLinkCreate",
    "IssueBase", "Issue", "IssueWithStats", "IssueHistory", "IssueSearchResult",
    "TagBase",
    
    # Comment
    "CommentCreate", "CommentUpdate", "CommentBase", "Comment", "CommentWithAttachments",
    "Activity",
    
    # Attachment
    "FileType", "AttachmentCreate", "AttachmentBase", "Attachment", "ImagePreview",
    
    # Notification
    "NotificationType", "NotificationStatus", "Notification", "NotificationSettings", 
    "NotificationUpdate",
    
    # Search
    "SearchQuery", "SearchResponse", "ReportQuery", "ReportResponse",
]