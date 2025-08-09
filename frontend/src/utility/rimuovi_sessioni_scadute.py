import asyncio
from datetime import datetime, timedelta
from typing import Dict

async def rimuovi_sessioni_scadute(sessioni_attive: Dict[int, Dict[str, str]]) -> None:
    """
    Task asincrono che rimuove periodicamente le sessioni utente scadute.

    Controlla ogni minuto le sessioni attive e rimuove quelle con timestamp più vecchio
    di 20 minuti, garantendo così la pulizia automatica delle sessioni inattive.

    Args:
        sessioni_attive (Dict[int, Dict[str, str]]): Dizionario delle sessioni attive,
            con timestamp associato a ciascun user_id.
    
    Returns:
        None
    """
    while True:
        now = datetime.now()
        scaduti = []
        for user_id in sessioni_attive.keys():
            if now - sessioni_attive[user_id]["timestamp"] > timedelta(minutes= 20):
                scaduti.append(user_id)
        for user_id in scaduti:
            sessioni_attive.pop(user_id)
        
        await asyncio.sleep(60)  # Attende 60 secondi prima del prossimo controllo
