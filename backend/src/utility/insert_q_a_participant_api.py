from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from typing import List
from fastapi import HTTPException

def insert_q_a_participant_api(game_id: int, questions: List[str], ai_question: bool, ai_answer: bool):
    try:
        connection: mariadb.Connection = connect_to_database()
        cursor: mariadb.Cursor = get_cursor(connection)

        query: str = "INSERT INTO Q_A (game_id, question_id, question, answer, ai_question, ai_answer) VALUES (%s, %s, %s, %s, %s, %s)"
        for idx, question in enumerate(questions, start=1):
            cursor.execute(query, (
                game_id,
                idx,
                question,
                "",
                ai_question,
                ai_answer
            ))
        connection.commit()
    except mariadb.Error as db_error:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante l'aggiunta dei dati: {db_error}"
        )
    finally:
        close_cursor(cursor)
        close_connection(connection)