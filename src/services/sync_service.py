from datetime import date
from src.data.gitlab_repository import GitLabRepository
from src.data.database_repository import DatabaseRepository

class SyncService:
    def __init__(self, gitlab_repo: GitLabRepository, db_repo: DatabaseRepository):
        self.gitlab_repo = gitlab_repo
        self.db_repo = db_repo

    def run_daily_sync(self, sync_date: date = None):
        print(f"Iniciando sincronização para a data {sync_date or date.today()}...")
        self.db_repo.init_tables()
        
        target_date = sync_date or date.today()

        # 1. Sincronizar Issues
        print(f"Extraindo issues do GitLab para {target_date}...")
        issues = self.gitlab_repo.get_issues(target_date)
        for issue in issues:
            self.db_repo.upsert_issue(issue)
        print(f"{len(issues)} issues processadas.")

        # 2. Sincronizar Métricas de Git
        print(f"Extraindo métricas de Git para {target_date}...")
        metrics = self.gitlab_repo.get_git_metrics(target_date)
        for metric in metrics:
            self.db_repo.upsert_git_metric(metric)
        print(f"{len(metrics)} desenvolvedores com métricas processadas.")

        print("Sincronização concluída com sucesso!")
