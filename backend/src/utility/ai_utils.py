import requests
from config.constants import OLLAMA_CHAT_URL, MODEL
from models.ollama import OllamaInput, OllamaMessage
from typing import List, Union, Dict

def get_ai_answer(question: str= None, flag_judge: bool= True) -> Union[None, str]:
    prompt: str = None
    if flag_judge:
        prompt = f'Rispondi in modo discorsivo come se fossi un essere umano alla domanda: {question}\
        Scrivi solo la risposta, in modo emotivo e naturale, senza meta commenti, spiegazioni o riferimenti alla domanda stessa.\
        Limìtati a rispondere come se fosse una conversazione vera, tra due persone. Non usare asterischi per indicare azioni,\
        pensieri o emozioni.'

    else:
        prompt = "Genera tre domande semplici e naturali, ciascuna su un argomento diverso. " \
        "Scegli liberamente argomenti comuni che possano emergere in una conversazione informale tra persone. " \
        "Evita domande tecniche, difficili o filosofiche. " \
        "Non aggiungere introduzioni, commenti, spiegazioni o riferimenti al motivo per cui le domande sono state generate. " \
        "Restituisci solo le tre domande, numerate da 1 a 3."

    message = OllamaMessage(role= "user", content= prompt)
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

from typing import List

def parse_ai_questions(answer: str) -> List[str]:
    """
    Estrae una lista di domande dalla risposta generata dall'AI.

    L'AI riceve un prompt che la invita a generare esattamente tre domande numerate da 1 a 3,
    separate da ritorni a capo. Questa funzione processa il testo generato ed estrae solo
    il contenuto testuale delle domande, scartando la numerazione.

    Args:
        answer (str): Risposta generata dall'AI, contenente tre domande numerate.

    Returns:
        List[str]: Lista di domande estratte come stringhe. La lista può essere vuota se
                   la risposta è assente o malformata.
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