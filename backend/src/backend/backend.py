from fastapi import FastAPI
from models.user_info import UserInfo
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb

app = FastAPI()
active_games = {}

@app.post("/start-game")
def start_game(payload: UserInfo):
    user_name = payload.user_name
    user_role = payload.user_role

    # Verifica dell'utente nel database
    connection: mariadb.Connection = connect_to_database()