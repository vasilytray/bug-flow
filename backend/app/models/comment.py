# backend/app/models/comment.py
from sqlalchemy import Column, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base, TimestampMixin, generate_uuid

class Comment(Base, TimestampMixin):
    __tablename__ = "comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    content = Column(Text, nullable=False)
    content_html = Column(Text)
    is_internal = Column(Boolean, default=False)
    
    # Relationships
    issue = relationship("Issue", back_populates="comments")
    author = relationship("User", back_populates="comments")
    attachments = relationship("Attachment", back_populates="comment", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_comments_issue_created', issue_id, created_at.desc()),
    )
    
    def __repr__(self):
        return f"<Comment(id={self.id}, issue_id={self.issue_id}, author_id={self.author_id})>"


class IssueHistory(Base):
    __tablename__ = "issue_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    changed_field = Column(String(100), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    change_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    issue = relationship("Issue", back_populates="history")
    changer = relationship("User", foreign_keys=[changed_by])
    
    __table_args__ = (
        Index('idx_issue_history_issue_created', issue_id, created_at.desc()),
        Index('idx_issue_history_field', changed_field),
    )
    
    def __repr__(self):
        return f"<IssueHistory(issue_id={self.issue_id}, field='{self.changed_field}')>"


class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)
    data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="activities")
    issue = relationship("Issue")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_activities_project_created', project_id, created_at.desc()),
        Index('idx_activities_issue', issue_id),
        Index('idx_activities_type', activity_type),
    )
    
    def __repr__(self):
        return f"<Activity(type='{self.activity_type}', project_id={self.project_id})>"