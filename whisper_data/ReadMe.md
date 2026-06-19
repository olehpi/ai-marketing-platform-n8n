# whisper_data

Purpose
- Persistent storage for Whisper-related files when running locally or in a container (commonly mounted to `~/.whisper` or `/root/.whisper`).
- Stores model weights, cached audio/preprocessed data, transcriptions and related configuration.

Contents
- Downloaded Whisper model files and weights
- Cached audio, feature files and temporary preprocessing artifacts
- Transcription outputs (`.txt`, `.json`, `.srt`, etc.)
- Configuration files and logs
- Optional custom language packs or decoder artifacts

Security and best practices
- This folder may contain sensitive audio and transcripts. Do not commit audio or transcript files to public repositories.
- Keep API keys and service credentials in environment variables or a secrets manager, not in files inside this folder.
- Consider encrypting stored transcripts or restricting access on shared hosts.

Docker Compose example
```yaml
services:
  whisper:
    image: yourorg/whisper:latest
    volumes:
      - ./whisper_data:/root/.whisper
    environment:
      - WHISPER_MODEL=\${WHISPER_MODEL}
      - OAUTH_TOKEN=\${OAUTH_TOKEN}  # store tokens in .env or secret store