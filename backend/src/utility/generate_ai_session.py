from typing import List, Dict
from fastapi import HTTPException
from rapidfuzz import process, fuzz
import random
import mariadb

from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from models.pending_game import GameReviewOutput, QA
from utility.ai_utils import get_ai_answer, parse_ai_questions

def generate_full_ai_session(user_id: int) -> GameReviewOutput:
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "INSERT INTO Games (terminated) VALUES (FALSE)"
        # 1. Crea una nuova partita 
        cursor.execute(query)
        game_id: int = cursor.lastrowid

        # 2. Inserisce nella UserGames: utente come judge, AI (id=1) come participant
        query = "INSERT INTO UserGames (game_id, player_id, player_role) VALUES (%s, %s, 'judge')"
        cursor.execute(query, (game_id, user_id))

        query = "INSERT INTO UserGames (game_id, player_id, player_role) VALUES (%s, %s, 'participant')"
        cursor.execute(query, (game_id, 1))

        # 3. Recupera domande distinte dal DB
        query = "SELECT DISTINCT question, ai_question FROM Q_A"
        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="Nessuna domanda trovata nel database")

        questions = [q[0].strip() for q in result]
        random.shuffle(questions)

        # 4. Filtra domande con fuzzy match
        domande_distinte: List[str] = []
        ai_flags: List[bool] = []

        for question, flag in questions:
            add_question = True  # supponiamo che la domanda sia valida

            for esistente in domande_distinte:
                similarita = fuzz.token_sort_ratio(question.lower(), esistente.lower())

                if similarita >= 85:
                    add_question = False  # troppo simile a una domanda già presente
                    break  # non serve continuare a confrontare con le altre

            if add_question:
                domande_distinte.append(question)
                ai_flags.append(flag)

            if len(domande_distinte) == 3:
                break  # abbiamo trovato abbastanza domande distinte

        # Fallback: usa domande generate dall'AI se non ci sono abbastanza distinte
        if len(domande_distinte) < 3:
            answer = get_ai_answer(flag_judge=False)
            domande_distinte = parse_ai_questions(answer)
            ai_flags = [True] * len(domande_distinte)

        # 5. Ottieni risposte AI
        risposte_ai: List[str] = []
        for domanda in domande_distinte:
            risposta = get_ai_answer(question=domanda, flag_judge=True)
            if not risposta:
                raise HTTPException(status_code=500, detail="Errore nella risposta dell'AI")
            risposte_ai.append(risposta.strip())

        # 6. Inserisci triple domanda-risposta nella Q_A
        query = """
        INSERT INTO Q_A (game_id, question_id, question, answer, ai_question, ai_answer)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        for idx, (question, answer, ai_flag) in enumerate(zip(domande_distinte, risposte_ai, ai_flags), start=1):
            cursor.execute(query, (
                game_id,
                idx,
                question,
                answer,
                ai_flag,
                True  # le risposte sono sempre generate dall'AI
            ))

        connection.commit()

        # 7. Costruisci oggetto Pydantic per risposta
        session_data: Dict[int, QA] = {
            idx: QA(question=q, answer=a)
            for idx, (q, a) in enumerate(zip(domande_distinte, risposte_ai), start=1)
        }

        return GameReviewOutput(game_id=game_id, session=session_data)

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Errore DB: {e}")
    finally:
        close_cursor(cursor)
        close_connection(connection)