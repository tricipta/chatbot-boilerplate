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