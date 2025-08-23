from fastapi import HTTPException
from models.participant_game import QADict
from utility.ai.ai_utils import get_ai_answer, parse_ai_questions
import mariadb
from typing import List, Tuple
import random
from rapidfuzz import fuzz

from config.constants import NUM_QUESTIONS_PER_GAME

def generate_ai_questions() -> Tuple[List[str], List[bool]]:
    """
    Genera tre domande testuali simulate da un'intelligenza artificiale per il ruolo di 'partecipante'.

    Utilizza un prompt testuale specifico per ottenere tre domande colloquiali e informali.
    Il risultato è elaborato e convertito in una lista di stringhe e una lista di flag associati.

    Returns:
        Tuple[List[str], List[bool]]:
            - Lista delle domande generate.
            - Lista di booleani che indicano che ogni domanda è stata generata dall'AI.

    Raises:
        HTTPException: 
            - 500: Se l'AI non restituisce un numero sufficiente di domande.
    """
    prompt = (
        "Sei l'autore di un quiz show (programma televisivo). Devo scrivere tre domande da porre ai concorrenti durante una sessione di gioco.\n"
        "Scegli tre argomenti distinti che possono emergere in una conversazione informale tra persone. Per ciascun argomento, formula una domanda in tono naturale e colloquiale.\n"
        "Evita domande tecniche, filosofiche o troppo complesse. Niente introduzioni, spiegazioni o commenti.\n"
        "Restituisci solo le tre domande, numerate da 1 a 3."
    )
    
    ai_answer: str = get_ai_answer(prompt)
    questions: List[str] = parse_ai_questions(ai_answer)

    if len(questions) < NUM_QUESTIONS_PER_GAME:
        raise HTTPException(status_code=500, detail="AI: domande generate insufficienti.")

    flags = [True] * NUM_QUESTIONS_PER_GAME
    return questions, flags

def select_unique_questions_from_db(cursor: mariadb.Cursor) -> Tuple[List[str], List[bool]]:
    """
    Seleziona fino a tre domande distinte e già presenti nel database, evitando domande troppo simili.

    Le domande sono considerate distinte se la similarità testuale (misurata con token_sort_ratio) è inferiore all'85%.
    L’ordine delle domande è casuale.

    Args:
        cursor (mariadb.Cursor): Cursore attivo collegato al database Q_A.

    Returns:
        Tuple[List[str], List[bool]]:
            - Lista di domande distinte selezionate.
            - Lista di flag che indicano se la domanda era stata generata dall’AI.
    """
    cursor.execute("SELECT DISTINCT question, ai_question FROM Q_A")
    result = cursor.fetchall()

    if not result:
        return [], []

    all_questions: List[Tuple[str, bool]] = [(row[0].strip(), row[1]) for row in result]
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

        if len(selected_questions) == NUM_QUESTIONS_PER_GAME:
            break # abbiamo trovato abbastanza domande distinte

    return selected_questions, selected_flags

def build_qa_list(questions: List[str], flags: List[bool]) -> List[QADict]:
    """
    Costruisce una lista di oggetti QADict a partire da domande e relativi flag AI.

    Ogni elemento QADict è inizialmente senza risposta (`answer = ""`) e con `ai_answer = False`.

    Args:
        questions (List[str]): Lista di domande da includere nella sessione.
        flags (List[bool]): Lista di flag che indicano se la domanda è stata generata dall'AI.

    Returns:
        List[QADict]: Lista di oggetti QADict pronti per essere inseriti nel database.
    """
    return [
        QADict(
            question=q,
            answer="",
            ai_question=flag,
            ai_answer=False
        ) for q, flag in zip(questions, flags)
    ]
