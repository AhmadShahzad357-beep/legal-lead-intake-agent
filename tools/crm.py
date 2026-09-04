"""HubSpot CRM integration for enriched legal leads."""

import re

import requests

import config

HUBSPOT_CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
ATTRIBUTION_PROPERTIES = {
    "source", "gclid", "utm_source", "utm_medium", "utm_campaign",
    "utm_term", "utm_content",
}


def _missing_properties(response: requests.Response) -> set[str]:
    """Return HubSpot property names rejected because they do not exist yet."""
    try:
        errors = response.json().get("errors", [])
    except ValueError:
        return set()

    missing = set()
    for error in errors:
        if error.get("code") == "PROPERTY_DOESNT_EXIST":
            missing.update(error.get("context", {}).get("propertyName", []))
    return missing


def save_lead_to_crm(name: str, phone: str, email: str, practice_area: str,
                     incident_date: str, key_details: str, urgency: str,
                     attribution: dict | None = None) -> dict:
    """Create or update a HubSpot contact without letting CRM failures crash intake."""
    if config.TEST_MODE or not config.HUBSPOT_API_KEY:
        print("[TEST MODE] HubSpot save skipped.")
        print(f"  -> Would save: {name}, {phone}, {email}, {practice_area}, {incident_date}, {key_details}, {urgency}")
        return {"status": "test_mode", "saved": False}

    first_name, _, last_name = name.partition(" ")
    properties = {
        "firstname": first_name or name,
        "lastname": last_name,
        "phone": phone,
        "email": email,
        "practice_area": practice_area,
        "incident_date": incident_date,
        "key_details": key_details,
        "lead_urgency": urgency,
    }
    for key, value in (attribution or {}).items():
        if key in ATTRIBUTION_PROPERTIES and value:
            properties[key] = value

    payload = {"properties": {key: value for key, value in properties.items() if value is not None}}
    headers = {
        "Authorization": f"Bearer {config.HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }

    skipped_properties = set()
    try:
        response = requests.post(HUBSPOT_CONTACTS_URL, headers=headers, json=payload, timeout=10)
    except requests.RequestException as exc:
        print(f"[HubSpot ERROR]: {exc}")
        return {"status": "error", "saved": False, "error": str(exc)}

    # A contact should still be captured if HubSpot custom fields have not
    # been configured yet. Retry once using only properties HubSpot accepts.
    if response.status_code == 400:
        skipped_properties = _missing_properties(response)
        if skipped_properties:
            payload["properties"] = {
                key: value for key, value in payload["properties"].items()
                if key not in skipped_properties
            }
            try:
                response = requests.post(HUBSPOT_CONTACTS_URL, headers=headers, json=payload, timeout=10)
            except requests.RequestException as exc:
                print(f"[HubSpot ERROR]: {exc}")
                return {"status": "error", "saved": False, "error": str(exc)}

    # HubSpot returns 409 for a duplicate email. Update that record instead.
    if response.status_code == 409:
        message = response.json().get("message", "")
        match = re.search(r"(?:Existing ID|ID):\s*(\d+)", message)
        if match:
            try:
                response = requests.patch(
                    f"{HUBSPOT_CONTACTS_URL}/{match.group(1)}",
                    headers=headers,
                    json=payload,
                    timeout=10,
                )
            except requests.RequestException as exc:
                print(f"[HubSpot ERROR]: {exc}")
                return {"status": "error", "saved": False, "error": str(exc)}

    if not response.ok:
        print(f"[HubSpot ERROR {response.status_code}]: {response.text}")
        return {
            "status": "error",
            "saved": False,
            "http_status": response.status_code,
            "error": response.text,
        }

    result = {"status": "saved", "saved": True, "contact": response.json()}
    if skipped_properties:
        result["skipped_properties"] = sorted(skipped_properties)
    return result


# Create these HubSpot Contact properties before enabling live mode:
# practice_area, incident_date, key_details, lead_urgency, source, gclid,
# utm_source, utm_medium, utm_campaign, utm_term, utm_content.
