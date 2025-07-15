from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import requests
from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from models.game_info import GameInfoInput, GameInfoOutput
from models.judge_game import JudgeGameInput, JudgeGameOutput, JudgeGameAnswer, EndJudgeGameOutput
from models.user_stats import UserStats
from models.user_games import UserGames
from models.user_info import UserInfo
from models.participant_game import ParticipantGameOutput, AnswerInput, ResponseSubmit
from models.pending_game import QA, GameReviewOutput, JudgeGameAnswer, EndPendingGame
from config.constants import API_BASE_URL
from typing import *

app = FastAPI()
BASE_DIR = os.path.dirname(__file__)
# MIDDLEWARE PER LA GESTIONE DEI FILE STATICI
templates = Jinja2Templates(directory= os.path.join(BASE_DIR, "../public/templates"))

app.mount("/assets", StaticFiles(directory= os.path.join(BASE_DIR, "../public/assets")))
app.mount("/css", StaticFiles(directory= os.path.join(BASE_DIR, "../public/css")))
app.mount("/js", StaticFiles(directory= os.path.join(BASE_DIR, "../public/js")))

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

# start_game.html, contiene la schermata con AVVIA PARTITA GIUDICE PARTECIPANTE
@app.get("/start-game")
def get_start_game_page(request: Request):
    return templates.TemplateResponse(
        "start_game.html", {"request": request}
    )

# Endpoint per gestire l'avvio effettivo della partita classica
@app.post("/start-classic-game")
def start_game(payload: PlayerInfo, request: Request):
    try:
        response = requests.post(os.path.join(API_BASE_URL, "/start-game-api"), json= payload.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore sconosciuto")
        )
    return ConfirmGame.model_validate(response.json())

# player_id è query param /game/{game_id}?player_id={}
@app.get("/judge-game/{game_id}")
def get_game(game_id: int, player_id: int, request: Request):
    try:
        payload = GameInfoInput(player_id= player_id, game_id= game_id)
        response = requests.post(os.path.join(API_BASE_URL, "/game-info-api"), json= payload.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = response.json()
        if response.status_code == 404:
            return templates.TemplateResponse(
            "game_not_found.html", {
                "request": request
            }
        )
        else:
            raise HTTPException(
                status_code= error_data.get("status_code", 500),
                detail= error_data.get("detail", "Errore sconosciuto")
            )
    response_data = GameInfoOutput.model_validate(response.json())

    if response_data.terminated == True or response_data.player_role == "participant":
        return templates.TemplateResponse(
            "partita_terminata.html", {
                "request": request
            }
        )
    
    return templates.TemplateResponse(
        "judge_game.html", {
            "request": request,  
            "game_id": response_data.game_id,
            "data": response_data.data,
            "player_id": response_data.player_id}
        )

@app.post("/send-questions-judge-game/{game_id}")
def send_questions_judge_game(game_id: int, request: Request, question1: str = Form(...), question2: str = Form(...), question3: str = Form(...)):
    try:
        payload = JudgeGameInput(questions_list= [question1, question2, question3])
        response = requests.post(os.path.join(API_BASE_URL, f"/judge-game-api/{game_id}"), json= payload.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = response.json()
        if response.status_code == 404:
            return templates.TemplateResponse(
            "game_not_found.html", {
                "request": request
            }
        )
        else:
            raise HTTPException(
                status_code= error_data.get("status_code", 500),
                detail= error_data.get("detail", "Errore sconosciuto")
            )
    
    return JudgeGameOutput.model_validate(response.json())

@app.post("/send-judge-answer/{game_id}")
def send_judge_answer(game_id: int, request: Request, payload: JudgeGameAnswer):
    try:
        response = requests.post(os.path.join(API_BASE_URL, f"/judge-game-api/{game_id}"), json= payload.model_dump())
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = response.json()
        if response.status_code == 404:
            return templates.TemplateResponse(
            "game_not_found.html", {
                "request": request
            }
        )
        else:
            raise HTTPException(
                status_code= error_data.get("status_code", 500),
                detail= error_data.get("detail", "Errore sconosciuto")
            )
        
    return EndJudgeGameOutput.model_validate(response.json())

@app.get("/user-stats/{user_id}")
def get_user_stats(user_id: int, request: Request):
    try:
        response = requests.get(os.path.join(API_BASE_URL, f"/user-stats-api/{user_id}"))
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = response.json()
        if response.status_code == 404:
            return templates.TemplateResponse(
            "game_not_found.html", {
                "request": request
            }
        )
        else:
            raise HTTPException(
                status_code= error_data.get("status_code", 500),
                detail= error_data.get("detail", "Errore sconosciuto")
            )
        
    response_data = UserStats.model_validate(response.json())

    return templates.TemplateResponse(
        "user_stats.html", {
            "request": request,
            "user_id": response_data.user_id,
            "n_games": response_data.n_games,
            "score_part": response_data.score_part,
            "score_judge": response_data.score_judge,
            "won_part": response_data.won_part,
            "won_judge": response_data.won_judge,
            "lost_part": response_data.lost_part,
            "lost_judge": response_data.lost_judge
        })

@app.get("/user-games/{user_id}")
def get_user_games(user_id: int, request: Request):
    try:
        response = requests.get(os.path.join(API_BASE_URL, f"/user-games-api/{user_id}"))
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore sconosciuto")
        )

    response_data = UserGames.model_validate(response.json())
    return templates.TemplateResponse(
        "user_games.html",{
            "request": request,
            "user_id": response_data.user_id,
            "user_games": response_data.user_games
        }
    )

@app.get("/user-info/{user_id}")
def get_user_info(user_id: int, request: Request):
    try:
        response = requests.get(os.path.join(API_BASE_URL, f"/user-info-api/{user_id}"))
        response.raise_for_status()
    except requests.RequestException as e:
        error_data: Dict = response.json()
        raise HTTPException(
            status_code= error_data.get("status_code", 500),
            detail= error_data.get("detail", "Errore sconosciuto")
        )
    
    return UserInfo.model_validate(response.json())

@app.post("/send-pending-verdict/{game_id}")
def send_pending_verdict(game_id: int, request: Request, payload: JudgeGameAnswer):
    try:
        response = requests.post(os.path.join(API_BASE_URL, f"/end-pending-game-api/{game_id}"), json=payload.model_dump())
        response.raise_for_status()
        result = EndPendingGame.model_validate(response.json())

    except requests.RequestException as e:
        try:
            detail = e.response.json().get("detail", "Errore nella richiesta")
        except Exception:
            detail = str(e)
        if e.response and e.response.status_code == 404:
            return templates.TemplateResponse("game_not_found.html", {"request": request})
        raise HTTPException(status_code=e.response.status_code if e.response else 500, detail=detail)

    return result

@app.get("/participant-game/{game_id}")
def get_participant_game(game_id: int, player_id: int, request: Request):
    # 1 Ottiene info sulla partita
    try:
        payload = GameInfoInput(player_id=player_id, game_id=game_id)
        response = requests.post(os.path.join(API_BASE_URL, "/game-info-api"), json=payload.model_dump())
        response.raise_for_status()
        game_info = GameInfoOutput.model_validate(response.json())
    except requests.RequestException as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)

        if e.response and e.response.status_code == 404:
            return templates.TemplateResponse("game_not_found.html", {"request": request})

        raise HTTPException(status_code=500, detail=f"Errore durante il recupero: {error_detail}")

    # 2 Blocca se partita terminata o se è il giudice
    if game_info.terminated or game_info.player_role == "judge":
        return templates.TemplateResponse("partita_terminata.html", {"request": request})

    # 3 Ottiene/genera le domande via /participant-game-api/{game_id}
    try:
        response = requests.post(os.path.join(API_BASE_URL, f"/participant-game-api/{game_id}"))
        response.raise_for_status()
        game_data = ParticipantGameOutput.model_validate(response.json())
    except requests.RequestException as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)

        if e.response and e.response.status_code == 404:
            return templates.TemplateResponse("game_not_found.html", {"request": request})

        raise HTTPException(status_code=500, detail=f"Errore durante il recupero: {error_detail}")
    
    # 4 Renderizza il template con le domande e le info
    return templates.TemplateResponse(
        "participant_game.html",
        {
            "request": request,
            "game_id": game_info.game_id,
            "player_id": game_info.player_id,
            "data": game_info.data,
            "questions": game_data.questions
        }
    )

@app.post("/send-answers-participant-game/{game_id}")
def send_answers_participant_game(game_id: int, request: Request, answer1: str = Form(...), answer2: str = Form(...), answer3: str = Form(...)):
    try:
        payload = AnswerInput(answers=[answer1, answer2, answer3])
        response = requests.post(os.path.join(API_BASE_URL, f"/submit-participant-answers-api/{game_id}"), json=payload.model_dump())
        response.raise_for_status()
        response_submit = ResponseSubmit.model_validate(response.json())
    except requests.RequestException as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except Exception:
            error_detail = str(e)

        if e.response and e.response.status_code == 404:
            return templates.TemplateResponse("game_not_found.html", {"request": request})

        raise HTTPException(status_code=500, detail=f"Errore durante il recupero: {error_detail}")
    
    return response_submit

@app.post("/start-pending-game")
def start_pending_game(player_name: int, request: Request):
    payload = UserInfo(player_name=player_name, player_role="judge")

    try:
        response = requests.post(os.path.join(API_BASE_URL, "/start-pending-game-api"), json= payload.model_dump())
        response.raise_for_status()
        game_data = GameReviewOutput.model_validate(response.json())
    except requests.RequestException as e:
        status_code = e.response.status_code if e.response else 500
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)

        raise HTTPException(status_code=status_code, detail=detail)
    
    return templates.TemplateResponse("pending_game.html", {
        "request": request,
        "game_id": game_data.game_id,
        "session": game_data.session
    })