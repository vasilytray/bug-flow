# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, DateTime, func
import uuid
from typing import Optional
from datetime import datetime

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class TimestampMixin:
    """Mixin для добавления created_at и updated_at"""
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

class SoftDeleteMixin:
    """Mixin для мягкого удаления"""
    is_deleted = Column(DateTime(timezone=True), nullable=True, default=None)
    
    @property
    def is_active(self) -> bool:
        return self.is_deleted is None