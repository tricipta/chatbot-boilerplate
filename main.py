"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Tricipta Chatbot Boilerplate")

# Dummy knowledge base per bot
KNOWLEDGE = {
    "sekolah": "Kamu adalah Bot Informasi Sekolah SMK Farmasi. Jawab ramah soal pendaftaran, jurusan, alamat.",
    "loker": "Kamu adalah Bot Loker SMK Farmasi. Jawab soal lowongan, magang, kerjasama industri."
}

@app.get("/")
async def root(request: Request):
    host = request.headers.get("host", "").lower()
    if "loker" in host:
        bot = "loker"
    else:
        bot = "sekolah"
    return {"status": "ok", "detected_bot": bot, "host": host, "message": KNOWLEDGE[bot]}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    host = request.headers.get("host", "").lower()
    
    bot_type = "loker" if "loker" in host else "sekolah"
    
    # TODO: Nanti ganti ini pake OpenAI + RAG dari folder knowledge/
    answer = f"[{bot_type.upper()}] Halo! Kamu nanya: '{message}'. Ini jawaban dari bot {bot_type} (host: {host})"
    
    return {"bot": bot_type, "host": host, "answer": answer}

@app.get("/health")
def health():
    return {"status": "healthy"}
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