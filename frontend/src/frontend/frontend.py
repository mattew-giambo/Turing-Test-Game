from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import asyncio
from models.player_info import PlayerInfo
from models.judge_game import JudgeGameAnswer, JudgeGameInput
from models.participant_game import AnswerInput
from models.authentication import UserLogin, UserRegister
from typing import *

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
from utility.verify_user_token import verify_user_token

app = FastAPI()
BASE_DIR = os.path.dirname(__file__)

class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

# MIDDLEWARE PER LA GESTIONE DEI FILE STATICI
templates = Jinja2Templates(directory= os.path.join(BASE_DIR, "../public/templates"))

app.mount("/assets", NoCacheStaticFiles(directory= os.path.join(BASE_DIR, "../public/assets")))
app.mount("/css", NoCacheStaticFiles(directory= os.path.join(BASE_DIR, "../public/css")))
app.mount("/js", NoCacheStaticFiles(directory= os.path.join(BASE_DIR, "../public/js")))

sessioni_attive: Dict[int, Dict[str, str]] = {}

@app.on_event("startup")
async def on_startup():
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
def login_endpoint(request: Request, user: UserLogin):
    return user_login(user, request, sessioni_attive)

@app.post("/register")
def register_endpoint(request: Request, user: UserRegister):
    return user_register(user, request)

# start_game.html, contiene la schermata con AVVIA PARTITA GIUDICE PARTECIPANTE, token è query param
@app.get("/start-game/{user_id}")
def get_start_game_page(request: Request, user_id: int, token: str):
    if verify_user_token(user_id, token, sessioni_attive):
        return templates.TemplateResponse(
            "start_game.html", {"user_id": user_id, "request": request}
        )
    else:
        return templates.TemplateResponse(
            "login.html", {"request": request}
        )

# Endpoint per gestire l'avvio effettivo della partita classica
@app.post("/start-game")
def start_game_endpoint(payload: PlayerInfo):
    return start_game(payload)

# player_id è query param /game/{game_id}?player_id={}, token={}
@app.get("/judge-game/{game_id}")
def get_judge_game_endpoint(game_id: int, player_id: int, token: str, request: Request):
    return get_judge_game(game_id, player_id, token, request, templates, sessioni_attive)

@app.post("/send-questions-judge-game/{game_id}")
async def send_questions_judge_game_endpoint(game_id: int, payload: JudgeGameInput):
    return await send_questions_judge_game(game_id, payload)

@app.post("/send-judge-answer/{game_id}")
def send_judge_answer_endpoint(game_id: int, payload: JudgeGameAnswer):
    return send_judge_answer(game_id, payload)

@app.get("/participant-game/{game_id}")
def get_participant_game_endpoint(game_id: int, player_id: int, token: str, request: Request):
    return get_participant_game(game_id, player_id, token, request, templates, sessioni_attive)

@app.post("/send-answers-participant-game/{game_id}")
def send_answers_participant_game_endpoint(game_id: int, payload: AnswerInput):
    return send_answers_participant_game(game_id, payload)

@app.post("/start-pending-game")
def start_pending_game_endpoint(payload: PlayerInfo):
    return start_pending_game(payload)

@app.get("/verdict-game/{game_id}")
def get_verdict_game_endpoint(game_id: int, player_id: int, token: str, request: Request):
    return get_verdict_game(game_id, player_id, token, request, templates, sessioni_attive)

@app.post("/send-pending-verdict/{game_id}")
def send_pending_verdict_endpoint(game_id: int, request: Request, payload: JudgeGameAnswer):
    return send_pending_verdict(game_id, request, payload, templates)

# USER 
@app.get("/profilo/{user_id}")
def get_profilo_endpoint(user_id: int, token: str, request: Request):
    return get_profilo(user_id, token, request, templates, sessioni_attive)

@app.post("/user-disconnect/{user_id}")
def user_disconnect_endpoint(user_id: int):
    return user_disconnect(user_id, sessioni_attive)

@app.exception_handler(404)
def not_found_handler(request: Request, exc):
    return templates.TemplateResponse(
        "404.html", {"request": request}
    )

# @app.get("/user-stats/{user_id}")
# def get_user_stats_endpoint(user_id: int, request: Request):
#     return get_user_stats(user_id, request, templates)

# @app.get("/user-games/{user_id}")
# def get_user_games_endpoint(user_id: int, request: Request):
#     return get_user_games(user_id, request, templates)

# @app.get("/user-info/{user_id}")
# def get_user_info_endpoint(user_id: int, request: Request):
#     return get_user_info(user_id, request)