from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from typing import List
from fastapi import HTTPException

def insert_q_a_judge_api(game_id: int, flag_ai: bool, lista_domande_input: List, lista_risposte_output: List):
    try:
        connection = connect_to_database()
        cursor = get_cursor(connection)
        for elem in zip(lista_domande_input, lista_risposte_output):
            cursor.execute(
                "INSERT INTO Q_A(game_id, question, answer, ai_answer) VALUES (%s, %s, %s, %s)",
                (game_id,) + elem + (flag_ai,)
            )
        connection.commit()
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore del server nell'esecuzione della query"
        )
    finally:
        close_cursor(cursor)
        close_connection(connection)
        