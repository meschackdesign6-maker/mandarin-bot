from flask import Flask, request
import google.generativeai as genai
import requests
import os
app = Flask(__name__)
VERIFY_TOKEN = "mandarin123"
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()
genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
@app.route("/")
def home():
    return "Mandarin Bot OK"
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "error", 403
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            msg = entry['messages'][0]
            from_id = msg['from']
            text = msg['text']['body']
            response = model.generate_content(text)
            reply = response.text
            phone_id = os.getenv("PHONE_ID")
            token = os.getenv("WHATSAPP_TOKEN")
            url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
            headers = {"Authorization": f"Bearer {token}"}
            payload = {"messaging_product": "whatsapp","to": from_id,"text": {"body": reply}}
            requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(e)
    return "ok", 200
