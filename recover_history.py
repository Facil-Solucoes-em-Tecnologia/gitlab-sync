import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv
from src.data.gitlab_repository import GitLabRepository
from src.data.database_repository import DatabaseRepository
from src.services.sync_service import SyncService

def main():
    # Carrega variáveis do arquivo .env
    load_dotenv()

    GITLAB_URL = os.getenv('GITLAB_URL')
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
    PROJECT_ID = int(os.getenv('PROJECT_ID', 0))
    DB_NAME = os.getenv('POSTGRES_DB')
    DB_USER = os.getenv('POSTGRES_USER')
    DB_PASS = os.getenv('POSTGRES_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'db')

    if not GITLAB_URL or not GITLAB_TOKEN or not PROJECT_ID:
        print("Faltam variáveis de ambiente (GITLAB_URL, GITLAB_TOKEN, PROJECT_ID).")
        sys.exit(1)

    gitlab_repo = GitLabRepository(GITLAB_URL, GITLAB_TOKEN, PROJECT_ID)
    db_repo = DatabaseRepository(DB_HOST, DB_NAME, DB_USER, DB_PASS)
    sync_service = SyncService(gitlab_repo, db_repo)

    # Inicia a partir de 01 de março conforme solicitado
    start_date = date(2026, 3, 1)
    end_date = date.today()

    current_date = start_date
    while current_date <= end_date:
        print(f"\n=== FORÇANDO REFRESH: {current_date} ===")
        print(f"Limpando dados antigos e recarregando do GitLab...")
        try:
            # O método run_daily_sync agora já faz o delete preventivo dos commits
            # garantindo que apenas a carga atual do GitLab permaneça no banco.
            sync_service.run_daily_sync(current_date)
        except Exception as e:
            print(f"Erro ao processar {current_date}: {e}")
        current_date += timedelta(days=1)

    print("\nRecuperação de histórico concluída.")

if __name__ == "__main__":
    main()