from fastapi import HTTPException
import requests
from models.user_stats import UserStats
from config.constants import API_BASE_URL
from typing import *
from urllib.parse import urljoin

def get_user_stats(user_id: int):
    try:
        response = requests.get(urljoin(API_BASE_URL, f"/user-stats-api/{user_id}"))
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = e.response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore sconosciuto")
        )
    
    return UserStats.model_validate(response.json())