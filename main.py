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
"""

"""
from fastapi import FastAPI, Request
from groq import Groq
import json, glob

app = FastAPI()
client = Groq(api_key="gsk_GANTI_KEY_AKANG")

MODEL = "openai/gpt-oss-120b"  # INI YANG AKANG PAKE YANG MASIH GRATIS

def load_knowledge(bot_type):
    texts = []
    for file in glob.glob(f"*{bot_type}*.json") + glob.glob(f"knowledge/*{bot_type}*") + glob.glob("*.json"):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        texts.append(f"Q: {item.get('question','')} A: {item.get('answer','')}")
                else:
                    texts.append(json.dumps(data, ensure_ascii=False))
        except: pass
    return "\n".join(texts)[:8000] # gpt-oss-120b context gede, bisa 8k

KNOWLEDGE = {
    "sekolah": load_knowledge("sekolah"),
    "loker": load_knowledge("loker")
}

@app.post("/chat/{bot_type}")
async def chat(bot_type: str, request: Request):
    data = await request.json()
    msg = data.get("message","")
    knowledge = KNOWLEDGE.get(bot_type, "")

    prompt = f""/"Kamu CS {bot_type} SMK Farmasi. WAJIB jawab pake KNOWLEDGE di bawah, jangan ngarang.

    KNOWLEDGE:
    {knowledge}

    Pertanyaan user: {msg}
    Kalo ga ada di knowledge, jawab: Maaf info itu belum ada, hubungi admin sekolah."/""

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": msg}
        ],
        temperature=0.1,
        max_tokens=500
    )
    return {"answer": completion.choices[0].message.content}

@app.post("/chat")
async def chat_default(request: Request):
    return await chat("sekolah", request)
"""

from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

app = FastAPI()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PERSONAS = {
    "sekolah": "Kamu admin di SMK Farmasi Bandung. Ramah, singkat, jelas. Info pendaftaran, biaya, jurusan farmasi, akademis dan info obat-obatan. Bahasa Indonesia santai.",
    "loker": "Kamu admin Loker SMK Farmasi Bandung. Info lowongan kerja farmasi, apotek, RS. Bantu bikin CV singkat. Bahasa Indonesia gaul sopan."
}

def load_knowledge(bot_type):
    path = f"bots/bot-{bot_type}/knowledge"
    text = ""
    if os.path.exists(path):
        for f in os.listdir(path):
            with open(os.path.join(path, f), 'r') as file:
                text += file.read() + "\n"
    return text

@app.post("/chat/{bot_type}")
async def chat(bot_type: str, request: Request):
    data = await request.json()
    msg = data.get("message","")
    persona = PERSONAS.get(bot_type, PERSONAS["sekolah"])
    knowledge = load_knowledge(bot_type)
    system_prompt = f"{persona}. Gunakan info ini untuk jawab: {knowledge}"

    try:
        completion = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return {"answer": completion.choices[0].message.content}
    except Exception as e:
        print(f"Error: {e}")
        return {"answer": f"Maaf bot lagi sibuk: {e}"}

# Buat backward compatibility sama gateway lama
@app.post("/chat")
async def chat_default(request: Request):
    return await chat("sekolah", request)

@app.get("/")
def root():
    return {"status": "ExclusorAI Active", "bots": ["sekolah", "loker"]}