from fastapi import HTTPException
from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from datetime import datetime
from typing import Dict, Any


def start_game_api(payload: PlayerInfo, active_judge_games: Dict[int, Dict[str, Any]]):
    player_id = payload.player_id
    player_role = payload.player_role

    ## Verifica dell'utente nel database
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    cursor.execute("SELECT player_name FROM Users WHERE id = %s", player_id)
    result = cursor.fetchone()
    
    if(result is None):
        raise HTTPException(status_code= 404, detail= "Utente non trovato")
    ##

    player_name = result[0]
    ## Inserimento della partita nel database e nel dizionario
    try:
        cursor.execute( "INSERT INTO Games() VALUES ()")
        game_id = cursor.lastrowid()
        cursor.execute( "INSERT INTO UserGames(game_id, player_id, player_role) VALUES (%s)", (game_id, player_id, player_role))
        connection.commit()
    except mariadb.Error as e:
        print(e)
        raise HTTPException(
            status_code= 500,
            detail= "Errore del server nell'esecuzione della query"
        )
    finally:
        close_cursor(cursor)
        close_connection(connection)

    if player_role == 'judge':
        active_judge_games[game_id] = {
            "player_name": player_name,
            "datetime": datetime.now(),
            "opponent_ai": None
        }
    ##
    return ConfirmGame(game_id= game_id, player_id= player_id, player_name= player_name, player_role= player_role)
