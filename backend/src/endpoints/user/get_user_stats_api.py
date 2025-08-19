from fastapi import HTTPException
import mariadb

from models.user_stats import UserStats
from utility.db.connect_to_database import connect_to_database
from utility.db.get_cursor import get_cursor
from utility.db.close_cursor import close_cursor
from utility.db.close_connection import close_connection

def get_user_stats_api(user_id: int) -> UserStats:
    """
    Recupera le statistiche di gioco di un utente specifico, includendo:
    - numero totale di partite giocate
    - partite giocate come giudice e partecipante
    - punteggi totali per ciascun ruolo
    - vittorie e sconfitte per ciascun ruolo

    Args:
        user_id (int): Identificativo univoco dell'utente.

    Returns:
        UserStats: Oggetto contenente tutte le statistiche aggregate.

    Raises:
        HTTPException: 
            - 404: Se l'utente associato a `user_id` è inesistente.
            - 500: In caso di errore interno durante l’accesso al database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = """
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
        
        # Calcolo delle partite giocate come partecipante e come giudice
        n_games_part: int = result[4] + result[6]
        n_games_judge: int = result[5] + result[7]
        
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