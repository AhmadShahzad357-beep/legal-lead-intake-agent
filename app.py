"""
Lead Intake Agent — Main Entry Point (v2: TRUE agent architecture)
====================================================================
Farak purane version se: pehle Python code khud decide karta tha
"pehle classify, phir CRM, phir Slack, phir SMS". Ab LLM ko tools
diye gaye hain aur woh KHUD decide karta hai kaunsa tool kab, kaise
call karna hai (dekhein agent.py).

Chalane ka tareeqa:
    python app.py
Phir POST request bhejein: http://localhost:5000/webhook/lead
"""

from collections import deque
from datetime import datetime, timezone
from threading import Lock

from flask import Flask, request, jsonify, render_template
from agent import run_agent
import config

app = Flask(__name__)
LEAD_ACTIVITY = deque(maxlen=100)
LEAD_ACTIVITY_LOCK = Lock()


def _first_value(data: dict, *keys: str) -> str:
    for key in keys:
        value = data.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _normalise_lead(data: dict) -> dict:
    """Normalise website, CallRail, and LSA-style payloads."""
    first_name = _first_value(data, "first_name", "firstname")
    last_name = _first_value(data, "last_name", "lastname")
    name = _first_value(data, "name", "caller_name", "customer_name")
    if not name:
        name = " ".join(part for part in (first_name, last_name) if part) or "Unknown"

    attribution = {
        key: _first_value(data, key)
        for key in ("source", "gclid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")
    }
    return {
        "name": name,
        "phone": _first_value(data, "phone", "phone_number", "caller_phone_number"),
        "email": _first_value(data, "email", "email_address"),
        "message": _first_value(data, "message", "notes", "transcript", "body", "description"),
        "attribution": {key: value for key, value in attribution.items() if value},
    }


def _record_lead(lead: dict, result: dict) -> None:
    """Store a compact presentation record for the local intake dashboard."""
    crm_args = next(
        (call.get("args", {}) for call in result.get("tool_calls_made", [])
         if call.get("tool") == "save_lead_to_crm"),
        {},
    )
    actions = {
        call.get("tool"): call.get("result", {}).get("status", "unknown")
        for call in result.get("tool_calls_made", [])
    }
    record = {
        "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
        "received_at": datetime.now().strftime("%I:%M %p"),
        "name": lead["name"],
        "phone": lead["phone"],
        "email": lead["email"],
        "message": lead["message"],
        "source": lead["attribution"].get("source", "Website"),
        "practice_area": crm_args.get("practice_area", "Pending review"),
        "urgency": crm_args.get("urgency", "medium"),
        "incident_date": crm_args.get("incident_date", "unknown"),
        "summary": crm_args.get("key_details", result.get("final_message", "")),
        "actions": actions,
    }
    with LEAD_ACTIVITY_LOCK:
        LEAD_ACTIVITY.appendleft(record)


@app.route("/", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/dashboard", methods=["GET"])
def dashboard_data():
    with LEAD_ACTIVITY_LOCK:
        leads = list(LEAD_ACTIVITY)

    stats = {
        "total": len(leads),
        "high_priority": sum(lead["urgency"] == "high" for lead in leads),
        "crm_saved": sum(lead["actions"].get("save_lead_to_crm") == "saved" for lead in leads),
        "messages_sent": sum(lead["actions"].get("send_auto_reply") == "sent" for lead in leads),
    }
    return jsonify({"leads": leads, "stats": stats})


@app.route("/webhook/lead", methods=["POST"])
def receive_lead():
    """
    Naya lead yahan aata hai. Expected JSON body:
    {
        "name": "Ali Khan",
        "phone": "+923001234567",
        "email": "ali@example.com",
        "message": "Kal mera car accident hua, meri tang toot gayi"
    }

    Security: URL mein ?secret=WEBHOOK_SECRET query param zaroor hona
    chahiye (form-builder / CallRail / LSA config mein bhi yehi secret
    daalna hoga). Yeh sirf request ko validate karta hai — encryption
    nahi hai, isliye HTTPS (Railway auto-deta hai) ke sath use karein.
    """
    if config.WEBHOOK_SECRET:
        if request.args.get("secret") != config.WEBHOOK_SECRET:
            return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "request body must be a JSON object"}), 400

    lead = _normalise_lead(data)
    name = lead["name"]
    phone = lead["phone"]
    email = lead["email"]
    message = lead["message"]

    if not message:
        return jsonify({"error": "message field is required"}), 400

    # Poora kaam agent.run_agent() ke andar hota hai — yahan hum sirf
    # lead ka raw data agent ko dete hain, aage ka faisla LLM khud karta hai.
    try:
        result = run_agent(name=name, phone=phone, email=email, message=message,
                           attribution=lead["attribution"])
    except Exception as exc:
        app.logger.exception("Lead processing failed")
        response = {"error": "lead processing is temporarily unavailable"}
        if app.debug:
            response["error_type"] = type(exc).__name__
        return jsonify(response), 502

    _record_lead(lead, result)
    return jsonify({"status": "success", **result}), 200


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)