from typing import List
from utility.ai_utils import get_ai_answer

def judge_game_api_ai(lista_domande_input: List[str]):
    lista_risposte_output: List[str] = []
    for domanda_input in lista_domande_input:
        risposta = get_ai_answer(domanda_input)
        if risposta is not None:
            lista_risposte_output.append(risposta)
    return lista_risposte_output