from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import requests
import asyncio
from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from models.game_info import GameInfoInput, GameInfoOutput
from models.judge_game import JudgeGameInput, JudgeGameOutput, JudgeGameAnswer, EndJudgeGameOutput
from models.user_stats import UserStats
from models.user_games import UserGames
from models.user_info import UserInfo
from models.participant_game import ParticipantGameOutput, AnswerInput, ResponseSubmit
from models.pending_game import GameReviewOutput, JudgeGameAnswer, EndPendingGame
from config.constants import API_BASE_URL
from typing import *
from urllib.parse import urljoin
from models.disconnect_response import DisconnectResponse

from endpoints.start_game import start_game
from endpoints.get_judge_game import get_judge_game
from endpoints.send_questions_judge_game import send_questions_judge_game
from endpoints.send_judge_answer import send_judge_answer
from endpoints.get_participant_game import get_participant_game
from endpoints.send_answers_participant_game import send_answers_participant_game
from endpoints.start_pending_game import start_pending_game
from endpoints.get_verdict_game import get_verdict_game
from endpoints.send_pending_verdict import send_pending_verdict
from endpoints.user_disconnect import user_disconnect
from endpoints.user_login import user_login
from endpoints.get_profilo import get_profilo
from endpoints.user_register import user_register

from utility.rimuovi_sessioni_scadute import rimuovi_sessioni_scadute

app = FastAPI()
BASE_DIR = os.path.dirname(__file__)
# MIDDLEWARE PER LA GESTIONE DEI FILE STATICI
templates = Jinja2Templates(directory= os.path.join(BASE_DIR, "../public/templates"))

app.mount("/assets", StaticFiles(directory= os.path.join(BASE_DIR, "../public/assets")))
app.mount("/css", StaticFiles(directory= os.path.join(BASE_DIR, "../public/css")))
app.mount("/js", StaticFiles(directory= os.path.join(BASE_DIR, "../public/js")))

sessioni_attive: Dict[int, Dict[str, str]] = {}

asyncio.create_task(rimuovi_sessioni_scadute(sessioni_attive))

@app.get("/")
def get_home_page(request: Request):
    return templates.TemplateResponse(
        "home.html", {"request": request}
    )

@app.get("/login")
def get_login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request}
    )

@app.get("/register")
def get_register_page(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request}
    )

@app.post("/login")
def login_endpoint(request: Request, email: str = Form(...), password: str = Form(...)):
    return user_login(email, password, request, sessioni_attive)

@app.post("/register")
def register_endpoint(request: Request, user_name:str = Form(...), email: str = Form(...), password: str = Form(...)):
    return user_register(user_name, email, password, request)

# start_game.html, contiene la schermata con AVVIA PARTITA GIUDICE PARTECIPANTE
@app.get("/start-game/{user_id}")
def get_start_game_page(request: Request, user_id: int):
    if user_id in sessioni_attive.keys():
        return templates.TemplateResponse(
            "start_game.html", {"request": request}
        )
    else:
        return templates.TemplateResponse(
            "login.html", {"request": request}
        )

# Endpoint per gestire l'avvio effettivo della partita classica
@app.post("/start-game")
def start_game_endpoint(payload: PlayerInfo, request: Request):
    return start_game(payload, request)

# player_id è query param /game/{game_id}?player_id={}
@app.get("/judge-game/{game_id}")
def get_judge_game_endpoint(game_id: int, player_id: int, request: Request):
    return get_judge_game(game_id, player_id, request, templates, sessioni_attive)

@app.post("/send-questions-judge-game/{game_id}")
def send_questions_judge_game_endpoint(game_id: int, request: Request, question1: str = Form(...), question2: str = Form(...), question3: str = Form(...)):
    return send_questions_judge_game(game_id, request, question1, question2, question3, templates)

@app.post("/send-judge-answer/{game_id}")
def send_judge_answer_endpoint(game_id: int, request: Request, payload: JudgeGameAnswer):
    return send_judge_answer(game_id, request, payload, templates)

@app.get("/participant-game/{game_id}")
def get_participant_game_endpoint(game_id: int, player_id: int, request: Request):
    return get_participant_game(game_id, player_id, request, templates, sessioni_attive)

@app.post("/send-answers-participant-game/{game_id}")
def send_answers_participant_game_endpoint(game_id: int, request: Request, answer1: str = Form(...), answer2: str = Form(...), answer3: str = Form(...)):
    return send_answers_participant_game(game_id, request, answer1, answer2, answer3, templates)

@app.post("/start-pending-game")
def start_pending_game_endpoint(player_id: int, request: Request):
    return start_pending_game(player_id, request)

@app.get("/verdict-game/{game_id}")
def get_verdict_game_endpoint(game_id: int, player_id: int, request: Request):
    return get_verdict_game(game_id, player_id, request, templates, sessioni_attive)

@app.post("/send-pending-verdict/{game_id}")
def send_pending_verdict_endpoint(game_id: int, request: Request, payload: JudgeGameAnswer):
    return send_pending_verdict(game_id, request, payload, templates)

# USER 
@app.get("/profilo/{user_id}")
def get_profilo_endpoint(user_id: int, request: Request):
    return get_profilo(user_id, request, sessioni_attive)

@app.post("/user-disconnect/{user_id}")
def user_disconnect_endpoint(user_id: int):
    return user_disconnect(user_id, sessioni_attive)

# @app.get("/user-stats/{user_id}")
# def get_user_stats_endpoint(user_id: int, request: Request):
#     return get_user_stats(user_id, request, templates)

# @app.get("/user-games/{user_id}")
# def get_user_games_endpoint(user_id: int, request: Request):
#     return get_user_games(user_id, request, templates)

# @app.get("/user-info/{user_id}")
# def get_user_info_endpoint(user_id: int, request: Request):
#     return get_user_info(user_id, request)