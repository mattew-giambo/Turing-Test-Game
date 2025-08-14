from fastapi import HTTPException
import requests
from config.constants import OLLAMA_CHAT_URL, MODEL
from models.ollama import OllamaInput, OllamaMessage
from typing import List, Optional, Dict

def get_ai_answer(prompt: str) -> Optional[str]:
    """
    Invia un prompt al modello AI Ollama e ritorna la risposta testuale.

    Args:
        prompt (str): Prompt testuale da inviare all'AI.

    Returns:
        Optional[str]: Testo della risposta AI, None se errore o risposta non valida.
    """
    message = OllamaMessage(role= "user", content= prompt)
    ollama_input = OllamaInput(model= MODEL, messages= [message], stream= False)

    try:
        response = requests.post(OLLAMA_CHAT_URL, json= ollama_input.model_dump())
        response.raise_for_status()
        result: Dict = response.json()
    except requests.RequestException as e:
        print(f"Errore nella chiamata API Ollama: {e}")
        return None
    
    answer: Optional[str] = result.get("message", {}).get("content")
    return answer

def parse_ai_questions(answer: str) -> List[str]:
    """
    Estrae una lista di domande numerate da una risposta testuale generata dall'AI.

    L'AI genera esattamente tre domande numerate da 1 a 3, separate da linee.
    Questa funzione estrae solo il testo delle domande, rimuovendo la numerazione.

    Args:
        answer (str): Testo generato dall'AI contenente le domande numerate.

    Returns:
        List[str]: Lista di domande pulite; lista vuota se input mancante o malformato.
    """
    if not answer or not isinstance(answer, str):
        return []

    lines: List[str] = [line.strip() for line in answer.split("\n") if line.strip()]
    questions: List[str] = []

    for line in lines:
        if "." in line:
            try:
                # Divide alla prima occorrenza del punto per isolare la domanda
                numero, domanda = line.split(".", 1)
                domanda = domanda.strip()
                if domanda:
                    questions.append(domanda)
            except ValueError:
                # Linea malformata, si ignora in modo silenzioso
                continue

    return questions
