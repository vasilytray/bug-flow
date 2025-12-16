# backend/app/models/project.py
from sqlalchemy import Column, String, Boolean, Text, ForeignKey, JSON, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy import event
import json

from app.core.database import Base, TimestampMixin, generate_uuid
from app.models.user import UserRole

class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    key = Column(String(10), unique=True, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    settings = Column(JSON, nullable=False, default={
        "workflow": {
            "statuses": [
                {"id": "open", "name": "Open", "color": "#3498db", "is_initial": True},
                {"id": "in_progress", "name": "In Progress", "color": "#f39c12"},
                {"id": "in_review", "name": "In Review", "color": "#9b59b6"},
                {"id": "resolved", "name": "Resolved", "color": "#2ecc71"},
                {"id": "closed", "name": "Closed", "color": "#95a5a6", "is_final": True}
            ],
            "transitions": [
                {"from": "open", "to": ["in_progress", "closed"]},
                {"from": "in_progress", "to": ["in_review", "open"]},
                {"from": "in_review", "to": ["resolved", "in_progress"]},
                {"from": "resolved", "to": ["closed", "in_review"]}
            ]
        },
        "issue_types": [
            {"id": "bug", "name": "Bug", "color": "#e74c3c", "icon": "🐛"},
            {"id": "feature", "name": "Feature", "color": "#2ecc71", "icon": "✨"},
            {"id": "task", "name": "Task", "color": "#3498db", "icon": "✅"},
            {"id": "improvement", "name": "Improvement", "color": "#9b59b6", "icon": "🔧"}
        ],
        "priorities": [
            {"id": "critical", "name": "Critical", "color": "#e74c3c", "level": 1},
            {"id": "high", "name": "High", "color": "#e67e22", "level": 2},
            {"id": "medium", "name": "Medium", "color": "#f1c40f", "level": 3},
            {"id": "low", "name": "Low", "color": "#2ecc71", "level": 4}
        ]
    })
    is_public = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    owner = relationship("User", back_populates="created_projects", foreign_keys=[owner_id])
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="project", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="project", cascade="all, delete-orphan")
    invitations = relationship("ProjectInvitation", back_populates="project", cascade="all, delete-orphan")
    
    @validates('key')
    def validate_key(self, key, value):
        if not value or len(value) > 10:
            raise ValueError('Project key must be 1-10 characters')
        if not value.isalnum():
            raise ValueError('Project key must be alphanumeric')
        return value.upper()
    
    def __repr__(self):
        return f"<Project(id={self.id}, key='{self.key}', name='{self.name}')>"


class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.DEVELOPER)
    permissions = Column(JSON, default={
        "can_create": True,
        "can_edit": True,
        "can_delete": False,
        "can_manage_members": False
    })
    joined_at = Column(DateTime(timezone=True), default=func.now())
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
    inviter = relationship("User", foreign_keys=[invited_by])
    
    __table_args__ = (
        CheckConstraint(
            "permissions::jsonb @> '{\"can_create\": true}'::jsonb OR "
            "permissions::jsonb @> '{\"can_create\": false}'::jsonb",
            name="check_permissions_json"
        ),
    )
    
    def __repr__(self):
        return f"<ProjectMember(project_id={self.project_id}, user_id={self.user_id}, role={self.role})>"


class ProjectInvitation(Base):
    __tablename__ = "project_invitations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.DEVELOPER)
    token_hash = Column(String(255), unique=True, nullable=False)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by])
    
    def __repr__(self):
        return f"<ProjectInvitation(project_id={self.project_id}, email='{self.email}')>"