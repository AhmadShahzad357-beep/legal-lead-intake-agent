"""
Responder tool — LLM isay tab call karega jab usay lagega ke
prospect ko turant reassuring reply bhejni chahiye.

NOTE: Wording jaan bujh kar yahan fixed rakha gaya hai (LLM se
generate nahi karwaya) — kyunke yeh message client (law firm) se
approve karwaya hua hona chahiye, LLM ki marzi se nahi badalna chahiye.
LLM sirf yeh DECIDE karta hai ke reply bhejni hai ya nahi, wording
control mein rehti hai.
"""

import requests
import config

def send_auto_reply(name: str, phone: str) -> dict:
    if not phone:
        return {"status": "skipped", "sent": False, "reason": "no phone number"}

    if config.TEST_MODE or not (config.WHATSAPP_ACCESS_TOKEN and config.WHATSAPP_PHONE_NUMBER_ID):
        print("[TEST MODE] Prospect ko WhatsApp bhejne ki jagah yahan print ho raha hai:")
        print(f"  -> To: {phone} | Template: {config.WHATSAPP_TEMPLATE_NAME} | Name: {name}")
        return {"status": "test_mode", "sent": False}

    # Meta expects international E.164 digits without a plus sign.
    recipient = phone.strip().replace("+", "").replace(" ", "").replace("-", "")
    if not recipient.isdigit():
        return {"status": "skipped", "sent": False, "reason": "invalid WhatsApp phone number"}

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "template",
        "template": {
            "name": config.WHATSAPP_TEMPLATE_NAME,
            "language": {"code": config.WHATSAPP_TEMPLATE_LANGUAGE},
        },
    }
    url = (
        f"https://graph.facebook.com/{config.WHATSAPP_API_VERSION}/"
        f"{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )

    try:
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {config.WHATSAPP_ACCESS_TOKEN}"},
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        detail = response.text if "response" in locals() else str(exc)
        print(f"[Meta WhatsApp ERROR]: {detail}")
        return {"status": "error", "sent": False, "error": str(exc)}
    return {"status": "sent", "sent": True}