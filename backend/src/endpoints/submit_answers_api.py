from typing import Optional
from fastapi import HTTPException
from models.participant_game import AnswerInput, ResponseSubmit
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb

def submit_answers_api(game_id: int, input_data: AnswerInput) -> ResponseSubmit:
    """
    Aggiorna le risposte fornite dal partecipante all'interno della tabella Q_A
    per una specifica partita, identificata tramite game_id.

    Args:
        game_id (int): ID della partita a cui sono associate le domande.
        input_data (AnswerInput): Oggetto contenente la lista delle risposte.

    Returns:
        ResponseSubmit: Oggetto che conferma l'avvenuto aggiornamento delle risposte.

    Raises:
        HTTPException: In caso di partita non trovata, già terminata, o errore di database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id, is_terminated FROM Games WHERE id = %s"
        cursor.execute(query, (game_id,))
        result: Optional[tuple] = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Partita non trovata")
        if result[1] is True:
            raise HTTPException(status_code=403, detail="Partita già terminata")

        query = """
        UPDATE Q_A
        SET answer = %s
        WHERE game_id = %s AND question_id = %s
        """

        for idx, answer in enumerate(input_data.answers, start=1):  
            cursor.execute(query, (answer.strip(), game_id, idx))

        connection.commit()
        return ResponseSubmit(status="ok")

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante l'aggiornamento delle risposte: {e}"
        )
    
    finally:
        close_cursor(cursor)
        close_connection(connection)