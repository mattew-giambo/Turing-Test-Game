import asyncio
from datetime import datetime, timedelta
from typing import Dict

async def rimuovi_sessioni_scadute(sessioni_attive: Dict[int, Dict[str, str]]):
    while True:
        now = datetime.now()
        scaduti = []
        for user_id in sessioni_attive.keys():
            if now - sessioni_attive[user_id]["timestamp"] > timedelta(minutes= 20):
                scaduti.append(user_id)
        for user_id in scaduti:
            sessioni_attive.pop(user_id)
        
        await asyncio.sleep(60)  # controlla ogni minuto
