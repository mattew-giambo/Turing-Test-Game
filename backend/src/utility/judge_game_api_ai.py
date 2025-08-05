from typing import List
from utility.ai_utils import get_ai_answer

def judge_game_api_ai(questions_input: List[str]) -> List[str]:
    """
    Genera risposte alle domande tramite AI.
    """
    answers_output: List[str] = []
    for question in questions_input:
        prompt = (
            f"Sei un concorrente di un quiz televisivo. Rispondi alla domanda: {question}.\n"
            "La risposta deve essere naturale, colloquiale e breve (1-2 frasi massimo).\n"
            "Evita esclamazioni, introduzioni, spiegazioni o commenti extra.\n"
            "Scrivi solo la risposta."
        )
        ai_answer = get_ai_answer(prompt)
        if ai_answer:
            answers_output.append(ai_answer)
    return answers_output