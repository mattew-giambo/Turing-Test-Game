import mariadb
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from typing import List, Dict
from rapidfuzz import process, fuzz
import random
from utility.ai_utils import get_ai_answer

def judge_game_api_db(questions_input: List[str]) -> List[str]:
    """
    Recupera risposte umane esistenti dal database usando fuzzy matching sulle domande.
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

        seen_ids = set()
        for question_input in questions_input:
            q_fuzzy = {question_input: []}

            # Fuzzy matching con domande esistenti
            result_fuzz = process.extract(question_input, questions_db, scorer=fuzz.token_sort_ratio, limit= 10)
            if result_fuzz:
                for match, score, index in result_fuzz:
                    if score >= 50 and index not in seen_ids:
                        seen_ids.add(index) # per evitare di usare la stessa domanda+risposta
                        q_fuzzy[question_input].append(qa_list[index])
                questions_fuzzy.append(q_fuzzy)
            else:
                return []

        for q_fuzzy in questions_fuzzy:
            question_input = list(q_fuzzy.keys())[0] # question_input è l'unica chiave
            lista_domande_risposta = q_fuzzy[question_input]

            prompt = (
                "Ti darò una domanda e una lista di risposte. "
                "Scegli la risposta migliore per la domanda fornita.\n"
                "Rispondi solo con il numero corrispondente (ad esempio '1').\n"
                "Se nessuna risposta è adeguata, rispondi '0'.\n"
                f"Domanda: {question_input}\n"
            )
            for idx, qa in enumerate(lista_domande_risposta, start= 1):
                prompt+=f"{idx}. {qa['answer']}\n"

            print(prompt)
            ai_answer: str = get_ai_answer(prompt)
            try:
                answer_idx = int(ai_answer)
                if answer_idx == 0:
                    raise ValueError(f"Nessuna risposta adeguata")
                if 1 <= answer_idx and answer_idx <= len(lista_domande_risposta):
                    answers_fuzzy.append(lista_domande_risposta[answer_idx - 1]["answer"])
                else:
                    raise ValueError(f"Indice fuori dal range {answer_idx}")
            except ValueError as e:
                print(e)
                return []
            
        return answers_fuzzy
    finally:
        close_cursor(cursor)
        close_connection(connection)