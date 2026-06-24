from enum import Enum as enum
from pydantic import BaseModel, Field
from typing import Optional


class issueStatus(str, enum):
    open = "open"
    in_progress = "in_progres"
    closed = "closed"


class issuePriority(str, enum):
    low = "low"
    medium = "medium"
    high = "high"


class createIssue(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=20, max_length=1000)
    priority: issuePriority = issuePriority.medium


class updateIssue(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=20, max_length=1000)
    priority: Optional[issuePriority] = None
    status: Optional[issueStatus] = None


class issueOut(BaseModel):
    id: str
    title: str
    description: str
    priority: issuePriority
    status: issueStatus
