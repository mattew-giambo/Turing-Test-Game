from fastapi import HTTPException
import mariadb
from models.game_info import GameInfoInput, GameInfoOutput
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor

def game_info_api(payload: GameInfoInput):
    """
    Restituisce le informazioni dettagliate su una partita specifica,
    identificata tramite game_id e player_id. Utilizzato per visualizzare
    il contesto di una sessione di gioco (ruolo, data, stato, ecc.).

    Args:
        payload (GameInfoInput): Oggetto contenente player_id e game_id.

    Returns:
        GameInfoOutput: Oggetto contenente le informazioni della partita.

    Raises:
        HTTPException: Se la partita non esiste o non appartiene all'utente specificato.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)
    
    player_id = payload.player_id
    game_id = payload.game_id

    try:
        query: str = """
            SELECT g.id, g.date, g.terminated, ug.player_id, ug.player_role
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
            terminated=result[2],
            player_id=result[3],
            player_role=result[4]
        )

    except mariadb.Error:
        raise HTTPException(
            status_code=500,
            detail="Errore del server durante il recupero delle informazioni sulla partita."
        )

    finally:
        close_cursor(cursor)
        close_connection(connection)