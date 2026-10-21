"""
from fastapi import FastAPI, Request
from core.rag_engine import get_answer

app = FastAPI()

@app.get("/")
def root(request: Request):
    host = request.headers.get("host", "")
    if "loker" in host:
        return {"bot": "loker", "msg": "Bot Loker Aktif"}
    else:
        return {"bot": "sekolah", "msg": "Bot Sekolah Aktif"}

@app.post("/chat")
async def chat(request: Request):
    host = request.headers.get("host", "")
    body = await request.json()
    bot_id = "bot-loker" if "loker" in host else "bot-sekolah"
    answer = get_answer(bot_id, body.get("message"))
    return {"answer": answer}
"""

from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

def load_knowledge(bot_type):
    path = f"bots/bot-{bot_type}/knowledge"
    text = ""
    if os.path.exists(path):
        for f in os.listdir(path):
            with open(os.path.join(path, f), 'r') as file:
                text += file.read() + "\n"
    return text

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message","")
    host = request.headers.get("host","").lower()
    
    bot_type = "loker" if "loker" in host or "8001" in host or "/loker" in str(request.url) else "sekolah"
    knowledge = load_knowledge(bot_type)
    
    system_prompt = f"Kamu bot {bot_type}. Gunakan info ini untuk jawab: {knowledge}. Jika tidak ada di info, jawab tidak tahu dan arahkan ke admin."

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content": system_prompt},
            {"role":"user","content": message}
        ]
    )
    return {"bot": bot_type, "answer": completion.choices[0].message.content}