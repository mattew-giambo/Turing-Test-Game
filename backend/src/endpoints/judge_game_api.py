from fastapi import HTTPException
from models.judge_game import JudgeGameInput, JudgeGameOutput
from utility.judge_game_api_ai import judge_game_api_ai
from utility.judge_game_api_db import judge_game_api_db
from utility.insert_q_a_judge_api import insert_q_a_judge_api
from utility.connect_to_database import connect_to_database
from utility.close_connection import close_connection
from utility.get_cursor import get_cursor
from utility.close_cursor import close_cursor
from typing import List
import mariadb
import random

def judge_game_api(payload: JudgeGameInput, game_id: int) -> JudgeGameOutput:
    """
    Gestisce la generazione delle risposte per la modalità Giudice.
    A partire da una lista di domande fornite dall'utente, recupera risposte da altri utenti (se disponibili)
    o le genera tramite AI. Salva la sessione nel database Q_A.

    Args:
        payload (JudgeGameInput): Input contenente le domande del giudice.
        game_id (int): Identificativo della partita.

    Returns:
        JudgeGameOutput: Lista di risposte generate per le domande.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id, is_terminated FROM Games WHERE id = %s"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Partita non trovata")
        if result[1] is True:
            raise HTTPException(status_code=403, detail="Partita già terminata")

        questions_input: List[str] = payload.questions_list
        answers_output: List[str] = []

        use_ai: bool = random.choice([True, False])

        if not use_ai:
            answers_output = judge_game_api_db(questions_input)

        if use_ai or len(answers_output) != len(questions_input):
            answers_output = judge_game_api_ai(questions_input)
            if len(answers_output) != len(questions_input):
                raise HTTPException(status_code=500, detail="Errore del server")
            use_ai = True  
        
        if use_ai:
            try:
                query = "INSERT INTO UserGames(game_id, player_id, player_role) VALUES (%s, %s, %s)"
                cursor.execute(query,(game_id, 1, "participant"))
                connection.commit()
            except mariadb.Error:
                raise HTTPException(status_code= 500, detail= "Errore del server")

    except mariadb.Error as e:
        print(e)
        raise HTTPException(status_code=500, detail="Errore del server nella gestione della partita")

    finally:
        close_cursor(cursor)
        close_connection(connection)

    insert_q_a_judge_api(game_id, use_ai, questions_input, answers_output)

    return JudgeGameOutput(answers_list=answers_output)