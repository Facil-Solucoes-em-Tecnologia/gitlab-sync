import gitlab
from datetime import datetime, date
from typing import List, Dict
from src.domain.models import IssueSnapshot, GitMetric

class GitLabRepository:
    def __init__(self, url: str, token: str, project_id: int):
        self.gl = gitlab.Gitlab(url, private_token=token)
        self.project = self.gl.projects.get(project_id)

    def _get_label_name(self, label) -> str:
        if isinstance(label, dict):
            return label.get('name', '')
        return str(label)

    def _get_label_value(self, labels: List, prefix: str) -> str:
        for label in labels:
            label_name = self._get_label_name(label)
            if label_name.startswith(prefix):
                # Tenta primeiro com '::' (padrão recomendado)
                if '::' in label_name:
                    parts = label_name.split('::', 1)
                    return parts[1].strip() if len(parts) > 1 else None
                
                # Fallback: se não tiver '::' mas começar com o prefixo, 
                # pode estar usando ':' ou apenas o prefixo com um espaço.
                # Remove o prefixo e retorna o resto.
                # Se o prefixo for 'workload::' e a label for 'workload:val', 
                # o startswith falharia. Vamos melhorar o prefixo.
                pass

        # Nova lógica mais robusta: procurar o prefixo base sem os separadores
        base_prefix = prefix.rstrip(':').rstrip()
        for label in labels:
            label_name = self._get_label_name(label)
            if label_name.startswith(base_prefix):
                # Tenta encontrar o separador após o prefixo base
                # Pode ser '::', ':', ' ' ou o próprio label se for apenas o prefixo
                rest = label_name[len(base_prefix):]
                if rest.startswith('::'):
                    return rest[2:].strip()
                if rest.startswith(':'):
                    return rest[1:].strip()
                if rest.startswith(' '):
                    return rest[1:].strip()
                # Se não houver separador conhecido, retorna o resto se não for vazio
                return rest.strip() if rest else None
        return None

    def get_issues(self, snapshot_date: date) -> List[IssueSnapshot]:
        issues = self.project.issues.list(all=True)
        snapshots = []
        for issue in issues:
            label_names = [self._get_label_name(l) for l in issue.labels]
            
            points_str = self._get_label_value(issue.labels, 'points::')
            points = 0
            try:
                if points_str:
                    points = int(points_str)
            except ValueError:
                pass

            sprint = self._get_label_value(issue.labels, 'sprint::')
            if not sprint and issue.milestone:
                sprint = issue.milestone['title']

            assignee_username = None
            assignee_name = None
            if issue.assignees:
                assignee_username = issue.assignees[0]['username']
                assignee_name = issue.assignees[0]['name']

            workflow_status = self._get_label_value(issue.labels, 'workflow::')
            if not workflow_status:
                if 'done' in label_names or 'closed' in label_names or 'close' in label_names:
                    workflow_status = 'done'
                elif 'open' in label_names:
                    workflow_status = 'open'

            snapshots.append(IssueSnapshot(
                issue_id=issue.id,
                issue_iid=issue.iid,
                project_id=issue.project_id,
                title=issue.title,
                state=issue.state,
                assignee_username=assignee_username,
                assignee_name=assignee_name,
                workflow_status=workflow_status,
                sprint_name=sprint,
                task_type=self._get_label_value(issue.labels, 'type::'),
                points=points,
                milestone_title=issue.milestone['title'] if issue.milestone else None,
                updated_at_gitlab=issue.updated_at,
                is_epic='epico' in label_names or 'epic' in label_names,
                snapshot_date=snapshot_date
            ))
        return snapshots

    def get_git_metrics(self, snapshot_date: date) -> List[GitMetric]:
        # Formato ISO 8601 (YYYY-MM-DDTHH:MM:SSZ) para garantir UTC
        since = datetime.combine(snapshot_date, datetime.min.time()).strftime('%Y-%m-%dT00:00:00Z')
        until = datetime.combine(snapshot_date, datetime.max.time()).strftime('%Y-%m-%dT23:59:59Z')
        
        print(f"DEBUG: Buscando commits entre {since} e {until}...")
        
        # O parâmetro 'all' no gitlab-python deve ser passado dentro de query_parameters 
        # ou como argumento se a versão suportar. 'get_all=True' ativa a paginação automática.
        commits = self.project.commits.list(since=since, until=until, get_all=True, query_parameters={'all': True})
        metrics_dict: Dict[str, GitMetric] = {}
        
        for commit in commits:
            # Garante que o commit pertence ao dia solicitado (filtro adicional de segurança)
            # O Gitlab pode retornar commits próximos se houver problemas de timezone
            commit_date = datetime.strptime(commit.created_at[:10], '%Y-%m-%d').date()
            if commit_date != snapshot_date:
                continue

            username = commit.author_email
            if username not in metrics_dict:
                metrics_dict[username] = GitMetric(developer_username=username, snapshot_date=snapshot_date)
            
            metrics_dict[username].commits_count += 1
            if len(commit.parent_ids) > 1:
                metrics_dict[username].merges_count += 1
        
        return list(metrics_dict.values())
