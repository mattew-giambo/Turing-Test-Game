from fastapi import HTTPException
from models.game_info import GameInfoInput, GameInfoOutput
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor

def game_info_api(payload: GameInfoInput):
    player_id = payload.player_id
    game_id = payload.game_id
    connection = connect_to_database()
    cursor = get_cursor(connection)

    cursor.execute("""
    SELECT id, date, terminated, player_id, player_role
    FROM Games as g JOIN UserGames as ug ON g.id = ug.game_id
    WHERE g.id = %s AND ug.player_id = %s
    """, (game_id, player_id))
    result = cursor.fetchone()

    if result is None:
        raise HTTPException(status_code= 404,
                            detail= "Nessuna partita trovata con questo id per questo giocatore")
    
    close_cursor(cursor)
    close_connection(connection)

    return GameInfoOutput(
        game_id= result[0],
        data= result[1],
        terminated= result[2],
        player_id= result[3],
        player_role= result[4] 
    )