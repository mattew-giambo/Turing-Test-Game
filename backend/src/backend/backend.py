from fastapi import FastAPI
from typing import *

from models.player_info import PlayerInfo
from models.judge_game import JudgeGameInput, JudgeGameAnswer, JudgeGameOutput, EndJudgeGameOutput
from models.participant_game import ParticipantGameOutput, AnswerInput, ResponseSubmit
from models.game_info import GameInfoInput, GameInfoOutput
from models.authentication import UserRegister, UserLogin, RegisterResponse, LoginResponse
from models.pending_game import GameReviewOutput, EndPendingJudgeGameOutput
from models.confirm_game import ConfirmGame
from models.user_stats import UserStats
from models.user_games import UserGames
from models.user_info import UserInfo

from endpoints.register_api import register_api
from endpoints.login_api import login_api
from endpoints.start_game_api import start_game_api
from endpoints.judge_game_api import judge_game_api
from endpoints.participant_game_api import participant_game_api
from endpoints.submit_answers_api import submit_answers_api
from endpoints.start_pending_game_api import start_pending_game_api
from endpoints.get_pending_game_api import get_pending_game_api
from endpoints.end_judge_game_api import end_judge_game_api
from endpoints.end_pending_game import end_pending_game_api
from endpoints.get_user_stats_api import get_user_stats_api
from endpoints.get_player_games_api import get_player_games_api
from endpoints.game_info_api import game_info_api
from endpoints.get_user_info_api import get_user_info_api

app = FastAPI()

@app.post("/register-api", response_model=RegisterResponse)
def register_api_endpoint(user: UserRegister):
    return register_api(user)

@app.post("/login-api", response_model=LoginResponse)
def login_api_endpoint(user: UserLogin):
    return login_api(user)

@app.post("/start-game-api", response_model=ConfirmGame)
def start_game_endpoint(payload: PlayerInfo):
    return start_game_api(payload)

@app.post("/judge-game-api/{game_id}", response_model=JudgeGameOutput)
def judge_game_endpoint(payload: JudgeGameInput, game_id: int):
    return judge_game_api(payload, game_id)
        
@app.post("/participant-game-api/{game_id}", response_model=ParticipantGameOutput)
def participant_game_endpoint(game_id: int):
    return participant_game_api(game_id)

@app.post("/submit-participant-answers-api/{game_id}", response_model=ResponseSubmit)
def submit_answers_endpoint(game_id: int, input_data: AnswerInput):
    return submit_answers_api(game_id, input_data)

@app.post("/start-pending-game-api", response_model=ConfirmGame)
def start_pending_game_endpoint(payload: PlayerInfo) -> ConfirmGame:
    return start_pending_game_api(payload)

@app.get("/pending-game-session/{game_id}", response_model=GameReviewOutput)
def get_pending_game_endpoint(game_id: int) -> GameReviewOutput:
    return get_pending_game_api(game_id)

@app.post("/end-judge-game-api/{game_id}", response_model=EndJudgeGameOutput)
def end_judge_game_endpoint(judge_answer: JudgeGameAnswer, game_id: int):
    return end_judge_game_api(judge_answer, game_id)

@app.post("/end-pending-game-api/{game_id}", response_model=EndPendingJudgeGameOutput)
def end_pending_game_endpoint(judge_answer: JudgeGameAnswer, game_id: int):
    return end_pending_game_api(judge_answer, game_id)

@app.get("/user-stats-api/{user_id}", response_model=UserStats)
def get_user_stats_endpoint(user_id: int):
    return get_user_stats_api(user_id)

@app.get("/user-games-api/{user_id}", response_model=UserGames)
def get_player_games_endpoint(user_id: int):
    return get_player_games_api(user_id)

@app.post("/game-info-api", response_model=GameInfoOutput)
def game_info_endpoint(payload: GameInfoInput):
    return game_info_api(payload)

@app.get("/user-info-api/{user_id}", response_model=UserInfo)
def get_user_info_endpoint(user_id: int):
    return get_user_info_api(user_id)