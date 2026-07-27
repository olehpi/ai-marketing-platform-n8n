import os
import asyncio
import re

from fastapi import FastAPI
from pydantic import BaseModel
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
PHONE = os.environ["PHONE"]
DEFAULT_TARGET_BOT = os.getenv("TARGET_BOT")
RESPONSE_IDLE_TIMEOUT_SECONDS = int(os.getenv("RESPONSE_IDLE_TIMEOUT_SECONDS", "15"))

app = FastAPI()
client = TelegramClient("sessions/telegram_session", API_ID, API_HASH)


class Message(BaseModel):
    text: str
    bot_name: str | None = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ToolSchema(BaseModel):
    name: str
    description: str | None = None
    parameters: dict | None = None


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    tools: list[ToolSchema] = []
    bot_name: str | None = None


async def init_telegram():
    await client.connect()
    if not await client.is_user_authorized():
        raise Exception("Telegram session not authorized")
    print("Telegram connected")


@app.on_event("startup")
async def startup():
    await init_telegram()


def build_prompt_with_tools(user_message: str, tools: list[ToolSchema]) -> str:
    holder = "$$$tools_block$$$"
    if not tools:
        return user_message.replace(holder, "")

    tools_text = []
    for t in tools:
        desc = t.description or "No description"
        tools_text.append(f"- {t.name}: {desc}")

    tools_block = "\n".join(tools_text)
    return user_message.replace(holder, tools_block)


def parse_tool_call(text: str) -> dict | None:
    """We look for the command to call the tool in the bot's response"""
    match = re.search(r"TOOL_CALL:\s*(\w+)", text, re.IGNORECASE)
    if match:
        tool_name = match.group(1).strip()
        return {
            "id": f"call_{tool_name}_{int(asyncio.get_event_loop().time())}",
            "name": tool_name,
            "arguments": {}
        }
    return None


@app.post("/chat")
async def chat(req: ChatRequest):
    target_bot = req.bot_name or DEFAULT_TARGET_BOT
    if not target_bot:
        raise Exception("No Telegram bot configured")
    user_message = req.messages[-1].content
    print("AI REQUEST:", user_message)
    print("TARGET BOT:", target_bot)
    print("TOOLS:", [t.name for t in req.tools])

    # Forming a prompt with tools
    prompt = build_prompt_with_tools(user_message, req.tools)
    print("PROMPT TO BOT:", prompt[:3000], "...")

    last = await client.get_messages(target_bot, limit=1)
    last_id = last[0].id if last else 0

    # Sending a prompt to the bot
    await client.send_message(target_bot, prompt)

    responses = []
    last_response_at = None

    for _ in range(120):
        await asyncio.sleep(1)
        async for message in client.iter_messages(target_bot, limit=10):
            if message.id <= last_id:
                continue
            if message.out:
                continue
            if not message.text:
                continue
            if message.text not in responses:
                responses.append(message.text)
                last_response_at = asyncio.get_running_loop().time()

        if (last_response_at is not None
                and asyncio.get_running_loop().time() - last_response_at
                >= RESPONSE_IDLE_TIMEOUT_SECONDS):
            break

    print("MESSAGES:", responses)

    if not responses:
        return {"content": "No answer"}

    answer = responses[-1]

    # Checking if the bot wants to call the tool
    tool_call = parse_tool_call(answer)
    if tool_call:
        print("DETECTED TOOL CALL:", tool_call)
        return {
            "content": "",
            "tool_calls": [tool_call]
        }

    # The usual answer
    return {"content": answer}