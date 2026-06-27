from sqlalchemy import Table, Column, Integer, String, Enum
from app.schemas import issuePriority, issueStatus
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
        "priority", Enum(issuePriority), nullable=False, default=issuePriority.medium
    ),
    Column("status", Enum(issueStatus), nullable=False, default=issueStatus.open),
)
