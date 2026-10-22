from fastapi import FastAPI, Request
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_from_file(path):
    text = ""
    if os.path.exists(path):
        for f in os.listdir(path):
            with open(os.path.join(path, f), 'r') as file:
                text += file.read() + "\n"
    return text

def load_persona():
    persona = "Nama kamu Bhakso, kamu adalah digital assistant di SMK Farmasi Bandung. Pakai bahasa Indonesia yang sopan, ramah, singkat, jelas tapi tetap santai."
    return persona

def load_knowledge():
    knowledge = "SMK Farmasi Bhakti Kencana Soreang, sekolah kejuruan farmasi terbaik di Kabupaten Bandung. Alamat: Jl. Raya Soreang-Banjaran No. 297, Soreang, Kabupaten Bandung. Jurusan: Farmasi dan Keperawatan"
    return knowledge

@app.post("/chat/{agent_name}")
async def chat(agent_name: str, request: Request):
    data = await request.json()
    msg = data.get("message","")

    persona = load_persona(agent_name)
    knowledge = load_knowledge(agent_name)

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
        return {"answer": f"Maaf layanan tidak tersedia: {e}"}

# Buat backward compatibility sama gateway lama
@app.post("/chat")
async def chat_default(request: Request):
    return await chat("dummy", request)

@app.get("/")
def root():
    return {"status": "ExclusorAI Active"}