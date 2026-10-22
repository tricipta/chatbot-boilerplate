from fastapi import FastAPI, Request
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_persona():
    persona = "Kamu digital assistant akademis di SMK Farmasi Bandung. Pakai bahasa Indonesia yang sopan, ramah, singkat, jelas tapi tetap santai."
    return persona

def load_knowledge():
    path = f"brain"
    text = ""
    if os.path.exists(path):
        for f in os.listdir(path):
            with open(os.path.join(path, f), 'r') as file:
                text += file.read() + "\n"
    return text

@app.post("/chat/{client_id}")
async def chat(client_id: str, request: Request):
    data = await request.json()
    msg = data.get("message","")
    persona = load_persona(client_id)
    knowledge = load_knowledge(client_id)

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