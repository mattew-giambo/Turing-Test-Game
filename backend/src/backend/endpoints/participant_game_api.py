from fastapi import HTTPException
from models.participant_game import ParticipantGameOutput, QADict
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.insert_q_a_participant_api import insert_q_a_participant_api
from utility.ai_utils import get_ai_answer, parse_ai_questions
import mariadb
from typing import List
import random
from rapidfuzz import fuzz

def participant_game_api(game_id: int) -> ParticipantGameOutput:
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        # 1. Verifica validità della partita
        query:str = "SELECT id FROM Games WHERE id = %s AND terminated = FALSE"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Partita non trovata o già terminata.")
        
        # 2. Decide la fonte delle domande
        ai = random.choice([True, False])

        if ai:
            # 3A. Generazione AI
            ai_answer: str = get_ai_answer(flag_judge=False)
            ai_questions: List[str] = parse_ai_questions(ai_answer)

            if len(ai_questions) < 3:
                raise HTTPException(status_code=500, detail="L'AI non ha generato abbastanza domande")

            # Costruzione oggetti da inserire nel DB
            qa_list: List[QADict] = [
                QADict(
                    question=question,
                    answer="",
                    ai_question=True,
                    ai_answer=False
                ) for question in ai_questions
            ]

            insert_q_a_participant_api(game_id, qa_list)

            return ParticipantGameOutput(questions=ai_questions)
        
        else:
            # 3B. Domande dal DB
            cursor.execute("SELECT DISTINCT question, ai_question FROM Q_A")
            result = cursor.fetchall()

            # Se non ci sono abbastanza domande nel db le genera l'AI
            if not result:
                ai_answer: str = get_ai_answer(flag_judge=False)
                ai_questions: List[str] = parse_ai_questions(ai_answer)

                if len(ai_questions) < 3:
                    raise HTTPException(status_code=500, detail="AI fallback fallito: domande insufficienti.")

                qa_list: List[QADict] = [
                    QADict(
                        question=question,
                        answer="",
                        ai_question=True,
                        ai_answer=False
                    ) for question in ai_questions
                ]

                insert_q_a_participant_api(game_id, qa_list)

                return ParticipantGameOutput(questions=ai_questions)
            
            # Filtro fuzzy per domande distinte
            all_questions = [(elem[0].strip(), elem[1]) for elem in result]
            random.shuffle(all_questions)

            selected_questions: List[str] = []
            selected_flags: List[bool] = []

            for question, flag in all_questions:
                is_distinct = True # supponiamo che la domanda sia valida

                for existing in selected_questions:
                    similarity = fuzz.token_sort_ratio(question.lower(), existing.lower())

                    if similarity >= 85:
                        is_distinct = False # troppo simile a una domanda già presente
                        break # non serve continuare a confrontare con le altre

                if is_distinct:
                    selected_questions.append(question)
                    selected_flags.append(flag)

                if len(selected_questions) == 3:
                    break # abbiamo trovato abbastanza domande distinte

            # Se meno di 3 domande distinte, fallback all’AI
            if len(selected_questions) < 3:
                ai_answer: str = get_ai_answer(flag_judge=False)
                ai_questions: List[str] = parse_ai_questions(ai_answer)

                if len(ai_questions) < 3:
                    raise HTTPException(status_code=500, detail="AI fallback fallito: domande insufficienti.")
                
                qa_list: List[QADict] = [
                    QADict(
                        question=question,
                        answer="",
                        ai_question=True,
                        ai_answer=False
                    ) for question in ai_questions
                ]

                insert_q_a_participant_api(game_id, qa_list)

                return ParticipantGameOutput(questions=ai_questions)

            # Inserisce le 3 domande selezionate dal DB
            qa_list: List[QADict] = [
                QADict(
                    question=q,
                    answer="",
                    ai_question=flag,
                    ai_answer=False
                ) for q, flag in zip(selected_questions, selected_flags)
            ]

            insert_q_a_participant_api(game_id, qa_list)

            return ParticipantGameOutput(questions=selected_questions)

    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail=f"Errore database: {e}")
    finally:
            close_cursor(cursor)
            close_connection(connection)