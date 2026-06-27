from sqlalchemy import Table, Column, Integer, String, Enum
from app.schemas import IssuePriority, IssueStatus
from app.database import meta

issues = Table(
    "issues",
    meta,
    Column(
        "id",
        Integer,
        primary_key=True,
        index=True,
    ),
    Column("title", String(100), nullable=False, unique=True),
    Column("description", String(1000), nullable=False),
    Column(
        "priority", Enum(IssuePriority), nullable=False, default=IssuePriority.medium
    ),
    Column("status", Enum(IssueStatus), nullable=False, default=IssueStatus.open),
)
