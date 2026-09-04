"""
Yeh file "asli agent" hai — yahan LLM sirf text return nahi karta,
balke usay actual tools (functions) diye gaye hain jo woh khud call
kar sakta hai. LLM khud decide karta hai:
  - Kaunsa tool call karna hai
  - Kis order mein call karna hai
  - Kya data (arguments) us tool ko dena hai
  - Kitni baar call karna hai (ek, do, ya sab teeno)

Yeh "tool calling" / "function calling" kehlata hai — yehi cheez
isay ek deterministic script se "agent" banati hai.
"""

import json
from openai import OpenAI

import config
from tools.definitions import TOOLS
from tools.crm import save_lead_to_crm
from tools.notifier import notify_team
from tools.responder import send_auto_reply

# Tool ka naam -> actual Python function. Jab LLM kahe "save_lead_to_crm
# call karo", hum yahan se real function dhoond kar chalate hain.
TOOL_REGISTRY = {
    "save_lead_to_crm": save_lead_to_crm,
    "notify_team": notify_team,
    "send_auto_reply": send_auto_reply,
}

CRM_ARGUMENT_ALIASES = {
    "incident_date": ("incidentDate", "lead_incident_date"),
    "key_details": ("keyDetails", "lead_key_details"),
    "urgency": ("lead_urgency", "leadUrgency"),
}

SYSTEM_PROMPT = """You are the intake agent for a personal injury / family law firm.

A new lead has just come in (from a website form, a phone call transcript, or
a Google LSA notification). Your job is to handle it end-to-end using the
tools available to you:

- save_lead_to_crm: log every lead into the CRM, no exceptions.
- notify_team: alert the intake staff, especially for high-urgency leads.
- send_auto_reply: reassure the prospect with a quick text, if we have their
  phone number and the message is a genuine legal inquiry.

Read the lead's message carefully, decide the practice area, incident date,
key details, and urgency yourself, then call whichever tools are appropriate
in whatever order makes sense. You may call more than one tool. Once you've
handled the lead, reply with a short confirmation summary — do not repeat
raw tool output.
"""


def _get_client():
    return OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)


def run_agent(name: str, phone: str, email: str, message: str,
              attribution: dict | None = None) -> dict:
    """
    Poora agent loop chalata hai:
    1. LLM ko lead ka data + tools deta hai
    2. LLM jo bhi tools call karna chahe, unhein execute karta hai
    3. Results LLM ko wapas deta hai
    4. Jab tak LLM aur tools call na kare, loop chalta rehta hai
    5. Aakhri mein LLM ka final text summary return karta hai
    """
    attribution = attribution or {}
    if config.TEST_MODE or not config.LLM_API_KEY:
        return _test_mode_fallback(name, phone, email, message, attribution)

    client = _get_client()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"New lead:\nName: {name}\nPhone: {phone}\nEmail: {email}\n"
                f"Message: {message}\nAttribution: {json.dumps(attribution)}"
            ),
        },
    ]

    tool_calls_made = []

    # Yeh loop hi "agent" hai — jab tak LLM tools call karta rahega,
    # hum unhein chalate rahenge aur result wapas dete rahenge.
    for _ in range(6):  # safety limit — infinite loop se bachne ke liye
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        choice = response.choices[0]
        messages.append(choice.message.model_dump(exclude_none=True))

        if choice.finish_reason != "tool_calls":
            # LLM ne decide kar liya ke ab koi aur tool nahi chahiye
            return {
                "final_message": choice.message.content,
                "tool_calls_made": tool_calls_made,
            }

        # LLM ne ek ya zyada tools call karne ka faisla kiya hai
        for tool_call in choice.message.tool_calls:
            fn_name = tool_call.function.name
            try:
                fn_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                fn_args = {}
                result = {"status": "error", "error": "LLM returned invalid tool arguments"}
                tool_calls_made.append({"tool": fn_name, "args": fn_args, "result": result})
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
                continue

            fn = TOOL_REGISTRY.get(fn_name)
            if fn is None:
                result = {"error": f"unknown tool {fn_name}"}
            else:
                if fn_name == "save_lead_to_crm":
                    fn_args.setdefault("attribution", attribution)
                    for canonical_name, aliases in CRM_ARGUMENT_ALIASES.items():
                        for alias in aliases:
                            if alias in fn_args:
                                fn_args.setdefault(canonical_name, fn_args[alias])
                                del fn_args[alias]
                    fn_args.setdefault("incident_date", "unknown")
                    fn_args.setdefault("key_details", "No details provided")
                    fn_args.setdefault("urgency", "medium")
                try:
                    result = fn(**fn_args)
                except (TypeError, ValueError) as exc:
                    result = {"status": "error", "error": str(exc)}

            tool_calls_made.append({"tool": fn_name, "args": fn_args, "result": result})

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, default=str),
            })

    return {"final_message": "Max tool-call turns reached.", "tool_calls_made": tool_calls_made}


def _test_mode_fallback(name: str, phone: str, email: str, message: str,
                        attribution: dict) -> dict:
    """
    Agar OpenAI key nahi hai, to real LLM call nahi ho sakti — lekin
    hum phir bhi 'agentic' flow simulate karte hain taake aap poora
    system bina paid key ke test kar sakein. Yahan tools ko hardcoded
    tareeqe se call kiya ja raha hai, sirf demo/testing ke liye.
    """
    print("[TEST MODE] OpenAI key nahi hai — LLM ki jagah simulated agent chal raha hai.")
    tool_calls_made = []

    r1 = save_lead_to_crm(
        name=name, phone=phone, email=email,
        practice_area="Personal Injury", incident_date="yesterday",
        key_details="TEST DATA - no OpenAI key set", urgency="high",
        attribution=attribution,
    )
    tool_calls_made.append({"tool": "save_lead_to_crm", "result": r1})

    r2 = notify_team(
        summary=f"[TEST MODE] New lead from {name}",
        urgency="high", name=name, phone=phone,
    )
    tool_calls_made.append({"tool": "notify_team", "result": r2})

    r3 = send_auto_reply(name=name, phone=phone)
    tool_calls_made.append({"tool": "send_auto_reply", "result": r3})

    return {
        "final_message": "[TEST MODE] Lead handled by simulated agent (no real LLM call).",
        "tool_calls_made": tool_calls_made,
    }
