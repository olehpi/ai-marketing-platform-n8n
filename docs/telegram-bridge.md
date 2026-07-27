# Telegram Bridge

`telegram_bridge` is a FastAPI service for communicating with a Telegram bot through an authorized Telegram user account. It uses [Telethon](https://docs.telethon.dev/) and is included in the main Docker Compose stack as the `telegram_bridge` service.

## Purpose

The bridge accepts text from another platform component, sends it to the bot specified in its configuration, waits for new incoming bot messages, and returns one selected response. This is useful when a workflow needs to interact with a bot as a user account rather than through the Bot API.

## Architecture

```text
Client or workflow
        |
        | POST /send
        v
Telegram Bridge (FastAPI, port 8000)
        |
        | Telethon user session
        v
Target Telegram bot
        |
        | incoming messages
        v
Telegram Bridge -> JSON answer
```

Docker Compose builds the service from `telegram_bridge/Dockerfile`, publishes port `8000`, loads variables from `telegram_bridge/.env`, and mounts `telegram_bridge/sessions/` at `/app/sessions` to preserve the authorization session between container restarts.

## Configuration

1. Copy `telegram_bridge/.env.example` to `telegram_bridge/.env`.
2. Fill in the following variables:

| Variable | Description |
| --- | --- |
| `API_ID` | Numeric Telegram API ID from [my.telegram.org](https://my.telegram.org). |
| `API_HASH` | Telegram API hash paired with `API_ID`. |
| `PHONE` | Phone number of the Telegram user account in international format, for example `+11222222222`. |
| `TARGET_BOT` | Username or identifier of the bot that receives messages from the bridge. |

Keep `telegram_bridge/.env` private. It contains credentials for a Telegram user account.

## First authorization

Before starting the bridge container, create an authorized Telethon session on the host:

```powershell
cd telegram_bridge
python -m pip install -r requirements.txt
python login.py
```

Telegram will request the login code and, if enabled, the two-factor-authentication password. A successful login creates `telegram_bridge/sessions/telegram_session.session`.

The session directory is mounted by Docker Compose, so the container can reuse it. If the session is revoked or expires, stop the service, repeat the authorization command, and start the service again.

## Start and health check

From the repository root, start the complete stack:

```powershell
# stop container if already running
docker compose down telegram_bridge
# run all containers
docker compose up -d  
# or run single container telegram_bridge with build: 
docker compose up -d --build telegram_bridge
# or stop and run single container telegram_bridge with build using one command: 
docker compose up -d --build --force-recreate telegram_bridge
```

Check the status of container:

```powershell
docker compose ps
```

Check the bridge logs to confirm the session is authorized and Telegram is connected:
```powershell
docker compose logs telegram_bridge
```
or 
```powershell
docker compose logs -f telegram_bridge
```

Check the code in file /app/app.py from 55 to 75p:
```powershell
docker compose exec telegram_bridge sed -n "55,75p" /app/app.py
```

The bridge is available at `http://localhost:8000`. FastAPI's interactive API documentation is available at `http://localhost:8000/docs`.

## API

### `POST /chat`

Sends `text` to `TARGET_BOT` and returns the selected incoming reply.

Request body:

```cmd
curl -X POST http://localhost:8000/chat ^ 
-H "Content-Type: application/json" ^ 
-d "{\"messages\":[{\"role\":\"user\",\"content\":\"/chatgpt\"}],\"bot_name\":\"your_chat_bot\"}"
```
```cmd
curl -X POST http://localhost:8000/chat ^
-H "Content-Type: application/json" ^
-d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hello!!!\"}],\"bot_name\":\"your_chat_bot\",\"tools\":[{\"name\":\"PricesTool\",\"description\":\"Provides current service prices from the pricing database\"}]}"

curl -X POST http://localhost:8000/chat ^
-H "Content-Type: application/json" ^
-d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hello!!!!!\"}],\"bot_name\":\"your_chat_bot\",\"tools\":[{\"name\":\"PricesTool\",\"description\":\"Provides current service prices from the pricing database\"},{\"name\":\"Internet_search\",\"description\":\"Search current external information\"}]}"
```
chatgpt3

Successful response:

```json
{
  "content": "Hello! It's great to hear from you. What would you like to talk about today?"
}
```

## Response-selection behavior

For each request, the bridge records the ID of the latest existing message in the chat with `TARGET_BOT`, sends the supplied text, then polls the latest messages for up to 60 seconds.

- Only incoming, non-empty text messages newer than the recorded message ID are considered.
- Duplicate message texts are ignored.
- Polling stops early after two distinct incoming messages are found.
- When two or more messages are found, the second collected message is returned.
- When exactly one message is found, that message is returned.
- When no qualifying message arrives within the timeout, the response is `{"content":"No answer"}`.

The bot should therefore return text messages and respond within one minute. If it sends multiple messages, its second distinct message is treated as the final answer.

## Security and operations

- Never commit `telegram_bridge/.env` or files under `telegram_bridge/sessions/`; both are ignored by `.gitignore`.
- Treat the session file as sensitive: anyone who obtains it may be able to use the authorized Telegram account.
- Restrict access to port `8000`; the current service has no application-level authentication.
- Use a dedicated Telegram account where possible and monitor service logs for authorization failures.
- Rotate or revoke the Telegram session immediately if credentials or the session file are exposed.

## Troubleshooting

| Symptom | Likely cause and action |
| --- | --- |
| Container exits on startup with `Telegram session not authorized` | Run `python login.py` on the host, complete Telegram authentication, and restart the container. |
| `No answer` is returned | Verify `TARGET_BOT`, confirm the bot accepts messages from the account, and check whether it replies with text within 60 seconds. |
| Connection or authentication errors | Verify `API_ID`, `API_HASH`, and `PHONE` in `telegram_bridge/.env`; recreate the session if it was revoked. |
| API is unreachable | Run `docker compose ps`, inspect `docker compose logs telegram_bridge`, and ensure port `8000` is not occupied. |
