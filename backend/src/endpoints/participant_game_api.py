from typing import List
from fastapi import HTTPException
from models.participant_game import ParticipantGameOutput, QADict
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.insert_q_a_participant_api import insert_q_a_participant_api
from utility.participant_functions import generate_ai_questions, select_unique_questions_from_db, build_qa_list
import mariadb
import random

from config.constants import NUM_QUESTIONS_PER_GAME

def participant_game_api(game_id: int) -> ParticipantGameOutput:
    """
    Gestisce la modalità 'participant' del gioco.

    A partire dal game_id fornito:
    - verifica che la partita esista e non sia già terminata
    - genera o recupera 3 domande (via AI o da database)
    - garantisce che le domande siano semanticamente distinte (via filtro fuzzy)
    - salva le domande nel database con i relativi flag AI

    Args:
        game_id (int): Identificativo univoco della partita.

    Returns:
        ParticipantGameOutput: Modello contenente la lista delle domande per il partecipante.

    Raises:
        HTTPException:
            - 404: Se la partita non esiste.
            - 403: Se la partita è già terminata.
            - 500: In caso di errore nella comunicazione con il database.
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
        
        use_ai: bool = random.choice([True, False])

        questions: List[str] = []
        flags: List[bool] = []

        if not use_ai:
            questions, flags = select_unique_questions_from_db(cursor)

        if use_ai or len(questions) < NUM_QUESTIONS_PER_GAME:
            questions, flags = generate_ai_questions()

            if len(questions) != NUM_QUESTIONS_PER_GAME:
                raise HTTPException(status_code=500, detail="Errore durante la generazione delle domande AI")

            use_ai = True
        
        qa_list: List[QADict] = build_qa_list(questions, flags)
        insert_q_a_participant_api(game_id, qa_list)

        return ParticipantGameOutput(questions=questions)

    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail=f"Errore database: {e}")
    
    finally:
        close_cursor(cursor)
        close_connection(connection)
