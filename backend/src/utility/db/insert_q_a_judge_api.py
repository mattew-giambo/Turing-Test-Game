from utility.db.close_connection import close_connection
from utility.db.close_cursor import close_cursor
from utility.db.connect_to_database import connect_to_database
from utility.db.get_cursor import get_cursor
import mariadb
from typing import List
from fastapi import HTTPException

def insert_q_a_judge_api(game_id: int, is_ai: bool, questions_input: List[str], answers_output: List[str]) -> None:
    """
    Salva le coppie domanda-risposta della modalità Giudice nella tabella Q_A del database.

    Ogni coppia viene associata a un identificatore progressivo (question_id),
    al game_id corrente e a un flag che indica se la risposta è stata generata dall'AI.

    Args:
        game_id (int): Identificativo della partita.
        is_ai (bool): True se le risposte sono state generate dall'intelligenza artificiale.
        questions_input (List[str]): Lista delle domande fornite dal giudice.
        answers_output (List[str]): Lista delle risposte associate, in ordine.

    Raises:
        HTTPException:
            - 500: In caso di errore durante l'inserimento nel database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = """
            INSERT INTO Q_A (game_id, question_id, question, answer, ai_answer)
            VALUES (%s, %s, %s, %s, %s)
        """
        for question_id, (question, answer) in enumerate(zip(questions_input, answers_output), start=1):
            cursor.execute(query, (game_id, question_id, question, answer, is_ai))

        connection.commit()

    except mariadb.Error:
        raise HTTPException(status_code=500, detail="Errore durante il salvataggio delle domande e risposte")
    finally:
        close_cursor(cursor)
        close_connection(connection)
        