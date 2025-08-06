from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from models.participant_game import QADict
import mariadb
from typing import List
from fastapi import HTTPException

def insert_q_a_participant_api(game_id: int, qa_list: List[QADict]) -> None:
    """
    Inserisce una lista ordinata di domande e risposte nella tabella Q_A,
    associandole a una specifica partita (game_id).

    Ogni domanda è accompagnata dalla risposta, dai flag ai_question e ai_answer.
    L'ordine fornito nella lista viene mantenuto, e viene usato per assegnare question_id (1, 2, 3).

    Args:
        game_id (int): ID della partita alla quale associare le Q&A
        qa_list (List[QADict]): Lista di oggetti QADict contenenti le domande e metadati

    Raises:
        HTTPException: 
            - 400: Se la lista è vuota o non valida
            - 500: In caso di errore durante l'inserimento nel database
    """
    if not qa_list:
        raise HTTPException(status_code=400, detail="La lista delle domande è vuota.")
    
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = """
        INSERT INTO Q_A (
            game_id, question_id, question, answer, ai_question, ai_answer
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """

        for idx, qa in enumerate(qa_list, start=1):
            cursor.execute(query, (
                game_id,
                idx,
                qa.question,
                qa.answer,
                qa.ai_question,
                qa.ai_answer
            ))

        connection.commit()

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante l'inserimento dei dati: {e}"
        )
    finally:
        close_cursor(cursor)
        close_connection(connection)