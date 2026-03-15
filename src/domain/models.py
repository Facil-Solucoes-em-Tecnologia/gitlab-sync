from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

@dataclass
class IssueSnapshot:
    issue_id: int
    issue_iid: int
    project_id: int
    title: str
    state: str
    assignee_username: Optional[str]
    assignee_name: Optional[str]
    workload_status: Optional[str]
    sprint_name: Optional[str]
    task_type: Optional[str]
    points: int
    milestone_title: Optional[str]
    updated_at_gitlab: datetime
    is_epic: bool = False
    snapshot_date: date = date.today()

@dataclass
class GitMetric:
    developer_username: str
    commits_count: int = 0
    merges_count: int = 0
    snapshot_date: date = date.today()
