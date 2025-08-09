from typing import Dict
from models.disconnect_response import DisconnectResponse

def user_disconnect(user_id: int, sessioni_attive: Dict[int, Dict[str, str]]) -> DisconnectResponse:
    """
    Gestisce la disconnessione di un utente rimuovendolo dalle sessioni attive.

    Controlla se l'utente è attualmente connesso tramite la presenza
    del suo ID nel dizionario delle sessioni attive.
    Se l'utente non è connesso, restituisce un messaggio di errore.
    Se l'utente è connesso, rimuove la sua sessione attiva e restituisce un messaggio di conferma.

    Args:
        user_id (int): Identificativo univoco dell'utente da disconnettere.
        sessioni_attive (Dict[int, Dict[str, str]]): Dizionario che mappa gli ID utente alle rispettive sessioni attive.

    Returns:
        DisconnectResponse: Oggetto contenente il messaggio di risultato dell'operazione.
    """
    if user_id not in sessioni_attive.keys():
        return DisconnectResponse(message= "Utente non connesso")
    
    sessioni_attive.pop(user_id)
    
    return DisconnectResponse(message= "Utente disconnesso con successo")