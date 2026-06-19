# n8n_data

Purpose
- Persistent folder for n8n container data mounted to the container (commonly `/home/node/.n8n`).
- Stores workflows, credentials, settings, session files, and local DB files (if SQLite is used).

Contents
- Workflows exported by n8n
- Credentials and secrets
- Configuration and session files
- Optional local SQLite DB (if Postgres is not used)
- Chat memory data (if a Postgres-backed chat memory is configured)

Security and best practices
- This folder contains secrets and credentials. Do not commit sensitive files to public repositories.
- Keep credentials and secrets in environment variables or a secure secret store, not directly in files inside this folder.
- Use a `.env` file or your orchestrator's secrets for database credentials (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB).

Docker Compose example
```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    volumes:
      - ./n8n_data:/home/node/.n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=\${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=\${N8N_BASIC_AUTH_PASSWORD}
      # Postgres connection for n8n and chat memory (set these in .env or your secret manager)
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=\${POSTGRES_DB}
      - DB_POSTGRESDB_USER=\${POSTGRES_USER}
      - DB_POSTGRESDB_PASSWORD=\${POSTGRES_PASSWORD}