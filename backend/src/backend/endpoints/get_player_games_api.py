from fastapi import HTTPException
from models.user_games import UserGames, Game
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor

def get_player_games_api(user_id: int):
    connection = connect_to_database()
    cursor = get_cursor(connection) 
    
    cursor.execute("""SELECT g.game_id, g.date, ug.player_role, g.terminated, ug.is_won, ug.points
                    FROM Users as u JOIN UserGames as ug ON u.id = ug.user_id
                   """)
    result = cursor.fetchall()

    if not result:
        raise HTTPException(
            status_code= 404,
            detail= "Utente non trovato"
        )

    close_cursor(cursor)
    close_connection(connection)

    return UserGames(user_id= user_id, 
                     user_games= [Game(game_id= game_id, data= data, player_role= player_role, terminated= terminated, is_won= is_won, points= points) for game_id, data, player_role, terminated, is_won, points in result])
