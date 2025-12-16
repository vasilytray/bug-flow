# backend/app/models/notification.py
from sqlalchemy import Column, String, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base, generate_uuid

class NotificationType(str, enum.Enum):
    ISSUE_ASSIGNED = "issue_assigned"
    ISSUE_MENTIONED = "issue_mentioned"
    COMMENT_ADDED = "comment_added"
    STATUS_CHANGED = "status_changed"
    DUE_DATE_APPROACHING = "due_date_approaching"
    PROJECT_INVITATION = "project_invitation"
    ISSUE_CREATED = "issue_created"

class NotificationStatus(str, enum.Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"))
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    message = Column(Text)
    data = Column(JSONB, default={})
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), default=func.now())
    read_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    issue = relationship("Issue")
    comment = relationship("Comment")
    project = relationship("Project")
    sender = relationship("User", foreign_keys=[sender_id])
    
    __table_args__ = (
        Index('idx_notifications_user_status', user_id, status, created_at.desc()),
        Index('idx_notifications_type', type),
    )
    
    def __repr__(self):
        return f"<Notification(user_id={self.user_id}, type='{self.type}', status='{self.status}')>"


class NotificationSetting(Base):
    __tablename__ = "notification_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    settings = Column(JSONB, default={
        "issue_assigned": {"email": True, "push": True, "in_app": True},
        "issue_mentioned": {"email": True, "push": True, "in_app": True},
        "comment_added": {"email": False, "push": True, "in_app": True},
        "status_changed": {"email": False, "push": False, "in_app": True},
        "due_date_approaching": {"email": True, "push": True, "in_app": True},
        "project_invitation": {"email": True, "push": True, "in_app": True}
    })
    
    # Relationships
    user = relationship("User")
    project = relationship("Project")
    
    __table_args__ = (
        Index('idx_notification_settings_user', user_id),
    )
    
    def __repr__(self):
        return f"<NotificationSetting(user_id={self.user_id}, project_id={self.project_id})>"