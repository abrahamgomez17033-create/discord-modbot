import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX", "!")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
MUTE_ROLE_NAME = os.getenv("MUTE_ROLE_NAME", "Muted")
TICKET_CATEGORY_NAME = os.getenv("TICKET_CATEGORY_NAME", "Tickets")
STAFF_ROLES = os.getenv("STAFF_ROLES", "Admin,Mod,Staff").split(",")

if not TOKEN:
    raise ValueError("TOKEN no configurado. Define la variable de entorno TOKEN.")