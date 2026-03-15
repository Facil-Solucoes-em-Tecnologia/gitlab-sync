import os
import time
import schedule
from src.data.gitlab_repository import GitLabRepository
from src.data.database_repository import DatabaseRepository
from src.services.sync_service import SyncService

# Configurações via variáveis de ambiente
GITLAB_URL = os.getenv('GITLAB_URL')
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')
PROJECT_ID = int(os.getenv('PROJECT_ID', 0))
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'db')
SYNC_TIME = os.getenv('SYNC_TIME', '23:59') # Horário da execução diária

def job():
    # Inicializar Repositórios
    gitlab_repo = GitLabRepository(GITLAB_URL, GITLAB_TOKEN, PROJECT_ID)
    db_repo = DatabaseRepository(DB_HOST, DB_NAME, DB_USER, DB_PASS)

    # Inicializar e Executar Serviço
    sync_service = SyncService(gitlab_repo, db_repo)
    
    try:
        sync_service.run_daily_sync()
    except Exception as e:
        print(f"Erro durante a sincronização: {e}")

def main():
    print(f"Agendando tarefa diária para as {SYNC_TIME}")
    schedule.every().day.at(SYNC_TIME).do(job)

    # Executar uma vez no início (opcional, para testar)
    # job()

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()