import psycopg2
from src.domain.models import IssueSnapshot, GitMetric

class DatabaseRepository:
    def __init__(self, host, dbname, user, password):
        self.conn_params = {
            'host': host,
            'database': dbname,
            'user': user,
            'password': password
        }

    def _get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def init_tables(self):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS fact_issue_daily (
                        id SERIAL PRIMARY KEY,
                        snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
                        issue_id INTEGER NOT NULL,
                        issue_iid INTEGER NOT NULL,
                        project_id INTEGER NOT NULL,
                        title TEXT,
                        state TEXT,
                        assignee_username TEXT,
                        assignee_name TEXT,
                        workload_status TEXT,
                        sprint_name TEXT,
                        task_type TEXT,
                        points INTEGER DEFAULT 0,
                        milestone_title TEXT,
                        updated_at_gitlab TIMESTAMP,
                        is_epic BOOLEAN DEFAULT FALSE,
                        UNIQUE (snapshot_date, issue_id)
                    );
                    CREATE TABLE IF NOT EXISTS fact_git_daily (
                        id SERIAL PRIMARY KEY,
                        snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
                        developer_username TEXT NOT NULL,
                        commits_count INTEGER DEFAULT 0,
                        merges_count INTEGER DEFAULT 0,
                        UNIQUE (snapshot_date, developer_username)
                    );
                """)
                conn.commit()

    def upsert_issue(self, issue: IssueSnapshot):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO fact_issue_daily (
                        snapshot_date, issue_id, issue_iid, project_id, title, state, 
                        assignee_username, assignee_name, workload_status, sprint_name, 
                        task_type, points, milestone_title, updated_at_gitlab, is_epic
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (snapshot_date, issue_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        state = EXCLUDED.state,
                        assignee_username = EXCLUDED.assignee_username,
                        assignee_name = EXCLUDED.assignee_name,
                        workload_status = EXCLUDED.workload_status,
                        sprint_name = EXCLUDED.sprint_name,
                        task_type = EXCLUDED.task_type,
                        points = EXCLUDED.points,
                        milestone_title = EXCLUDED.milestone_title,
                        updated_at_gitlab = EXCLUDED.updated_at_gitlab,
                        is_epic = EXCLUDED.is_epic
                """, (
                    issue.snapshot_date, issue.issue_id, issue.issue_iid, issue.project_id, 
                    issue.title, issue.state, issue.assignee_username, issue.assignee_name, 
                    issue.workload_status, issue.sprint_name, issue.task_type, issue.points, 
                    issue.milestone_title, issue.updated_at_gitlab, issue.is_epic
                ))
                conn.commit()

    def upsert_git_metric(self, metric: GitMetric):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO fact_git_daily (
                        snapshot_date, developer_username, commits_count, merges_count
                    ) VALUES (%s, %s, %s, %s)
                    ON CONFLICT (snapshot_date, developer_username) DO UPDATE SET
                        commits_count = EXCLUDED.commits_count,
                        merges_count = EXCLUDED.merges_count
                """, (
                    metric.snapshot_date, metric.developer_username, 
                    metric.commits_count, metric.merges_count
                ))
                conn.commit()
