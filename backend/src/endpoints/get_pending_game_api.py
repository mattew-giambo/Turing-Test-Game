from fastapi import HTTPException

from models.pending_game import QA, GameReviewOutput
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor

import mariadb
from typing import Dict

def get_pending_game_api(game_id: int) -> GameReviewOutput:
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id FROM Games WHERE id = %s AND is_terminated = FALSE"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Partita non trovata o già terminata.")

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