from typing import List
from fastapi import HTTPException
from models.user_games import UserGames, Game
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb

def get_player_games_api(user_id: int) -> UserGames:
    """
    Restituisce la lista delle partite giocate da un determinato utente,
    con informazioni dettagliate su ogni sessione (ruolo, punteggio, esito, ecc.).

    Args:
        user_id (int): ID dell'utente di cui si vogliono recuperare le partite.

    Returns:
        UserGames: Oggetto contenente l'ID utente e la lista delle sue partite.

    Raises:
        HTTPException: Se l'utente non ha partite registrate o in caso di errore del database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = """
            SELECT g.id, g.game_date, ug.player_role, g.is_terminated, ug.is_won, ug.points
            FROM Games AS g
            JOIN UserGames AS ug ON g.id = ug.game_id
            WHERE ug.player_id = %s
            ORDER BY g.game_date DESC
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()

        if not result:
            return UserGames(
                user_id=user_id,
                user_games=[]
            )

        games: List[Game] = [
            Game(
                game_id=row[0],
                player_role=row[2],
                data=row[1],
                terminated=row[3],
                is_won=row[4],
                points=row[5]
            )
            for row in result
        ]

        return UserGames(
                user_id=user_id,
                user_games=games
            )

    except mariadb.Error as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Errore del server."
        )

    finally:
        close_cursor(cursor)
        close_connection(connection)