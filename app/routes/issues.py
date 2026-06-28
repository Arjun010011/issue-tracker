from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import CreateIssue, IssueOut, IssueStatus, UpdateIssue
from sqlalchemy.orm import Session
from sqlalchemy import select, update, insert, delete
from app.database import engine
from app.models import issues
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/issues",
    tags=["issues"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[IssueOut])
async def get_issues():
    """retrieve all issues"""
    with Session(engine) as session:
        result = session.execute(select(issues)).mappings().all()
        return result


@router.post("/", response_model=IssueOut, status_code=status.HTTP_201_CREATED)
async def create_issue(issue: CreateIssue,user_id:int = Depends(get_current_user)):
    new_issues = {
        "title": issue.title,
        "description": issue.description,
        "priority": issue.priority,
        "status": IssueStatus.open,
        "user_id":user_id
    }

    with Session(engine) as session:
        existing_issue = (
            session.execute(select(issues).where(issues.c.title == issue.title))
            .mappings()
            .first()
        )

        if existing_issue:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="an issue with the same title already exists",
            )

        result = session.execute(insert(issues).values(**new_issues).returning(issues))
        created_issue = result.mappings().first()
        session.commit()
        return created_issue


@router.get("/{issue_id}", response_model=IssueOut)
async def get_issue(issue_id: int):
    with Session(engine) as session:
        result = (
            session.execute(select(issues).where(issues.c.id == issue_id))
            .mappings()
            .first()
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="issue not found"
            )
        return result


@router.put("/{issue_id}", response_model=IssueOut, status_code=status.HTTP_200_OK)
async def update_issue(issue_id: int, payload: UpdateIssue):
    update_data = payload.model_dump(exclude_unset=True)
    with Session(engine) as session:
        existing_issue = (
            session.execute(select(issues).where(issues.c.id == issue_id))
            .mappings()
            .first()
        )
        if not existing_issue:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="issue not found")
        session.execute(
            update(issues).where(issues.c.id == issue_id).values(**update_data)
        )
        session.commit()
        updated_issues = (
            session.execute(select(issues).where(issues.c.id == issue_id))
            .mappings()
            .first()
        )
        return updated_issues


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_issue(issue_id: int):
    with Session(engine) as session:
        existing_issue = (
            session.execute(select(issues).where(issues.c.id == issue_id))
            .mappings()
            .first()
        )
        if not existing_issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="issue not found"
            )
        session.execute(delete(issues).where(issues.c.id == issue_id))
        session.commit()
        return
