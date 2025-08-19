import mariadb
from utility.db.close_connection import close_connection
from utility.db.close_cursor import close_cursor
from utility.db.connect_to_database import connect_to_database
from utility.db.get_cursor import get_cursor
from utility.ai_utils import get_ai_answer
from typing import List, Dict
from rapidfuzz import process, fuzz
import random


def judge_game_api_db(questions_input: List[str]) -> List[str]:
    """
    Recupera dal database domande e risposte non generate da AI, esegue
    un fuzzy matching tra domande input e domande salvate, e seleziona
    tramite AI la risposta migliore per ciascuna domanda input.

    Args:
        questions_input (List[str]): Lista di domande fornite dal client (giudice).

    Returns:
        List[str]: Lista di risposte selezionate dall'AI corrispondenti alle domande input. Lista vuota se non si trovano corrispondenze o in caso di errore.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT question, answer FROM Q_A WHERE ai_answer = FALSE"
        cursor.execute(query)
        result = cursor.fetchall()

        qa_list = [{"question": q, "answer": a} for q, a in result]
        random.shuffle(qa_list)

        questions_db = [qa["question"] for qa in qa_list]

        answers_fuzzy: List[str] = []
        questions_fuzzy: List[Dict[str, List[Dict[str, str]]]] = []

        seen_indices = set() # per evitare di usare la stessa domanda+risposta

        for question_input in questions_input:
            q_fuzzy = {question_input: []}
            matches = process.extract(
                question_input,
                questions_db,
                scorer=fuzz.token_sort_ratio,
                limit=10
            )

            if not matches:
                return []
            
            for match, score, index in matches:
                if score >= 50 and index not in seen_indices:
                    seen_indices.add(index)
                    q_fuzzy[question_input].append(qa_list[index])

            questions_fuzzy.append(q_fuzzy)

        for q_fuzzy in questions_fuzzy:
            question_input = next(iter(q_fuzzy)) # question_input è l'unica chiave
            candidate_answers = q_fuzzy[question_input]

            prompt = (
                "Sei l'autore di un gioco a quiz.\n"
                "Ti fornirò una domanda e una lista di risposte.\n"
                "Le risposte possono essere corrette, parzialmente pertinenti o completamente sbagliate.\n"
                "Analizza attentamente il significato di ogni risposta e scegli quella che risponde meglio alla domanda.\n"
                "Rispondi SOLO con il numero della risposta scelta (es. '1').\n"
                "Se nessuna risposta è adeguata, scrivi '0'.\n"
                f"\nDOMANDA:\n{question_input}\n\nRISPOSTE:\n"
                + "\n".join(f"{idx}. {qa['answer']}" for idx, qa in enumerate(candidate_answers, start=1))

            )

            ai_answer: str = get_ai_answer(prompt)

            try:
                answer_idx = int(ai_answer)
                if answer_idx == 0:
                    raise ValueError("Nessuna risposta adeguata selezionata dall'AI")
                if 1 <= answer_idx <= len(candidate_answers):
                    answers_fuzzy.append(candidate_answers[answer_idx - 1]["answer"])
                else:
                    raise ValueError(f"Indice risposta AI fuori range: {answer_idx}")
            except (ValueError, TypeError) as e:
                print(f"Errore interpretazione risposta AI: {e}")
                return []
            
        return answers_fuzzy
    finally:
        close_cursor(cursor)
        close_connection(connection)