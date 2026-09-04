"""
Notifier tool — LLM isay tab call karega jab usay lagega ke intake
team ko turant alert karna chahiye.
"""

import requests
import config


def notify_team(summary: str, urgency: str, name: str, phone: str) -> dict:
    message = f"[{urgency.upper()} PRIORITY] {summary}\nName: {name} | Phone: {phone}"

    if config.TEST_MODE or not config.SLACK_WEBHOOK_URL:
        print("[TEST MODE] Slack alert bhejne ki jagah yahan print ho raha hai:")
        print(f"  -> {message}")
        return {"status": "test_mode", "sent": False}

    try:
        response = requests.post(config.SLACK_WEBHOOK_URL, json={"text": message}, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[Slack ERROR]: {exc}")
        return {"status": "error", "sent": False, "error": str(exc)}
    return {"status": "sent", "sent": True}
