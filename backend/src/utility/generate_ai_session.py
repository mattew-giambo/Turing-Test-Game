from typing import List, Dict
from fastapi import HTTPException
from rapidfuzz import fuzz
import random
import mariadb

from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from models.pending_game import QA
from utility.ai_utils import get_ai_answer, parse_ai_questions

def generate_full_ai_session(user_id: int) -> Dict[str, int | Dict[int, QA]]:
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "INSERT INTO Games () VALUES ()"
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
            ai_answer: str = get_ai_answer(flag_judge=False)
            selected_questions: List[str] = parse_ai_questions(ai_answer)

            if len(selected_questions) < 3:
                raise HTTPException(status_code=500, detail="L'AI non ha generato abbastanza domande")
            
            ai_flags: List[bool] = [True] * len(selected_questions)
        
        else:
            # 4. Filtra domande con fuzzy match
            all_questions = [(elem[0].strip(), elem[1]) for elem in result]
            random.shuffle(all_questions)

            selected_questions: List[str] = []
            ai_flags: List[bool] = []

            for question, flag in all_questions:
                is_distinct = True # supponiamo che la domanda sia valida

                for existing in selected_questions:
                    similarity = fuzz.token_sort_ratio(question.lower(), existing.lower())

                    if similarity >= 85:
                        is_distinct = False # troppo simile a una domanda già presente
                        break # non serve continuare a confrontare con le altre

                if is_distinct:
                    selected_questions.append(question)
                    ai_flags.append(flag)

                if len(selected_questions) == 3:
                    break # abbiamo trovato abbastanza domande distinte

            # Se meno di 3 domande distinte, fallback all’AI
            if len(selected_questions) < 3:
                ai_answer: str = get_ai_answer(flag_judge=False)
                selected_questions: List[str] = parse_ai_questions(ai_answer)

                if len(selected_questions) < 3:
                    raise HTTPException(status_code=500, detail="AI fallback fallito: domande insufficienti.")
                
                ai_flags = [True] * len(selected_questions)

        # 5. Ottieni risposte AI
        risposte_ai: List[str] = []
        for question in selected_questions:
            risposta_ai = get_ai_answer(question=question, flag_judge=True)
            if not risposta_ai:
                raise HTTPException(status_code=500, detail="Errore nella risposta dell'AI")
            risposte_ai.append(risposta_ai.strip())

        # 6. Inserisci triple domanda-risposta nella Q_A
        query = """
        INSERT INTO Q_A (game_id, question_id, question, answer, ai_question, ai_answer)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        for idx, (question, answer, ai_flag) in enumerate(zip(selected_questions, risposte_ai, ai_flags), start=1):
            cursor.execute(query, (
                game_id,
                idx,
                question,
                answer,
                ai_flag,
                True  # le risposte sono sempre generate dall'AI
            ))

        connection.commit()

        # 7. Costruisce dizionario sessione con gli oggetti QA
        session_data: Dict[int, QA] = {
            idx: QA(question=question, answer=answer)
            for idx, (question, answer) in enumerate(zip(selected_questions, risposte_ai), start=1)
        }

        return {
            "game_id": game_id,
            "session": session_data
        }

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Errore DB: {e}")
    finally:
        close_cursor(cursor)
        close_connection(connection)