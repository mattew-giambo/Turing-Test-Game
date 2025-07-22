from typing import List
from utility.ai_utils import get_ai_answer

def judge_game_api_ai(questions_input: List[str]) -> List[str]:
    """
    Genera risposte alle domande tramite AI.
    """
    answers_output: List[str] = []
    for question in questions_input:
        ai_answer = get_ai_answer(question)
        if ai_answer:
            answers_output.append(ai_answer)
    return answers_output