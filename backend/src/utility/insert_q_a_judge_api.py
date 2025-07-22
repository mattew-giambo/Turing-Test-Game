from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from typing import List
from fastapi import HTTPException

def insert_q_a_judge_api(game_id: int, is_ai: bool, questions_input: List[str], answers_output: List[str]):
    """
    Inserisce le domande e le risposte nel database Q_A per una data partita.

    Args:
        game_id (int): Identificativo della partita.
        is_ai (bool): Flag che indica se le risposte sono state generate da AI.
        questions_input (List[str]): Lista delle domande poste.
        answers_output (List[str]): Lista delle risposte generate.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "INSERT INTO Q_A (game_id, question_id, question, answer, ai_answer) VALUES (%s, %s, %s, %s, %s)"
        for q_id, (question, answer) in enumerate(zip(questions_input, answers_output), start=1):
            cursor.execute(query, (game_id, q_id, question, answer, is_ai))
        connection.commit()
    except mariadb.Error:
        raise HTTPException(status_code=500, detail="Errore durante il salvataggio delle risposte")
    finally:
        close_cursor(cursor)
        close_connection(connection)
        