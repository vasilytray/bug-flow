# backend/app/schemas/base.py
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import Optional, Any
from datetime import datetime
import uuid

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

class IDSchema(BaseSchema):
    id: uuid.UUID

class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: Optional[datetime] = None

class PaginationParams(BaseSchema):
    page: int = 1
    per_page: int = 50
    order_by: Optional[str] = None
    order_dir: Optional[str] = "desc"
    
    @field_validator('per_page')
    def validate_per_page(cls, v):
        if v > 100:
            raise ValueError('per_page cannot exceed 100')
        return v

class PaginatedResponse(BaseSchema):
    items: list[Any]
    total: int
    page: int
    per_page: int
    total_pages: int