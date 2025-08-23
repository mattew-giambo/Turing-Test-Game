from typing import List
from utility.ai.ai_utils import get_ai_answer

def judge_game_api_ai(questions_input: List[str]) -> List[str]:
    """
    Genera un set di risposte utilizzando un modello AI, dato un elenco di domande.

    Ogni domanda viene trasformata in un prompt personalizzato per simulare 
    una risposta realistica e colloquiale in un contesto da quiz televisivo.
    Il prompt viene poi inviato al motore AI tramite la funzione `get_ai_answer()`.

    Args:
        questions_input (List[str]): Lista di domande fornite dal giudice.

    Returns:
        List[str]: Lista di risposte generate dall'AI, una per ogni domanda.
    """
    answers_output: List[str] = []

    for question in questions_input:
        prompt = (
            f"Sei un concorrente di un quiz televisivo. Rispondi alla domanda: {question}.\n"
            "La risposta deve essere naturale, colloquiale e breve (1-2 frasi massimo).\n"
            "Evita esclamazioni, introduzioni o commenti extra.\n"
            "Scrivi solo la risposta."
        )
        
        ai_answer: str | None = get_ai_answer(prompt)

        if ai_answer:
            answers_output.append(ai_answer)
            
    return answers_output