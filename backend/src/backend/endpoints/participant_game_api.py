from fastapi import HTTPException
from models.participant_game import ParticipantGameOutput, QADict
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.insert_q_a_participant_api import insert_q_a_participant_api
from utility.ai_utils import get_ai_answer, parse_ai_questions
from utility.participant_functions import generate_ai_questions, select_unique_questions_from_db, build_qa_list
import mariadb
from typing import List, Tuple
import random
from rapidfuzz import fuzz

def participant_game_api(game_id: int) -> ParticipantGameOutput:
    """
    Gestisce la logica della modalità participant.
    Recupera o genera domande da mostrare al partecipante della partita identificata da game_id.

    La logica prevede:
    - verifica validità della partita
    - generazione casuale di domande tramite AI o recupero da DB
    - verifica unicità semantica delle domande (con filtro fuzzy)
    - inserimento delle domande nel database

    Args:
        game_id (int): Identificativo della partita

    Returns:
        ParticipantGameOutput: Output contenente le 3 domande generate o recuperate
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id FROM Games WHERE id = %s AND terminated = FALSE"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Partita non trovata o già terminata.")
        
        use_ai: bool = random.choice([True, False])

        if use_ai:
            questions, flags = generate_ai_questions()
        
        else:
            questions, flags = select_unique_questions_from_db(cursor)

            if len(questions) < 3:
                # Fallback se il DB non ha abbastanza domande distinte
                questions, flags = generate_ai_questions()
        
        # Costruzione e inserimento nel database
        qa_list = build_qa_list(questions, flags)
        insert_q_a_participant_api(game_id, qa_list)

        return ParticipantGameOutput(questions=questions)

    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail=f"Errore database: {e}")
    finally:
        close_cursor(cursor)
        close_connection(connection)
