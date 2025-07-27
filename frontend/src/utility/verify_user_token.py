from typing import Dict

def verify_user_token(user_id: int, token: str, sessioni_attive: Dict[int, Dict[str, str]]) -> bool:
    if user_id in sessioni_attive.keys():
        if token == sessioni_attive.get(user_id).get("token"):
            return True
        else:
            sessioni_attive.pop(user_id)
            return False
    else:
        return False

