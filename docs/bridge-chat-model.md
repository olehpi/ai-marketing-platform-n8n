# Bridge Chat Model

`n8n-nodes-bridge-chat` is a custom n8n AI-language-model node. It adapts messages from an n8n AI Agent to the HTTP API provided by the `telegram_bridge` service and returns its response as an AI message.

## Architecture

```text
n8n AI Agent
      |
      | LangChain messages
      v
Bridge Chat Model custom node
      |
      | POST /chat
      v
telegram_bridge (Docker service)
      |
      v
Telegram target bot
```

Both `n8n` and `telegram_bridge` run in the same Docker Compose network. The node uses the Compose service name, not a host address:

```text
http://telegram_bridge:8000/chat
```

## Docker build

The custom node is bundled into the n8n image by `custom-nodes/n8n-nodes-bridge-chat/Dockerfile`.

1. The builder stage installs the node dependencies and compiles TypeScript into `dist/`.
2. The final stage starts with `docker.n8n.io/n8nio/n8n:2.21.7` and copies the built package to `/home/node/custom/n8n-nodes-bridge-chat`.
3. `N8N_CUSTOM_EXTENSIONS=/home/node/custom` makes n8n load the package at startup.

The `n8n` service in `docker-compose.yml` uses this Dockerfile as its build context. Source files are deliberately not bind-mounted into the container, so the running node always matches the image.

Rebuild n8n after changing the node source or dependencies:

```powershell
docker compose up -d --build n8n
```

To rebuild the entire stack, including the bridge service:

```powershell
docker compose up -d --build
```

## n8n configuration

1. Start `telegram_bridge` and n8n with Docker Compose.
2. In an n8n workflow, add **Bridge Chat Model** as the language model for an AI Agent.
3. Leave **Bridge URL** set to `http://telegram_bridge:8000/chat`, or set it to another compatible HTTP endpoint.

The node sends this request shape:

```json
{
  "messages": [
    { "role": "system", "content": "You are helpful." },
    { "role": "human", "content": "Hello" }
  ],
  "tools": []
}
```

The endpoint must return either `{"content":"..."}` or `{"answer":"..."}`. For tool calls, it may return `tool_calls` with `id`, `name`, and `args` (or `arguments`).

## Troubleshooting

| Symptom | Resolution |
| --- | --- |
| Node is absent from n8n | Rebuild and restart with `docker compose up -d --build n8n`, then inspect `docker compose logs n8n`. |
| Connection refused or DNS error | Confirm `telegram_bridge` is running with `docker compose ps`; use `http://telegram_bridge:8000/chat` from n8n, not `localhost`. |
| Request times out | The node timeout is 120 seconds. Check `docker compose logs telegram_bridge` and the Telegram bot response time. |
| Telegram authorization error | Follow the session-authorization steps in [Telegram Bridge](telegram-bridge.md). |

## Related files

- `custom-nodes/n8n-nodes-bridge-chat/nodes/ BridgeChatModel/BridgeChatModel.node.ts` — node implementation.
- `custom-nodes/n8n-nodes-bridge-chat/package.json` — node metadata and dependencies.
- `custom-nodes/n8n-nodes-bridge-chat/Dockerfile` — custom n8n image build.
- `telegram_bridge/app.py` — `/chat` API implementation.
