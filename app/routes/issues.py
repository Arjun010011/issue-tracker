from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import CreateIssue, IssueOut, IssueStatus, UpdateIssue
from sqlalchemy.orm import Session
from sqlalchemy import select, update, insert, delete
from app.models import issues
from app.dependencies import get_current_user, get_db

router = APIRouter(
    prefix="/api/v1/issues",
    tags=["issues"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[IssueOut])
async def get_issues(session: Session = Depends(get_db)):
    """retrieve all issues"""
    result = session.execute(select(issues)).mappings().all()
    return result


@router.post("/", response_model=IssueOut, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue: CreateIssue,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    new_issues = {
        "title": issue.title,
        "description": issue.description,
        "priority": issue.priority,
        "status": IssueStatus.open,
        "user_id": user_id,
    }
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
async def get_issue(issue_id: int, session: Session = Depends(get_db)):
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
async def update_issue(
    issue_id: int,
    payload: UpdateIssue,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    update_data = payload.model_dump(exclude_unset=True)
    existing_issue = (
        session.execute(select(issues).where(issues.c.id == issue_id))
        .mappings()
        .first()
    )
    if not existing_issue:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="issue not found")
    if existing_issue["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not allowed to update this issue",
        )
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
async def del_issue(
    issue_id: int,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    existing_issue = (
        session.execute(select(issues).where(issues.c.id == issue_id))
        .mappings()
        .first()
    )
    if not existing_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="issue not found"
        )
    if existing_issue["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you are not allowed to delete this issue",
        )
    session.execute(delete(issues).where(issues.c.id == issue_id))
    session.commit()
    return
