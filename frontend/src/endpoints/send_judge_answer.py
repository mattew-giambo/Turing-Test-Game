from fastapi import Request, HTTPException
import requests
from models.judge_game import JudgeGameAnswer, EndJudgeGameOutput
from config.constants import API_BASE_URL
from typing import Dict
from urllib.parse import urljoin

def send_judge_answer(game_id: int, payload: JudgeGameAnswer) -> EndJudgeGameOutput:
    try:
        response = requests.post(
            urljoin(API_BASE_URL, f"/end-judge-game-api/{game_id}"),
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

    return EndJudgeGameOutput.model_validate(response.json())