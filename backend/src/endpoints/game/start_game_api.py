from models.start_game_info import StartGameInfo
from models.confirm_game import ConfirmGame
from utility.game.start_classic_game import start_classic_game
from utility.game.start_verdict_game import start_verdict_game

def start_game_api(payload: StartGameInfo) -> ConfirmGame:
    if payload.mode == "classic":
        return start_classic_game(payload)
    else:
        return start_verdict_game(payload)
        
