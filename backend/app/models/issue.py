# backend/app/models/issue.py
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, Enum, CheckConstraint, Index, Computed
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import expression
import enum
from datetime import datetime

from app.core.database import Base, TimestampMixin, generate_uuid

class IssueType(str, enum.Enum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    IMPROVEMENT = "improvement"

class IssuePriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class IssueLinkType(str, enum.Enum):
    BLOCKS = "blocks"
    IS_BLOCKED_BY = "is_blocked_by"
    DUPLICATES = "duplicates"
    IS_DUPLICATED_BY = "is_duplicated_by"
    RELATES_TO = "relates_to"
    PARENT = "parent"
    CHILD = "child"

class Issue(Base, TimestampMixin):
    __tablename__ = "issues"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    description_html = Column(Text)
    type = Column(Enum(IssueType), default=IssueType.BUG)
    status = Column(String(50), nullable=False, default="open")
    priority = Column(Enum(IssuePriority), default=IssuePriority.MEDIUM)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    estimate_hours = Column(Integer, CheckConstraint("estimate_hours >= 0"), nullable=True)
    spent_hours = Column(Integer, CheckConstraint("spent_hours >= 0"), default=0)
    due_date = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    custom_fields = Column(JSONB, default={})
    
    # Generated column
    is_closed = Column(
        Boolean,
        Computed(
            expression.case(
                (status.in_(['closed', 'resolved']), True),
                else_=False
            ),
            persisted=True
        )
    )
    
    # Relationships
    project = relationship("Project", back_populates="issues")
    assignee = relationship("User", back_populates="assigned_issues", foreign_keys=[assignee_id])
    reporter = relationship("User", back_populates="reported_issues", foreign_keys=[reporter_id])
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")
    tags = relationship("IssueTag", back_populates="issue", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="issue", cascade="all, delete-orphan")
    history = relationship("IssueHistory", back_populates="issue", cascade="all, delete-orphan")
    
    # Links (both directions)
    outgoing_links = relationship(
        "IssueLink",
        foreign_keys="IssueLink.source_issue_id",
        back_populates="source_issue",
        cascade="all, delete-orphan"
    )
    incoming_links = relationship(
        "IssueLink",
        foreign_keys="IssueLink.target_issue_id",
        back_populates="target_issue",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_issues_project_status', project_id, status, postgresql_where=expression.text("is_closed = false")),
        Index('idx_issues_assignee', assignee_id, postgresql_where=expression.text("assignee_id IS NOT NULL")),
        Index('idx_issues_project_created', project_id, created_at.desc()),
        Index('idx_issues_due_date', due_date, postgresql_where=expression.text("due_date IS NOT NULL")),
        CheckConstraint("estimate_hours IS NULL OR estimate_hours >= 0", name="check_estimate_hours"),
        CheckConstraint("spent_hours >= 0", name="check_spent_hours"),
        {'postgresql_partition_by': 'LIST (project_id)'}  # Для больших проектов можно партиционировать
    )
    
    @validates('status')
    def validate_status(self, key, status):
        if self.project and self.project.settings:
            valid_statuses = [s['id'] for s in self.project.settings.get('workflow', {}).get('statuses', [])]
            if valid_statuses and status not in valid_statuses:
                raise ValueError(f'Invalid status. Valid statuses: {valid_statuses}')
        return status
    
    def __repr__(self):
        return f"<Issue(id={self.id}, key='{self.key}', title='{self.title[:30]}...')>"


class IssueLink(Base):
    __tablename__ = "issue_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    source_issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    target_issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    link_type = Column(Enum(IssueLinkType), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    source_issue = relationship("Issue", foreign_keys=[source_issue_id], back_populates="outgoing_links")
    target_issue = relationship("Issue", foreign_keys=[target_issue_id], back_populates="incoming_links")
    creator = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        Index('idx_issue_links_source', source_issue_id),
        Index('idx_issue_links_target', target_issue_id),
        Index('idx_issue_links_type', link_type),
        CheckConstraint("source_issue_id != target_issue_id", name="check_no_self_link"),
    )
    
    def __repr__(self):
        return f"<IssueLink(source={self.source_issue_id}, target={self.target_issue_id}, type={self.link_type})>"


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    color = Column(String(7), default="#3498db")
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="tags")
    issues = relationship("IssueTag", back_populates="tag", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_tags_project_name', project_id, name),
    )
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', color='{self.color}')>"


class IssueTag(Base):
    __tablename__ = "issue_tags"
    
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    added_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    issue = relationship("Issue", back_populates="tags")
    tag = relationship("Tag", back_populates="issues")
    adder = relationship("User", foreign_keys=[added_by])
    
    def __repr__(self):
        return f"<IssueTag(issue_id={self.issue_id}, tag_id={self.tag_id})>"