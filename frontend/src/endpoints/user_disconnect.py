from fastapi import HTTPException
import requests
from config.constants import API_BASE_URL
from typing import Dict
from urllib.parse import urljoin
from models.disconnect_response import DisconnectResponse

def user_disconnect(user_id: int):
    try:
        response = requests.post(urljoin(API_BASE_URL, f"/user-disconnect-api/{user_id}"))
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = e.response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore sconosciuto")
        )
    return DisconnectResponse.model_validate(response.json())