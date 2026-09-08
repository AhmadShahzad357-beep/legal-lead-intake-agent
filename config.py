"""
Yeh file saari settings/API keys ek jagah se load karti hai.
Real keys .env file mein daali jayengi (yeh file kabhi share/upload nahi hoti).
"""

import os
from dotenv import load_dotenv

load_dotenv()  # .env file se values uthata hai

# --- LLM Provider ---
# Groq bilkul free hai (koi credit card nahi chahiye) aur OpenAI jaisa
# hi API use karta hai. Agar aap OpenAI use karna chahte hain, LLM_BASE_URL
# ko khali chhor dein aur OPENAI_API_KEY mein apni OpenAI key dalein.
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")  # default model

# Purana naam bhi rakha hai backward-compatibility ke liye
OPENAI_API_KEY = LLM_API_KEY

# --- HubSpot (CRM) ---
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY", "")

# --- Slack (team notification ke liye) ---
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# --- Meta WhatsApp Cloud API (prospect ko auto-reply ke liye) ---
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v25.0")
WHATSAPP_TEMPLATE_NAME = os.getenv("WHATSAPP_TEMPLATE_NAME", "lead_intake_auto_reply")
WHATSAPP_TEMPLATE_LANGUAGE = os.getenv("WHATSAPP_TEMPLATE_LANGUAGE", "en_US")

# --- Webhook security ---
# Yeh secret query param (?secret=...) se match hona chahiye, warna
# request reject ho jayegi. Isse koi bhi random banda internet se
# aapke webhook par fake leads nahi bhej sakta.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# --- Test mode ---
# Agar TEST_MODE True hai, to koi real WhatsApp/Slack message nahi jayega,
# bas console mein print hoga. Isse aap bina paid accounts ke poora
# system test kar sakte hain.
TEST_MODE = os.getenv("TEST_MODE", "true").lower() in ("true", "1", "yes", "on")