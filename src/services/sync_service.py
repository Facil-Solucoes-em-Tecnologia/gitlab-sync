from datetime import date
from src.data.gitlab_repository import GitLabRepository
from src.data.database_repository import DatabaseRepository

class SyncService:
    def __init__(self, gitlab_repo: GitLabRepository, db_repo: DatabaseRepository):
        self.gitlab_repo = gitlab_repo
        self.db_repo = db_repo

    def run_daily_sync(self):
        print("Iniciando sincronização diária...")
        self.db_repo.init_tables()
        
        today = date.today()

        # 1. Sincronizar Issues
        print(f"Extraindo issues do GitLab para {today}...")
        issues = self.gitlab_repo.get_issues(today)
        for issue in issues:
            self.db_repo.upsert_issue(issue)
        print(f"{len(issues)} issues processadas.")

        # 2. Sincronizar Métricas de Git
        print(f"Extraindo métricas de Git para {today}...")
        metrics = self.gitlab_repo.get_git_metrics(today)
        for metric in metrics:
            self.db_repo.upsert_git_metric(metric)
        print(f"{len(metrics)} desenvolvedores com métricas processadas.")

        print("Sincronização concluída com sucesso!")
