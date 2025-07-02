from fastapi import FastAPI, HTTPException
from models.user_info import UserInfo
from models.confirm_game import ConfirmGame
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from typing import Dict, Any
import time

app = FastAPI()
active_games: Dict[str, Dict[Any]] = {}

@app.post("/start-game")
def start_game(payload: UserInfo):
    player_name = payload.player_name
    player_role = payload.player_role

    ## Verifica dell'utente nel database
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    query= "SELECT id FROM Users WHERE user_name = %s"
    cursor.execute(query, player_name)
    result = cursor.fetchone()

    if(result is None):
        raise HTTPException(status_code= 401, detail= "User not found")
    ##

    ## Inserimento della partita nel database e nel dizionario
    user_id = result[0]
    query = "INSERT INTO Games(user_id, player_role) VALUES (%s, %s)"
    cursor.execute(query, (user_id, player_role))
    connection.commit()
    game_id = cursor.lastrowid

    active_games[game_id] = {
        "player_name": player_name,
        "player_role": player_role,
        "timestamp": time.time(),
        "result": None
    }
    ##

    return ConfirmGame(game_id= game_id)