from fastapi import HTTPException
import requests
from config.constants import API_BASE_URL
from typing import Dict
from urllib.parse import urljoin
from models.disconnect_response import DisconnectResponse

def user_disconnect(user_id: int, sessioni_attive: Dict[int, Dict[str, str]]):
    if user_id not in sessioni_attive.keys():
        return DisconnectResponse(message= "Utente non connesso")
    
    sessioni_attive.pop(user_id)
    return DisconnectResponse(message= "Utente disconnesso con successo")