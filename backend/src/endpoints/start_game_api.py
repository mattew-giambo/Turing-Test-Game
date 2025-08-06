from fastapi import HTTPException
from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from typing import Literal


def start_game_api(payload: PlayerInfo) -> ConfirmGame:
    """
    Avvia una nuova partita assegnando il ruolo (judge o participant) a un utente esistente.

    Args:
        payload (PlayerInfo): Oggetto contenente l'ID dell'utente e il suo ruolo nella partita.

    Returns:
        ConfirmGame: Oggetto con i dettagli della partita appena creata.
    
    Raises:
        HTTPException: 404 se l'utente non esiste,
                       500 se si verifica un errore a livello di database.
    """
    player_id: int = payload.player_id
    player_role: Literal['judge', 'participant'] = payload.player_role

    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT user_name FROM Users WHERE id = %s"
        cursor.execute(query, (player_id,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code= 404, detail= "Utente non trovato.")

        player_name: str = result[0]
    
        cursor.execute("INSERT INTO Games () VALUES ()")
        game_id: int = cursor.lastrowid

        query = """
            INSERT INTO UserGames (game_id, player_id, player_role)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (game_id, player_id, player_role))
        connection.commit()

        return ConfirmGame(
            game_id=game_id,
            player_id=player_id,
            player_name=player_name,
            player_role=player_role
        )

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Errore del server durante la creazione della partita: {e}"
        )

    finally:
        close_cursor(cursor)
        close_connection(connection)
