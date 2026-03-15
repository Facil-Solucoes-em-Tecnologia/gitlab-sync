# GitLab Snapshot Sync Worker

Este projeto é um worker automatizado para extração de dados do GitLab e armazenamento em um banco de dados PostgreSQL para análise de métricas no Grafana. Ele captura snapshots diários de issues, milestones, épicos e métricas de atividade de desenvolvedores.

## 🚀 Objetivo

- Extrair informações detalhadas de Issues e Git Metrics.
- Organizar dados por Sprints, Pontuação (Fibonacci), Status de Workload e Tipo de Tarefa.
- Permitir o acompanhamento histórico de produtividade e progresso de Épicos.
- Oferecer uma base de dados estruturada para dashboards no Grafana.

## 🏗️ Arquitetura

O projeto utiliza uma arquitetura de camadas para facilitar a manutenção e escalabilidade:

- **`src/domain`**: Modelos de dados e entidades de negócio (`dataclasses`).
- **`src/data`**: Repositórios para interação com APIs externas (GitLab) e persistência (PostgreSQL).
- **`src/services`**: Lógica de sincronização e orquestração entre repositórios.
- **`main.py`**: Ponto de entrada, configuração de agendamento e execução.

## 🛠️ Tecnologias

- **Python 3.11**
- **PostgreSQL**
- **Docker & Docker Compose**
- **python-gitlab** (API Integration)
- **psycopg2** (Database driver)
- **schedule** (Job scheduling)
- **GitHub Actions** (CI/CD)

## 📋 Convenções de Labels (GitLab)

Para que a extração funcione corretamente, utilize o sistema de **Scoped Labels** no GitLab:

- `workload::{{status}}`: Ex: `workload::backlog`, `workload::em andamento`, `workload::done`.
- `sprint::{{nome}}`: Ex: `sprint::2024-Q1-S1`. (Caso ausente, utiliza o Milestone vinculado).
- `points::{{valor}}`: Pontuação Fibonacci. Ex: `points::3`, `points::5`.
- `type::{{categoria}}`: Ex: `type::feature`, `type::bugfix`, `type::hotfix`.
- `epico`: Marcador para identificar issues que representam Épicos.

## ⚙️ Configuração

1.  Crie um arquivo `.env` baseado no `.env.example`:
    ```bash
    cp .env.example .env
    ```
2.  Preencha as variáveis de ambiente:
    - `GITLAB_URL`: URL do seu GitLab (ex: https://gitlab.com).
    - `GITLAB_TOKEN`: Token de acesso privado com permissão de leitura.
    - `PROJECT_ID`: ID numérico do projeto no GitLab.
    - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Credenciais do banco.
    - `DB_HOST`: Host do banco (use `db` se estiver usando Docker Compose).
    - `SYNC_TIME`: Horário da execução diária (formato HH:MM, padrão `23:59`).

## 🐳 Como Executar com Docker

Certifique-se de ter o Docker e Docker Compose instalados.

1.  **Subir o ambiente completo:**
    ```bash
    docker-compose up -d
    ```
    Isso iniciará o banco de dados e o worker em segundo plano.

2.  **Verificar Logs:**
    ```bash
    docker-compose logs -f worker
    ```

## 📊 Estrutura do Banco de Dados

O worker cria automaticamente duas tabelas principais:

- `fact_issue_daily`: Armazena o estado de cada issue no momento do snapshot.
- `fact_git_daily`: Armazena o volume de commits e merges por desenvolvedor no dia.

## 🚀 CI/CD

O projeto conta com um workflow do **GitHub Actions** (`.github/workflows/docker-publish.yml`) que:
- Dispara automaticamente em pushes para a branch `main`.
- Realiza o build da imagem Docker.
- Publica a imagem no **GitHub Container Registry (GHCR)**.

## 📝 Notas Adicionais

- O script é **idempotente**: você pode executá-lo múltiplas vezes no mesmo dia e ele apenas atualizará os registros existentes para aquela data (usando `ON CONFLICT`).
- O agendamento é feito nativamente no Python, garantindo que o container permaneça ativo e execute no horário configurado.
