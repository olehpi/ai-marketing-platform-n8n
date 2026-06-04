# AI Marketing Platform (n8n Workflow)
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
