# logs

Purpose
- Central folder for storing service and utility logs for the project (n8n, Ollama, Whisper, Postgres, scripts, containers).
- Used for debugging, auditing and retaining runtime history during local development and container deployments.

Contents
- Active log files (for example: `n8n.log`, `ollama.log`, `whisper.log`, `postgres.log`).
- Rotated and archived logs (e.g. `*.log.1`, `*.log.gz`).
- Diagnostic dumps and trace files.

Security and best practices
- Do not commit real logs to public repositories. Use `.gitignore`.
- Avoid storing secrets in logs. Mask or filter sensitive fields at the application level.
- Restrict filesystem access to the folder and encrypt if required on shared hosts.

`.gitignore` suggestion