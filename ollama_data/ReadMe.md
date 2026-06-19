# ollama_data

Purpose
- Persistent storage for Ollama data when running locally or in a container (commonly mounted to `/root/.ollama`).
- Stores models, cached files, configuration, logs, sessions, and metadata.

Contents
- Downloaded models and weights
- Cache and temporary files
- Configuration files and logs
- Session data and metadata

Security and best practices
- This folder may contain large binaries and sensitive data. Do not commit sensitive files to public repositories.
- Keep API keys and credentials in environment variables or a secret manager, not inside this folder.
- Use a `.env` file or your orchestrator's secret management for external service credentials.

Docker Compose example
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ./ollama_data:/root/.ollama
    environment:
      - OLLAMA_API_KEY=\${OLLAMA_API_KEY}
      # other variables supplied via .env or secrets# postgres_data
      
      Purpose
      - Persistent directory for PostgreSQL database files used by services (e.g., n8n chat memory, application databases).
      - Typically mounted to the container path `/var/lib/postgresql/data`.
      - Can also contain initialization scripts (`/docker-entrypoint-initdb.d`), custom configuration, and backups.
      
      Contents
      - Database data files (base, WAL)
      - Optional init scripts (`initdb` folder)
      - Custom `postgresql.conf` / `pg_hba.conf`
      - Logical backups/dumps (`.sql`, `.dump`) if stored here
      
      Security and best practices
      - This folder contains sensitive data. Do not commit database files or dumps with credentials to public repos.
      - Keep DB credentials in environment variables or a secrets manager (e.g., `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).
      - Prefer storing dumps outside the live data folder; maintain encrypted backups.
      
      Docker Compose example
      ```yaml
      services:
        postgres:
          image: postgres:15
          restart: unless-stopped
          volumes:
            - ./postgres_data:/var/lib/postgresql/data
            - ./postgres_data/initdb:/docker-entrypoint-initdb.d  # optional init scripts
          environment:
            - POSTGRES_USER=${POSTGRES_USER}
            - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
            - POSTGRES_DB=${POSTGRES_DB}