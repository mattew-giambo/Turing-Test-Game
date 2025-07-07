import requests
from config.constants import OLLAMA_CHAT_URL, MODEL
from models.ollama import OllamaInput, OllamaMessage
from typing import Union, Dict

def get_ai_answer(question: str, flag_judge: bool) -> Union[None, str]:
    promt: str = None
    if flag_judge:
        promt = f'Rispondi in modo discorsivo come se fossi un essere umano alla domanda: {question}\
        Scrivi solo la risposta, in modo emotivo e naturale, senza meta commenti, spiegazioni o riferimenti alla domanda stessa.\
        Limìtati a rispondere come se fosse una conversazione vera, tra due persone. Non usare asterischi per indicare azioni,\
        pensieri o emozioni.'

    message = OllamaMessage(role= "user", content= promt)
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
