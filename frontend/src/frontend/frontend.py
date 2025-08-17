from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import asyncio
from typing import *

from models.confirm_game import ConfirmGame
from models.disconnect_response import DisconnectResponse
from models.pending_game import EndPendingGame
from models.player_info import PlayerInfo
from models.judge_game import EndJudgeGameOutput, JudgeGameAnswer, JudgeGameInput, JudgeGameOutput
from models.participant_game import AnswerInput, ResponseSubmit
from models.authentication import LoginResponse, RegisterResponse, UserLogin, UserRegister
from models.game_info import GameInfoInput, GameInfoOutput

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
from endpoints.game_info import game_info

from utility.rimuovi_sessioni_scadute import rimuovi_sessioni_scadute
from utility.verify_user_token import verify_user_token

app = FastAPI()
BASE_DIR = os.path.dirname(__file__)

class NoCacheStaticFiles(StaticFiles):
    """Classe custom per disabilitare caching su file statici."""
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

# Setup Jinja2 templates e mount directory per file statici con no-cache
templates = Jinja2Templates(directory= os.path.join(BASE_DIR, "../public/templates"))

app.mount("/assets", NoCacheStaticFiles(directory= os.path.join(BASE_DIR, "../public/assets")))
app.mount("/css", NoCacheStaticFiles(directory= os.path.join(BASE_DIR, "../public/css")))
app.mount("/js", NoCacheStaticFiles(directory= os.path.join(BASE_DIR, "../public/js")))

sessioni_attive: Dict[int, Dict[str, str]] = {}

@app.on_event("startup")
async def on_startup() -> None:
    """
    Evento startup FastAPI per avviare task asincrono
    che rimuove periodicamente sessioni scadute.
    """
    asyncio.create_task(rimuovi_sessioni_scadute(sessioni_attive))

@app.get("/", response_class=HTMLResponse)
def get_home_page(request: Request):
    return templates.TemplateResponse(
        "home.html", {"request": request}
    )

@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request}
    )

@app.get("/register", response_class=HTMLResponse)
def get_register_page(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request}
    )

@app.post("/login", response_model=LoginResponse)
def login_endpoint(request: Request, user: UserLogin):
    return user_login(user, request, sessioni_attive)

@app.post("/register", response_model=RegisterResponse)
def register_endpoint(request: Request, user: UserRegister):
    return user_register(user, request)

# start_game.html, contiene la schermata con AVVIA PARTITA GIUDICE PARTECIPANTE, token è query param
@app.get("/start-game/{user_id}", response_class=HTMLResponse)
def get_start_game_page(request: Request, user_id: int, token: str):
    if verify_user_token(user_id, token, sessioni_attive):
        return templates.TemplateResponse(
            "start_game.html", {"user_id": user_id, "request": request}
        )
    else:
        return templates.TemplateResponse(
            "login.html", {"request": request}
        )

@app.post("/start-game", response_model=ConfirmGame)
def start_game_endpoint(payload: PlayerInfo):
    return start_game(payload)

# player_id è query param /game/{game_id}?player_id={}, token={}
@app.get("/judge-game/{game_id}", response_class=HTMLResponse)
def get_judge_game_endpoint(game_id: int, player_id: int, token: str, request: Request):
    return get_judge_game(game_id, player_id, token, request, templates, sessioni_attive)

@app.post("/send-questions-judge-game/{game_id}", response_model=JudgeGameOutput)
async def send_questions_judge_game_endpoint(game_id: int, payload: JudgeGameInput):
    return await send_questions_judge_game(game_id, payload)

@app.post("/send-judge-answer/{game_id}", response_model=EndJudgeGameOutput)
def send_judge_answer_endpoint(game_id: int, payload: JudgeGameAnswer):
    return send_judge_answer(game_id, payload)

@app.get("/participant-game/{game_id}", response_class=HTMLResponse)
def get_participant_game_endpoint(game_id: int, player_id: int, token: str, request: Request):
    return get_participant_game(game_id, player_id, token, request, templates, sessioni_attive)

@app.post("/send-answers-participant-game/{game_id}", response_model=ResponseSubmit)
def send_answers_participant_game_endpoint(game_id: int, payload: AnswerInput):
    return send_answers_participant_game(game_id, payload)

@app.post("/start-pending-game", response_model=ConfirmGame)
async def start_pending_game_endpoint(payload: PlayerInfo):
    return await start_pending_game(payload)

@app.get("/verdict-game/{game_id}", response_class=HTMLResponse)
def get_verdict_game_endpoint(game_id: int, player_id: int, token: str, request: Request):
    return get_verdict_game(game_id, player_id, token, request, templates, sessioni_attive)

@app.post("/send-pending-verdict/{game_id}", response_model=EndPendingGame)
def send_pending_verdict_endpoint(game_id: int, request: Request, payload: JudgeGameAnswer):
    return send_pending_verdict(game_id, request, payload, templates)

@app.get("/profilo/{user_id}", response_class=HTMLResponse)
def get_profilo_endpoint(user_id: int, token: str, request: Request):
    return get_profilo(user_id, token, request, templates, sessioni_attive)

@app.post("/user-disconnect/{user_id}", response_model=DisconnectResponse)
def user_disconnect_endpoint(user_id: int):
    return user_disconnect(user_id, sessioni_attive)

@app.post("/game-info", response_model=GameInfoOutput)
def game_info_endpoint(payload: GameInfoInput):
    return game_info(payload)

@app.get("/{full_path:path}", response_class=HTMLResponse)
def catch_all(full_path: str, request: Request) -> HTMLResponse:
    """
    Endpoint catch-all per intercettare tutte le richieste verso percorsi non definiti.

    Questo endpoint viene utilizzato per gestire richieste a URL non mappati da altri endpoint
    restituendo una pagina HTML personalizzata 404 (pagina non trovata).

    Args:
        full_path (str): Percorso richiesto dal client, intercettato da questo catch-all.
        request (Request): Oggetto richiesta HTTP di FastAPI, passato al template per il rendering.

    Returns:
        HTMLResponse: Risposta HTML che renderizza la pagina "404.html" con il contesto della richiesta.
    """
    return templates.TemplateResponse(
        "404.html", {"request": request}
    )