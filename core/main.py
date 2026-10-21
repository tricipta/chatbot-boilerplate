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