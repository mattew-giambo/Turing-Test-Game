from fastapi import Request, HTTPException, Form
from fastapi.templating import Jinja2Templates
import requests
from models.judge_game import JudgeGameInput, JudgeGameOutput
from config.constants import API_BASE_URL
from typing import *
import asyncio
from urllib.parse import urljoin

async def send_questions_judge_game(game_id: int, request: Request, payload: JudgeGameInput):
    try:
        response = requests.post(urljoin(API_BASE_URL, f"/judge-game-api/{game_id}"), json= payload.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict =  e.response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore sconosciuto")
        )

    await asyncio.sleep(30) # wait di 60s
    return JudgeGameOutput.model_validate(response.json())