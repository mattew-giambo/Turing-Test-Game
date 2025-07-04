from typing import List
from utility.get_ai_answer import get_ai_answer

def judge_game_api_ai(lista_domande_input: List[str]):
    risposte_lista_output: List[str] = []
    for domanda_input in lista_domande_input:
        risposta = get_ai_answer(domanda_input)
        if risposta is not None:
            risposte_lista_output.append(risposta)
    return risposte_lista_output