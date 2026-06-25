from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Enum
from app.schemas import issuePriority, issueStatus

engine = create_engine("sqlite:///mydatabase.db", echo=True)
meta = MetaData()
issues = Table(
    "issues",
    meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String(100), nullable=False),
    Column("description", String(1000), nullable=False),
    Column(
        "priority", Enum(issuePriority), nullable=False, default=issuePriority.medium
    ),
    Column("status", Enum(issueStatus), nullable=False, default=issueStatus.open),
)
meta.create_all(engine)
