"""
Yeh file LLM ko batati hai ke uske paas kaunse "tools" (actions) hain
jo woh use kar sakta hai — LLM khud decide karega kaunsa tool kab,
kaise, aur kis data ke saath call karna hai.

Yeh OpenAI ka "function calling" / "tool calling" format hai.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "save_lead_to_crm",
            "description": (
                "Naye lead ko law firm ke CRM mein save karta hai. "
                "Har naye lead ke liye yeh zaroor call karna chahiye, "
                "taake koi lead record se miss na ho."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Lead ka naam"},
                    "phone": {"type": "string", "description": "Lead ka phone number"},
                    "email": {"type": "string", "description": "Lead ka email (agar mila ho)"},
                    "practice_area": {
                        "type": "string",
                        "enum": ["Personal Injury", "Family Law", "Criminal Defense", "Estate Planning", "Other"],
                        "description": "Case kis type ka hai",
                    },
                    "incident_date": {"type": "string", "description": "Ghatna kab hui (ya 'unknown')"},
                    "incidentDate": {"type": "string", "description": "Alias for incident_date."},
                    "lead_incident_date": {"type": "string", "description": "Alias for incident_date."},
                    "key_details": {"type": "string", "description": "Case ke aham details, chhote mein"},
                    "keyDetails": {"type": "string", "description": "Alias for key_details."},
                    "lead_key_details": {"type": "string", "description": "Alias for key_details."},
                    "urgency": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Yeh lead kitni urgent hai",
                    },
                    "lead_urgency": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Alias for urgency.",
                    },
                    "leadUrgency": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Alias for urgency.",
                    },
                    "attribution": {
                        "type": "object",
                        "description": "Lead source and Google Ads attribution supplied by the webhook.",
                        "additionalProperties": {"type": "string"},
                    },
                },
                "required": ["name", "phone", "email", "practice_area"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "notify_team",
            "description": (
                "Firm ke intake staff ko turant alert bhejta hai (Slack). "
                "High-value ya urgent leads ke liye zaroor call karo, taake "
                "staff turant follow-up kar sake."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Ek chhota 1-sentence summary staff ke liye"},
                    "urgency": {"type": "string", "enum": ["high", "medium", "low"]},
                    "name": {"type": "string"},
                    "phone": {"type": "string"},
                },
                "required": ["summary", "urgency", "name", "phone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_auto_reply",
            "description": (
                "Prospect (lead) ko turant approved-template WhatsApp message bhejta hai, "
                "taake woh kisi doosri firm ko contact na kare. Sirf tab call karo "
                "jab lead ka phone number mojood ho aur message genuine legal inquiry ho."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": "string"},
                },
                "required": ["name", "phone"],
            },
        },
    },
]
