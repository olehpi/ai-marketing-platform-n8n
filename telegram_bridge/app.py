import os
import asyncio
import re

from fastapi import FastAPI
from pydantic import BaseModel
from telethon import TelegramClient
from dotenv import load_dotenv
from telethon.tl.types import User, Channel, Chat

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


class ChannelInfoRequest(BaseModel):
    channel_url: str


class SendMessageRequest(BaseModel):
    target: str
    text: str


class GroupRequest(BaseModel):
    group: str
    limit: int = 100


class GroupMessagesRequest(BaseModel):
    groups: list[GroupRequest]


async def init_telegram():
    await client.connect()
    if not await client.is_user_authorized():
        raise Exception("Telegram session not authorized")
    print("Telegram connected")

    # print("Telegram connected")
    # print("GROUP TITLE:", getattr(group, "title", None))
    # print("GROUP ID:", group.id)
    # print("GROUP USERNAME:", getattr(group, "username", None))
    #
    # client.add_event_handler(
    #     handle_group_message,
    #     events.NewMessage(chats=group.id)
    # )


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
    print("AI REQUEST:", user_message[:100])
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

async def handle_group_message(event):
    if not event.message.text:
        return

    chat = await event.get_chat()
    sender = await event.get_sender()

    sender_data = {
        "id": event.sender_id,
        "username": getattr(sender, "username", None),
        "first_name": getattr(sender, "first_name", None),
        "last_name": getattr(sender, "last_name", None),
        "phone": getattr(sender, "phone", None),
    }

    message_data = {
        "chat": {
            "id": event.chat_id,
            "title": getattr(chat, "title", None),
            "username": getattr(chat, "username", None),
        },

        "sender": sender_data,

        "message": {
            "id": event.message.id,
            "date": event.message.date.isoformat()
            if event.message.date else None,
            "text": event.message.text,
        }
    }

    print("========== GROUP MESSAGE ==========")
    print("CHAT ID:", message_data["chat"]["id"])
    print("CHAT TITLE:", message_data["chat"]["title"])

    print("SENDER ID:", sender_data["id"])
    print("SENDER USERNAME:", sender_data["username"])
    print("SENDER FIRST NAME:", sender_data["first_name"])
    print("SENDER LAST NAME:", sender_data["last_name"])

    print("MESSAGE ID:", message_data["message"]["id"])
    print("TEXT:", message_data["message"]["text"])
    print("===================================")

@app.post("/group/messages")
async def get_group_messages(req: GroupMessagesRequest):
    messages = []

    for group_request in req.groups:
        group_name = group_request.group
        limit = group_request.limit

        try:
            group = await client.get_entity(group_name)

            print("===================================")
            print("READING GROUP:", group_name)
            print("GROUP TITLE:", getattr(group, "title", None))
            print("GROUP ID:", group.id)
            print("GROUP USERNAME:", getattr(group, "username", None))
            print("LIMIT:", limit)
            print("===================================")

            group_messages = []

            async for message in client.iter_messages(
                    group,
                    limit=limit
            ):
                if not message.text:
                    continue

                chat = await message.get_chat()
                sender = await message.get_sender()

                sender_data = {
                    "id": message.sender_id,
                    "username": getattr(sender, "username", None),
                    "first_name": getattr(sender, "first_name", None),
                    "last_name": getattr(sender, "last_name", None),
                    "phone": getattr(sender, "phone", None),
                }

                message_data = {
                    "chat": {
                        "id": message.chat_id,
                        "title": getattr(chat, "title", None),
                        "username": getattr(chat, "username", None),
                    },

                    "sender": sender_data,

                    "message": {
                        "id": message.id,
                        "date": (
                            message.date.isoformat()
                            if message.date else None
                        ),
                        "text": message.text,
                    }
                }

                group_messages.append(message_data)

            messages.extend(reversed(group_messages))

        except Exception as e:
            print(
                f"ERROR READING GROUP {group_name}: {e}"
            )

    return {
        "count": len(messages),
        "messages": messages
    }

class ValidateTelegramContactsRequest(BaseModel):
    contacts: list[dict]  # [{"value": "...", "type": "..."}, ...]

@app.post("/telegram/validate")
async def validate_telegram_contacts(req: ValidateTelegramContactsRequest):
    """check the type of contact"""
    print(f"validate_telegram_contacts: {len(req.contacts)} контактов")

    results = []
    all_correct = True

    try:
        for contact in req.contacts:
            try:
                # get real contact
                resolve_result = await resolve_telegram_contact(contact["value"])

                if not resolve_result.get("success", True):
                    actual_type = "unknown"
                else:
                    actual_type = resolve_result.get("type", "unknown")

                # Проверяем совпадение
                declared_type = contact["type"].lower()
                is_correct = declared_type == actual_type.lower()
                all_correct = all_correct and is_correct

                results.append({
                    "value": contact["value"],
                    "declared_type": contact["type"],
                    "actual_type": actual_type,
                    "is_correct": is_correct,
                    "error": resolve_result.get("error") if not resolve_result.get("success") else None,
                    "details": {
                        "id": resolve_result.get("id"),
                        "username": resolve_result.get("username"),
                        "title": resolve_result.get("title"),
                    }
                })

            except Exception as e:
                print(f"ERROR VALIDATING {contact['value']}: {e}")
                all_correct = False
                results.append({
                    "value": contact["value"],
                    "declared_type": contact["type"],
                    "actual_type": "unknown",
                    "is_correct": False,
                    "error": str(e),
                    "details": None
                })

        return {
            "success": True,
            "all_correct": all_correct,
            "total": len(req.contacts),
            "correct_count": sum(1 for r in results if r["is_correct"]),
            "results": results
        }

    except Exception as e:
        print(f"ERROR IN VALIDATION: {e}")
        return {
            "success": False,
            "error": str(e),
            "results": []
        }

async def resolve_telegram_contact(contact: str):
    """
    Определяет реальный тип Telegram контакта используя Telethon

    Args:
        contact: Контакт (@username, https://t.me/username, и т.д.)

    Returns:
        Dict с типом контакта и дополнительной информацией
    """
    try:
        entity = await client.get_entity(contact)

        if isinstance(entity, User):
            return {
                "type": "bot" if entity.bot else "user",
                "id": entity.id,
                "username": entity.username,
                "first_name": entity.first_name,
                "last_name": entity.last_name,
            }

        if isinstance(entity, Channel):
            if entity.megagroup:
                entity_type = "group"
            elif entity.broadcast:
                entity_type = "channel"
            else:
                entity_type = "channel"

            return {
                "type": entity_type,
                "id": entity.id,
                "username": entity.username,
                "title": entity.title,
                "megagroup": entity.megagroup,
                "broadcast": entity.broadcast,
            }

        if isinstance(entity, Chat):
            return {
                "type": "chat",
                "id": entity.id,
                "username": getattr(entity, "username", None),
                "title": entity.title,
            }

        return {
            "type": "unknown",
            "id": getattr(entity, "id", None),
            "username": getattr(entity, "username", None),
            "title": getattr(entity, "title", None),
        }

    except Exception as e:
        print(f"Error resolving contact {contact}: {e}")
        return {
            "type": "unknown",
            "error": str(e)
        }

from telethon.errors import FloodWaitError
async def send_message_to_contact(contact: str, message: str, retry_count: int = 0):
    max_retries = 3

    try:
        await asyncio.sleep(2 + retry_count)   # небольшая пауза перед отправкой

        entity = await client.get_entity(contact)
        result = await client.send_message(entity, message)

        return {
            "success": True,
            "message_id": result.id,
            "contact": contact
        }

    except FloodWaitError as e:
        wait_seconds = e.seconds
        print(f"FloodWaitError: Telegram просит подождать {wait_seconds} секунд "
              f"(попытка {retry_count + 1}/{max_retries})")

        if retry_count >= max_retries:
            return {
                "success": False,
                "contact": contact,
                "error": f"Too many requests - max retries exceeded (нужно было ждать {wait_seconds}с)"
            }

        await asyncio.sleep(wait_seconds + 3)  # ждём столько, сколько сказал Telegram + запас
        return await send_message_to_contact(contact, message, retry_count + 1)

    except Exception as e:
        error_msg = str(e)
        print(f"Ошибка при отправке в {contact}: {error_msg}")
        print(f"Тип ошибки: {type(e)}")          # ← добавьте эту строку для диагностики

        return {
            "success": False,
            "contact": contact,
            "error": error_msg
        }

@app.post("/telegram/send")
async def send_telegram_message(req: SendMessageRequest):
    print(f"send_telegram_message: target={req.target}, text_len={len(req.text)}")
    result = await send_message_to_contact(req.target, req.text)
    return result
