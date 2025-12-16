# backend/app/schemas/search.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.base import BaseSchema

class SearchQuery(BaseSchema):
    q: str
    project_id: Optional[str] = None
    limit: int = 20
    offset: int = 0

class SearchResultItem(BaseSchema):
    id: str
    type: str  # 'issue', 'comment', 'user'
    title: str
    description: Optional[str] = None
    project_key: Optional[str] = None
    issue_key: Optional[str] = None
    highlight: Dict[str, List[str]] = {}
    score: float

class SearchResponse(BaseSchema):
    results: List[SearchResultItem]
    total: int
    took_ms: int

class ReportQuery(BaseSchema):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    project_id: Optional[str] = None
    group_by: str = "day"  # day, week, month, status, type, priority, assignee

class ReportDataPoint(BaseSchema):
    label: str
    value: int
    color: Optional[str] = None

class ReportResponse(BaseSchema):
    type: str
    title: str
    data: List[ReportDataPoint]
    total: int