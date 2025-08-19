from fastapi import HTTPException
from models.judge_game import JudgeGameInput, JudgeGameOutput
from utility.game.judge_game_api_ai import judge_game_api_ai
from utility.game.judge_game_api_db import judge_game_api_db
from utility.db.insert_q_a_judge_api import insert_q_a_judge_api
from utility.db.connect_to_database import connect_to_database
from utility.db.close_connection import close_connection
from utility.db.get_cursor import get_cursor
from utility.db.close_cursor import close_cursor
from typing import List
import mariadb
import random

def judge_game_api(payload: JudgeGameInput, game_id: int) -> JudgeGameOutput:
    """
    Endpoint per la modalità Giudice del gioco. A partire da una lista di domande 
    fornite dal giudice, tenta di ottenere risposte da utenti precedenti nel database 
    (tramite fuzzy matching), oppure le genera tramite AI. Le domande e risposte vengono
    poi salvate nella tabella Q_A associate al game_id.

    Args:
        payload (JudgeGameInput): Input contenente la lista di domande del giudice.
        game_id (int): Identificativo univoco della partita in corso.

    Returns:
        JudgeGameOutput: Lista delle risposte generate o recuperate.

    Raises:
        HTTPException:
            - 404: se il game_id non corrisponde a una partita esistente.
            - 403: se la partita è già terminata.
            - 500: in caso di errore nel database o risposta non valida da AI.
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

        insert_q_a_judge_api(game_id, use_ai, questions_input, answers_output)
        return JudgeGameOutput(answers_list=answers_output)
    
    except mariadb.Error as e:
        raise HTTPException(
            status_code=500, 
            detail="Errore del server nella gestione della partita"
            )

    finally:
        close_cursor(cursor)
        close_connection(connection)