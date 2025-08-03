from fastapi import HTTPException
import mariadb
from models.user_stats import UserStats
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor

def get_user_stats_api(user_id: int) -> UserStats:
    """
    Recupera le statistiche di gioco associate a un determinato utente.

    Args:
        user_id (int): ID dell'utente di cui si vogliono ottenere le statistiche.

    Returns:
        UserStats: Oggetto contenente le statistiche complete dell'utente.

    Raises:
        HTTPException: 
            - 404: Se l'utente associato a `user_id` è inesistente.
            - 500: In caso di errore interno durante l’accesso al database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query = """
                SELECT user_id, n_games, score_part, score_judge, 
                    won_part, won_judge, lost_part, lost_judge
                FROM Stats
                WHERE user_id = %s
            """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(
                status_code= 404,
                detail= "Utente non trovato."
            )
        
        # Calcolo del numero di partite giocate come partecipante e come giudice
        n_games_part = result[4] + result[6]
        n_games_judge = result[5] + result[7]
        
        return UserStats(
                user_id=result[0],
                n_games=result[1],
                n_games_part=n_games_part,
                n_games_judge=n_games_judge,
                score_part=result[2],
                score_judge=result[3],
                won_part=result[4],
                won_judge=result[5],
                lost_part=result[6],
                lost_judge=result[7]
            )
    except mariadb.Error:
        raise HTTPException(
            status_code=500,
            detail="Errore del server durante il recupero delle statistiche."
        )

    finally:
        close_cursor(cursor)
        close_connection(connection)