from fastapi import HTTPException
import requests
from config.constants import OLLAMA_CHAT_URL, MODEL
from models.ollama import OllamaInput, OllamaMessage
from typing import List, Optional, Dict

def get_ai_answer(question: Optional[str] = None, flag_judge: bool= True) -> Optional[str]:
    """
    Richiede una risposta dall'AI Ollama. 
    Il comportamento cambia a seconda del ruolo (giudice o partecipante).

    - Se `flag_judge` è True, l'AI risponde a una domanda simulando un essere umano.
    - Se `flag_judge` è False, l'AI genera 3 domande semplici e naturali per l'interrogatorio.

    Args:
        question (Optional[str]): Domanda a cui l'AI deve rispondere (necessaria se flag_judge=True).
        flag_judge (bool): Flag che indica il ruolo (True = giudice; False = generatore domande AI).

    Returns:
        Optional[str]: Risposta testuale dell'AI, o None in caso di errore.

    Raises:
        HTTPException: In caso di errore irreversibile nella comunicazione con l'AI.
    """
    
    if flag_judge:
        if not question:
            raise HTTPException(status_code=400, detail="Domanda mancante per la risposta del giudice AI.")
        
        prompt: str = f"""Rispondi in modo discorsivo e naturale come se fossi un essere umano alla domanda: {question}
                    Scrivi solo la risposta, senza meta-commenti, spiegazioni o riferimenti alla domanda stessa.
                    Rispondi in modo emotivo e spontaneo, come in una vera conversazione tra due persone.
                    Non usare asterischi per indicare azioni o pensieri. 
                    La risposta deve essere breve, massimo 1-2 frasi."""


    else:
        prompt: str = "Genera tre domande semplici e naturali, ciascuna su un argomento diverso. " \
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
    
    answer: Optional[str] = result.get("message", {}).get("content")
    return answer

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