from fastapi import HTTPException
from models.participant_game import QADict
from utility.ai_utils import get_ai_answer, parse_ai_questions
import mariadb
from typing import List, Tuple
import random
from rapidfuzz import fuzz

def generate_ai_questions() -> Tuple[List[str], List[bool]]:
    """
    Genera 3 domande utilizzando il modello AI.

    Returns:
        Tuple[List[str], List[bool]]: Le domande generate e i flag ai_question=True

    Raises:
        HTTPException: se la generazione non produce abbastanza domande
    """
    prompt: str = "Genera tre domande semplici e naturali, ciascuna su un argomento diverso. " \
        "Scegli liberamente argomenti comuni che possano emergere in una conversazione informale tra persone. " \
        "Evita domande tecniche, difficili o filosofiche. " \
        "Non aggiungere introduzioni, commenti, spiegazioni o riferimenti al motivo per cui le domande sono state generate. " \
        "Restituisci solo le tre domande, numerate da 1 a 3."
    
    ai_answer: str = get_ai_answer(prompt)
    questions: List[str] = parse_ai_questions(ai_answer)

    if len(questions) < 3:
        raise HTTPException(status_code=500, detail="AI: domande generate insufficienti.")

    flags = [True] * len(questions)
    return questions, flags

def select_unique_questions_from_db(cursor: mariadb.Cursor) -> Tuple[List[str], List[bool]]:
    """
    Recupera domande esistenti nel DB, evitando ripetizioni tramite fuzzy matching.

    Returns:
        Tuple[List[str], List[bool]]: Domande selezionate e relativi flag AI associati
    """
    cursor.execute("SELECT DISTINCT question, ai_question FROM Q_A")
    result = cursor.fetchall()

    if not result:
        return [], []

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

    return selected_questions, selected_flags

def build_qa_list(questions: List[str], flags: List[bool]) -> List[QADict]:
    """
    Costruisce oggetti QADict da domande e flag associati.

    Args:
        questions (List[str]): Domande
        flags (List[bool]): Flag ai_question

    Returns:
        List[QADict]: Lista pronta da inserire nel DB
    """
    return [
        QADict(
            question=q,
            answer="",
            ai_question=flag,
            ai_answer=False
        ) for q, flag in zip(questions, flags)
    ]
