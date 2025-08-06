from fastapi import HTTPException
import mariadb
from models.game_info import GameInfoInput, GameInfoOutput
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor

def game_info_api(payload: GameInfoInput) -> GameInfoOutput:
    """
    Recupera le informazioni essenziali su una partita specifica a cui ha partecipato un determinato giocatore.
    Verifica che la partita esista e che il giocatore sia effettivamente associato ad essa.

    Args:
        payload (GameInfoInput): Oggetto contenente l'ID del giocatore e l'ID della partita.

    Returns:
        GameInfoOutput: Dettagli della partita per il giocatore indicato.

    Raises:
        HTTPException: 
            - 404: Se la partita non esiste o non è associata al giocatore.
            - 500: In caso di errore interno durante l’accesso al database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)
    
    player_id: int = payload.player_id
    game_id: int = payload.game_id

    try:
        query: str = """
            SELECT g.id, g.game_date, g.is_terminated, ug.player_id, ug.player_role, ug.is_won
            FROM Games AS g
            JOIN UserGames AS ug ON g.id = ug.game_id
            WHERE g.id = %s AND ug.player_id = %s
        """
        cursor.execute(query, (game_id, player_id))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Nessuna partita trovata con questo ID per questo giocatore."
            )

        return GameInfoOutput(
            game_id=result[0],
            data=result[1],
            is_terminated=result[2],
            player_id=result[3],
            player_role=result[4],
            is_won= result[5]
        )

    except mariadb.Error:
        raise HTTPException(
            status_code=500,
            detail="Errore del server durante il recupero delle informazioni sulla partita."
        )

    finally:
        close_cursor(cursor)
        close_connection(connection)