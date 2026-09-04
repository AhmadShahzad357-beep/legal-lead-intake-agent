"""
Yeh script khud ek fake/dummy lead bana kar aapke agent (app.py) ko
bhejti hai — taake aap bina real website form ke bhi poora system
test kar sakein.

Chalane se pehle app.py ko ek terminal mein alag se chala lein:
    python app.py

Phir doosre terminal mein yeh chalayein:
    python test_lead.py
"""

import requests
import config

url = "http://localhost:5000/webhook/lead"
if config.WEBHOOK_SECRET:
    url += f"?secret={config.WEBHOOK_SECRET}"

sample_leads = [
    {
        "name": "Ali Khan",
        "phone": "+923226305614",
        "email": "ali@example.com",
        "message": "Kal mera car accident hua, meri tang toot gayi, mujhe lawyer chahiye.",
    },
    {
        "name": "Sara Ahmed",
        "phone": "+923226305614",
        "email": "sara@example.com",
        "message": "I need help with a divorce case, we have two kids.",
    },
]

for lead in sample_leads:
    response = requests.post(url, json=lead)
    print(f"\n--- Sent lead for {lead['name']} ---")
    print("Status:", response.status_code)
    print("Response:", response.json())
