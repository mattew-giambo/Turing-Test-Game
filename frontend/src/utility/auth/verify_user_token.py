from typing import Dict

def verify_user_token(user_id: int, token: str, sessioni_attive: Dict[int, Dict[str, str]]) -> bool:
    """
    Verifica la validità del token di sessione associato a un utente autenticato.

    La funzione controlla se l'utente è presente tra le sessioni attive e se il token
    fornito corrisponde al token salvato. In caso di mismatch, la sessione viene rimossa
    per motivi di sicurezza.

    Args:
        user_id (int): Identificativo univoco dell'utente.
        token (str): Token di sessione da validare.
        sessioni_attive (Dict[int, Dict[str, str]]): Dizionario delle sessioni attive, 
            mappa user_id a un dizionario contenente informazioni di sessione (es. token, timestamp).

    Returns:
        bool: True se il token è valido e corrisponde alla sessione attiva, False altrimenti.
    """
    if user_id in sessioni_attive.keys():
        if token == sessioni_attive.get(user_id).get("token"):
            return True
        else:
            sessioni_attive.pop(user_id)
            return False
    else:
        return False

