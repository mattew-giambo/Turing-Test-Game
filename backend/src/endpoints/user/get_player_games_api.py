from typing import List
from fastapi import HTTPException
from models.user_games import UserGames, Game
from utility.db.close_connection import close_connection
from utility.db.close_cursor import close_cursor
from utility.db.connect_to_database import connect_to_database
from utility.db.get_cursor import get_cursor
import mariadb

def get_player_games_api(user_id: int) -> UserGames:
    """
    Recupera tutte le partite giocate da un utente (sia come partecipante che come giudice),
    ordinate per data decrescente. Le partite in cui l'utente è giudice e non terminate 
    vengono considerate abbandonate e quindi eliminate dal database.

    Args:
        user_id (int): Identificativo univoco dell'utente.

    Returns:
        UserGames: Oggetto contenente l'elenco delle partite associate all'utente.

    Raises:
        HTTPException: 
            - 404: In caso l'utente associato a `user_id` è inesistente
            - 500: In caso di errore interno durante l’accesso al database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        cursor.execute("SELECT id FROM Users WHERE id= %s", (user_id,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code= 404, detail="Utente non trovato")
        
        query: str = """
            SELECT g.id, g.game_date, ug.player_role, g.is_terminated, ug.is_won, ug.points
            FROM Games AS g
            JOIN UserGames AS ug ON g.id = ug.game_id
            WHERE ug.player_id = %s
            ORDER BY g.game_date DESC, g.id DESC
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()

        if not result:
            return UserGames(
                user_id=user_id,
                user_games=[]
            )

        games: List[Game] = []

        query = """
            DELETE FROM UserGames 
            WHERE game_id = %s AND player_role = %s
        """
        
        for game_id, game_date, player_role, is_terminated, is_won, points in result:
            if player_role == "judge" and not is_terminated:
                cursor.execute(query, (game_id, player_role))
            else:
                games.append(Game(
                    game_id=game_id,
                    player_role=player_role,
                    data=game_date,
                    is_terminated=is_terminated,
                    is_won=is_won,
                    points=points
                ))
        connection.commit()

        return UserGames(
                user_id=user_id,
                user_games=games
            )

    except mariadb.Error:
        raise HTTPException(
            status_code=500,
            detail="Errore del server durante il recupero delle partite dell'utente."
        )

    finally:
        close_cursor(cursor)
        close_connection(connection)