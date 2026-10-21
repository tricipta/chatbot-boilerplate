import os
# Ini nanti logic buat baca knowledge base per bot
def get_answer(bot_id: str, query: str):
    # bot_id = bot-sekolah / bot-loker
    # Baca file di bots/{bot_id}/knowledge/
    return f"[Jawaban dari {bot_id}] untuk: {query}"