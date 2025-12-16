# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from enum import StrEnum

from app.schemas.base import BaseSchema, TimestampSchema

class UserRole(str, StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    PROJECT_ADMIN = "project_admin"
    DEVELOPER = "developer"
    TESTER = "tester"
    VIEWER = "viewer"

# Input schemas
class UserCreate(BaseSchema):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    password: str
    
    @field_validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[UserRole] = None
    
    @field_validator('username')
    def validate_username(cls, v):
        if v and len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v.lower() if v else v

class UserLogin(BaseSchema):
    email: EmailStr
    password: str
    remember_me: bool = False

class UserChangePassword(BaseSchema):
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

# Output schemas
class UserBase(BaseSchema):
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole

class User(UserBase, TimestampSchema):
    is_active: bool
    email_verified: bool
    last_login_at: Optional[datetime] = None

class UserWithToken(User):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserProfile(User):
    projects_count: int = 0
    assigned_issues_count: int = 0
    reported_issues_count: int = 0

# Auth schemas
class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseSchema):
    sub: str  # user_id
    exp: int
    role: UserRole

class RefreshTokenRequest(BaseSchema):
    refresh_token: str