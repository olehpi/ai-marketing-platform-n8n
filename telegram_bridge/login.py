import os

from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
PHONE = os.environ["PHONE"]

client = TelegramClient("sessions/telegram_session", API_ID, API_HASH)

client.start(phone=PHONE)
print("LOGIN SUCCESS")
client.disconnect()
