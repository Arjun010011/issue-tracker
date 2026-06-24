from fastapi import APIRouter, HTTPException, status
import uuid
from app.schemas import createIssue, updateIssue, issueOut, issueStatus
from app.storage import load_data, write_data

router = APIRouter(prefix="/api/v1/routes", tags=["issues"])


@router.get("/", response_model=list[issueOut])
async def get_issues():
    """retrieve all issues"""
    issues = load_data()
    return issues


@router.post("/", response_model=issueOut, status_code=status.HTTP_201_CREATED)
async def create_issue(issue: createIssue):
    """create  new issue"""
    issues = load_data()
    new_issues = {
        "id": str(uuid.uuid4()),
        "title": issue.title,
        "description": issue.description,
        "priority": issue.priority,
        "status": issueStatus.open,
    }

    issues.append(new_issues)
    write_data(issues)
    return new_issues


@router.get("/{issue_id}", response_model=issueOut)
def get_issue(issue_id: str):
    issue_list = load_data()
    for issue in issue_list:
        if issue["id"] == issue_id:
            return issue
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="issue not found")


@router.put("/{issue_id}", response_model=issueOut, status_code=status.HTTP_201_CREATED)
async def update_issue(issue_id: str, payload: updateIssue):
    issue_list = load_data()
    update_data = payload.model_dump(exclude_unset=True)
    for issue in issue_list:
        if issue["id"] == issue_id:
            issue.update(update_data)
            write_data(issue_list)
            return issue

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="issue not found")


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_issue(issue_id: str):
    issue_list = load_data()
    for index, issue in enumerate(issue_list):
        if issue["id"] == issue_id:
            issue_list.pop(index)
            write_data(issue_list)
            return

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="issue not found")
