from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class IssueStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class IssuePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class CreateIssue(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=20, max_length=1000)
    priority: IssuePriority = IssuePriority.medium


class UpdateIssue(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=20, max_length=1000)
    priority: Optional[IssuePriority] = None
    status: Optional[IssueStatus] = None


class IssueOut(BaseModel):
    id: int
    title: str
    description: str
    priority: IssuePriority
    status: IssueStatus


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class CreateUser(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=255)
    role: UserRole = UserRole.user


class UpdateUser(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=5, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    role: Optional[UserRole] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
