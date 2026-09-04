# Lead Intake Agent — v2 (True Agent Architecture)

Yeh v1 se different hai: pehle Python code khud order decide karta tha
(pehle classify, phir CRM, phir Slack, phir WhatsApp — hardcoded sequence).

**Ab LLM ko "tools" diye gaye hain aur woh KHUD decide karta hai:**
- Kaunsa tool call karna hai (CRM save? Team notify? Auto-reply?)
- Kis order mein
- Kya data un tools ko dena hai
- Kitni baar call karna hai

Yeh farak `agent.py` mein hai — waha ek loop hai jahan LLM tools maangta
hai, hum unhein execute karte hain, result LLM ko wapas dete hain, aur
yeh chalta rehta hai jab tak LLM khud na kahe "ab kaam khatam".

## Folder structure
```
lead_intake_agent_v2/
  app.py                  <- Webhook server (sirf entry point)
  agent.py                <- ASLI AGENT LOOP (yahan LLM tools call karta hai)
  config.py                <- API keys
  test_lead.py              <- Test ke liye dummy lead bhejta hai
  tools/
    definitions.py          <- LLM ko dikhne wali tool descriptions (schema)
    crm.py                   <- Actual CRM save function
    notifier.py              <- Actual Slack notify function
    responder.py             <- Actual WhatsApp reply function
  .env.example
  requirements.txt
```

## Yeh "real agent" kyun hai (v1 se farak)

| | v1 (script) | v2 (agent) |
|---|---|---|
| Order kaun decide karta hai | Python code (hardcoded) | LLM khud |
| AI kya karta hai | Sirf classify (ek kaam) | Poora decision-making |
| Tools LLM ko dikhte hain? | Nahi | Haan (`tools/definitions.py`) |
| Agar lead adhoora ho | Same steps chalte, chahe useless ho | LLM khud skip/adjust kar sakta hai |

## Setup

1. ```
   pip install -r requirements.txt
   cp .env.example .env
   ```
2. `TEST_MODE=false` rehne dein jab tak real keys na hon — is halat mein
   real LLM call nahi hoti (kyunki OpenAI key nahi), balke ek
   "simulated agent" fallback chalta hai taake aap poora flow dekh sakein.
3. Real test karne ke liye `OPENAI_API_KEY` daal dein — phir asli LLM
   tools call karega (dekhein `agent.py` ka terminal output, saaf pata
   chalega LLM ne kaunsa tool kab call kiya).

## Chalana

Full website + lead-agent backend ek saath chalane ke liye (Node.js 18+ aur
Python installed hon):
```
npm start
```
Phir browser mein `http://localhost:3000` kholein. Node server frontend serve
karta hai aur Flask lead-agent ko khud start karta hai. Form ka API secret
browser mein expose nahi hota.

Sirf backend test karna ho to alag terminal mein:
```
python app.py
```
Aur phir:
```
python test_lead.py
```

## Existing website ke saath integration

Is frontend ko `https://intake.yourfirm.com` par deploy karein aur kisi bhi
WordPress, Webflow, Shopify ya custom website par is iframe ko page mein paste
karein:
```html
<iframe src="https://intake.yourfirm.com"
  title="Request a consultation" width="100%" height="760"
  style="border:0; max-width:1200px; display:block; margin:auto;"></iframe>
```
`server.js` frontend form ko Flask ke protected `/webhook/lead` endpoint par
server-side proxy karta hai; `WEBHOOK_SECRET` kabhi website visitor ko nahi
milta. Production mein `FRONTEND_PORT`, `BACKEND_URL`, aur `WEBHOOK_SECRET`
apne deployment provider ki environment variables mein set karein.

## Real keys milne par

`.env` mein yeh dalein aur `TEST_MODE=false` karein (poori instructions
`.env.example` mein comment ke sath likhi hain):
- `LLM_API_KEY` — Groq se free milti hai (asli agent loop chalane ke liye)
- `HUBSPOT_API_KEY` — real CRM (free HubSpot account, private app token)
- `SLACK_WEBHOOK_URL` — team notification ke liye
- `WHATSAPP_ACCESS_TOKEN` / `WHATSAPP_PHONE_NUMBER_ID` — Meta WhatsApp auto-reply
- `WEBHOOK_SECRET` — koi bhi random string, isse fake/spam leads block hote hain

## Railway par deploy karna (taake ye client ke liye 24/7 live rahe)

1. Is poore folder ko GitHub repo mein push karein.
2. https://railway.app par account banayein (GitHub se login).
3. "New Project" -> "Deploy from GitHub repo" -> apna repo select karein.
4. Railway khud `Procfile` dekh kar `gunicorn` se app chala dega.
5. "Variables" tab mein sab `.env` wali keys yahan bhi daal dein
   (LLM_API_KEY, HUBSPOT_API_KEY, SLACK_WEBHOOK_URL, WHATSAPP_*,
   WEBHOOK_SECRET, TEST_MODE=false).
6. Deploy hone ke baad Railway ek public URL dega, jaise:
   `https://your-app.up.railway.app`
7. Live webhook URL: `https://your-app.up.railway.app/webhook/lead?secret=YOUR_WEBHOOK_SECRET`
   — yehi URL website form / CallRail / LSA config mein dalna hai.

## Website form ko connect karna

Jo bhi form-builder use ho raha hai (WordPress/Elementor, Webflow,
Typeform, Zapier wagera), uska "on submit -> send webhook / POST
request" feature use karein aur URL yeh dein:
```
https://your-app.up.railway.app/webhook/lead?secret=YOUR_WEBHOOK_SECRET
```
Body mein `name`, `phone`, `email`, `message` fields map karni hongi.

CallRail aur Google LSA ke liye alag se webhook config unki respective
dashboards mein karni hoti hai — donon similar POST-to-URL pattern
follow karte hain, wahi upar wala URL dena hai.

## ⚠️ Zaroori: WhatsApp consent and template compliance

Chunke ye ek **law firm** ke liye automated WhatsApp bhej raha hai,
prospect se pehle explicit WhatsApp opt-in lena zaroori hai. Website
form mein consent checkbox aur WhatsApp Terms/Privacy Policy ka link
rakhein. Pehla outbound message Meta-approved template hona chahiye;
client ke legal/compliance team se wording aur consent process approve
karwa kar hi `TEST_MODE=false` karein.

## Note on message wording

`tools/responder.py` Meta ka approved template bhejta hai. LLM sirf
yeh decide karta hai ke reply bhejni hai ya nahi; wording Meta template
aur client approval ke control mein rehti hai.

Suggested template body:
```
Hi {{1}}, thank you for contacting [Firm Name]. We have received your
inquiry. A member of our intake team will contact you shortly.
```
