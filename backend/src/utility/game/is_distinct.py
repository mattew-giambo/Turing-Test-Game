from typing import List
from rapidfuzz import fuzz

def is_distinct(question: str, selected_questions: List[str], threshold: int = 85) -> bool:
        """
    Verifica se una nuova domanda è sufficientemente diversa dalle domande già selezionate,
    confrontando la similarità testuale tramite `token_sort_ratio` di RapidFuzz.

    Questa funzione è utile per evitare domande duplicate o troppo simili tra loro
    durante la generazione di contenuti di gioco.

    Args:
        question (str): Testo della nuova domanda da verificare.
        selected_questions (List[str]): Elenco delle domande già selezionate nella sessione di gioco.
        threshold (int, opzionale): Valore percentuale di similarità (0-100) oltre il quale
            la domanda viene considerata troppo simile. Default a 85.

    Returns:
        bool: 
            - True se la domanda è considerata distinta (similarità < threshold con tutte le altre).
            - False se la domanda è troppo simile ad almeno una già selezionata.
    """
        for existing in selected_questions:
            similarity = fuzz.token_sort_ratio(question.lower(), existing.lower())
            if similarity >= threshold:
                return False
        return True