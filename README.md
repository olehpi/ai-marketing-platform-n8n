# AI Marketing Platform (`workflow/AI-assistent.json`)
This project is an **AI-powered marketing automation platform** built with **n8n**, **LangChain AI Agent**, **Ollama LLM**, and **Tavily Internet Search**.

---
## 🚀 Key Capabilities
- 💬 AI Telegram assistant for users and leads
- 🎤 Voice message processing (speech-to-text)
- 🧠 AI responses via local LLM (Ollama)
- 🌐 Real-time web search (Tavily API)
- 💾 Per-user memory stored in PostgreSQL (conversation context)
- 📣 Admin notifications for all incoming leads/messages
---

## ✨ Features
### 💬 Telegram AI Chatbot (Lead Interface)
Users can interact with the platform via Telegram.
It can be used as:
- Lead qualification bot
- Customer support assistant
- Marketing assistant

---

### 🎤 Voice Message Support
Voice messages are processed through pipeline:

1. Download from Telegram
2. Convert speech → text (Whisper / OpenAI transcription)
3. Send to AI agent for processing

---

### 🧠 AI Agent (LangChain + Ollama)
Core intelligence layer:
- Model: **qwen3.5:9b (Ollama)**
- Routes user requests to tools
- Executes web search when needed
- Uses system prompt optimized for assistant behavior

# Facebook Comments Auto\-Reply (`workflow/Facebook-comments-auto-reply.json`)

Purpose
- Automatically monitor and reply to comments on Facebook posts to qualify leads, provide quick answers and route complex requests to the AI agent.
- Log interactions to PostgreSQL and notify admins for follow\-up.

How it works
1. Facebook sends a webhook on new comment.
2. n8n workflow receives and validates the webhook.
3. Filters and rules determine if auto\-reply should run (contains keywords, post ID, author rules).
4. Comment text is sent to the AI agent (LangChain + Ollama) and optionally to Tavily search for up\-to\-date info.
5. Generated reply is posted via Facebook Graph API.
6. Interaction is stored in `n8n_chat_memory` (Postgres) and an admin notification is sent.

Requirements
- Facebook Page access token and app webhook subscription.
- n8n configured to accept external webhooks (valid `WEBHOOK_URL` / ngrok).
- Environment variables: `FACEBOOK_PAGE_TOKEN`, `FACEBOOK_APP_SECRET`, plus existing `POSTGRES_*`, `OLLAMA_*`, `TAVILY_*`.
- Import `workflow/Facebook-comments-auto-reply.json` into n8n and connect Facebook credential.

Configuration & Usage
- Import the workflow into n8n.
- Create and link a Facebook credential using `FACEBOOK_PAGE_TOKEN`.
- Set webhook endpoint in Facebook App to the n8n webhook URL used by the workflow.
- Test by leaving comments on a subscribed page post; watch `logs/` for workflow events.

Security and best practices
- Do not commit access tokens to the repository.
- Mask or filter personal data in logs.
- Respect Facebook rate limits and comment moderation policies.
- Keep an audit trail in Postgres and rotate credentials periodically.
---

### 🌐 Web Search Tool
Integrated via **Tavily API**:
- Fetches real-time information from the internet
- Helps AI answer up-to-date questions
- Used as a tool by AI agent

---
### 💾 Memory System (PostgreSQL)
Uses persistent **PostgreSQL** storage:

- Stores conversation history per Telegram user in `n8n_chat_memory` database
- Enables contextual responses across sessions
- Improves personalization with durable context
- Database credentials managed via environment variables (`.env`)

---

### 📣 Admin Notification System
Every incoming message is automatically forwarded to admin chats:
- User details
- Message content
- AI response
- Telegram username link

---

## 🛠️ Setup & Deployment

### Prerequisites
- Docker & Docker Compose
- PostgreSQL 16
- n8n

### Environment Configuration
Create a `.env` file based on `.env.example`:

```env
POSTGRES_USER=n8n
POSTGRES_PASSWORD=your_strong_password
POSTGRES_DB=n8n_chat_memory

N8N_HOST=your-domain
N8N_PROTOCOL=https
WEBHOOK_URL=https://your-domain/
```

### Local Startup
Use the interactive PowerShell scripts from the repository root:

1. Open PowerShell in this folder.
2. Run `.\start.ps1`.
3. Confirm the prompts for Docker, ngrok, Ollama, Whisper, and n8n startup.
4. Wait for the n8n health check to return `200 OK`.
5. Open the displayed n8n URL, or use `http://localhost:5678` if ngrok is not available.
6. Run `.\status.ps1` anytime to check Docker, Ollama, and ngrok status.

Useful commands:

- `.\status.ps1` shows Docker, Ollama, and ngrok status.
- `.\stop.ps1` stops Whisper, n8n, Postgres, ngrok, and Ollama.
- Logs are written to the `logs/` directory.
