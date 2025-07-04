import requests
from config.constants import OLLAMA_CHAT_URL, MODEL
from models.ollama import OllamaInput, OllamaMessage
from typing import Union, Dict

def get_ai_answer(question: str) -> Union[None, str]:
    message = OllamaMessage(role= "user", content= question)
    ollama_input = OllamaInput(model= MODEL, messages= [message], stream= False)

    try:
        response = requests.post(OLLAMA_CHAT_URL, json= ollama_input.model_dump())
        response.raise_for_status()
        result: Dict = response.json()
    except requests.RequestException as e:
        print(f"Errore nella chiamata API: {e}")
        return None
    
    answer = result.get("message").get("content")
    return answer
