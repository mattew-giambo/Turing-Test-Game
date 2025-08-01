import asyncio
from fastapi import HTTPException
from urllib.parse import urljoin
from typing import Dict
import requests
import random
from models.judge_game import JudgeGameInput, JudgeGameOutput
from config.constants import API_BASE_URL

async def send_questions_judge_game(game_id: int, payload: JudgeGameInput):
    try:
        response = requests.post(
            urljoin(API_BASE_URL, f"/judge-game-api/{game_id}"),
            json=payload.model_dump()
        )
        response.raise_for_status()

    except requests.RequestException as e:
        status_code = 500
        detail = "Errore sconosciuto"
        if e.response is not None:
            status_code = e.response.status_code
            try:
                error_data: Dict = e.response.json()
                detail = error_data.get("detail", detail)
            except Exception:
                detail = e.response.text or detail

        raise HTTPException(status_code=status_code, detail=detail)

    # Attendi un tempo randomico tra 0 e 30s
    await asyncio.sleep(random.randint(0, 30))

    return JudgeGameOutput.model_validate(response.json())