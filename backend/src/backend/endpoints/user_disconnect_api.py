from typing import Dict
from models.disconnect_response import DisconnectResponse

def user_disconnect_api(user_id: int, sessioni_attive: Dict):
    if user_id not in sessioni_attive.keys():
        return DisconnectResponse(message= "Utente non connesso")
    
    sessioni_attive.pop(user_id)
    return DisconnectResponse(message= "Utente disconnesso con successo")
    
