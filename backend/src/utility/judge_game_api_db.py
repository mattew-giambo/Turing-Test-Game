import mariadb
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from typing import List
from rapidfuzz import process, fuzz
import random

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

        answers_output: List[str] = []
        for question_input in questions_input:
            # Fuzzy matching con domande esistenti
            result_fuzz = process.extractOne(question_input, questions_db, scorer=fuzz.token_sort_ratio)
            if result_fuzz:
                match, score, index = result_fuzz
                if score >= 80:
                    answers_output.append(qa_list[index]["answer"])

        return answers_output
    finally:
        close_cursor(cursor)
        close_connection(connection)