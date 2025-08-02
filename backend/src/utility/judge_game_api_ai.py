from typing import List
from utility.ai_utils import get_ai_answer

def judge_game_api_ai(questions_input: List[str]) -> List[str]:
    """
    Genera risposte alle domande tramite AI.
    """
    answers_output: List[str] = []
    for question in questions_input:
        prompt: str = f"""Rispondi in modo naturale come se fossi un essere umano alla domanda: {question}
                    Scrivi solo la risposta, senza meta-commenti, spiegazioni o riferimenti alla domanda stessa.
                    Rispondi in modo emotivo e spontaneo, come in una vera conversazione tra due persone.
                    Non usare asterischi per indicare azioni o pensieri. 
                    La risposta deve essere breve, massimo 1-2 frasi."""
        ai_answer = get_ai_answer(prompt)
        if ai_answer:
            answers_output.append(ai_answer)
    return answers_output