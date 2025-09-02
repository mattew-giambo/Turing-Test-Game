from fastapi import HTTPException

from models.verdict_game import QA, GameReviewOutput
from utility.db.close_connection import close_connection
from utility.db.close_cursor import close_cursor
from utility.db.connect_to_database import connect_to_database
from utility.db.get_cursor import get_cursor

import mariadb
from typing import Dict

def get_verdict_game_api(game_id: int) -> GameReviewOutput:
    """
    Recupera la sessione di gioco associata a una partita pendente specificata dal suo ID.

    La funzione verifica l'esistenza e lo stato della partita, quindi estrae tutte le domande e risposte
    associate, ordinandole per question_id, e le restituisce come dizionario indicizzato.

    Args:
        game_id (int): Identificativo univoco della partita pendente.

    Returns:
        GameReviewOutput: Modello contenente l'ID della partita e la sessione di gioco completa.

    Raises:
        HTTPException:
            - 404 se la partita non esiste o non contiene sessioni valide.
            - 403 se la partita è già terminata.
            - 500 per errori di accesso al database o problemi imprevisti.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id, is_terminated FROM Games WHERE id = %s"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Partita non trovata")
        if result[1] is True:
            raise HTTPException(status_code=403, detail="Partita già terminata")
        
        query = """
            SELECT question_id, question, answer
            FROM Q_A
            WHERE game_id = %s
            ORDER BY question_id
        """
        cursor.execute(query, (game_id,))
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="Nessuna sessione trovata per questa partita")
        
        session: Dict[int, QA] = {
            question_id: QA(question=question, answer=answer)
            for question_id, question, answer in result
        }

        return GameReviewOutput(game_id=game_id, session=session)

    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail=f"Errore durante il recupero della sessione: {e}")

    finally:
        close_cursor(cursor)
        close_connection(connection)