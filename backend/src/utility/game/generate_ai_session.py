from typing import Dict, List
from fastapi import HTTPException
from rapidfuzz import fuzz
import random
import mariadb

from utility.db.close_connection import close_connection
from utility.db.close_cursor import close_cursor
from utility.db.connect_to_database import connect_to_database
from utility.db.get_cursor import get_cursor
from utility.ai_utils import get_ai_answer, parse_ai_questions
from utility.game.is_distinct import is_distinct

from config.constants import NUM_QUESTIONS_PER_GAME

def generate_ai_session(player_id: int) -> Dict[str, int]:
    """
    Genera una nuova sessione di gioco completamente gestita dall'intelligenza artificiale (AI).
    
    La funzione crea una partita nella quale il giocatore `player_id` assume il ruolo di giudice
    mentre il partecipante è un'entità AI (player_id=1). Vengono generate 3 domande distinte con
    relative risposte da parte dell'AI, e inserite nella tabella `Q_A` associate alla partita.
    
    Il metodo cerca di utilizzare domande già presenti nel database per varietà e distinzione, 
    ricorrendo all'AI solo in caso di domande insufficienti o troppo simili.
    
    Args:
        player_id (int): ID del giocatore che assume il ruolo di giudice.
    
    Returns:
        Dict[str, int]: Dizionario contenente l'ID della partita creata, ad es. {"game_id": 123}.
    
    Raises:
        HTTPException: 
            - 500: se si verifica un errore durante la comunicazione con Ollama o In caso di errore interno durante al database. 
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    # Prompt base per generare le domande dall'AI in fallback
    prompt: str = (
        "Sei l'autore di un quiz show (programma televisivo). Devo scrivere tre domande da porre ai concorrenti durante una sessione di gioco.\n"
        "Scegli tre argomenti distinti che possono emergere in una conversazione informale tra persone. Per ciascun argomento, formula una domanda in tono naturale e colloquiale.\n"
        "Evita domande tecniche, filosofiche o troppo complesse. Niente introduzioni, spiegazioni o commenti.\n"
        "Restituisci solo le tre domande, numerate da 1 a 3."
    )

    try:
        # Creo una nuova partita
        query: str = "INSERT INTO Games () VALUES ()"
        cursor.execute(query)
        game_id: int = cursor.lastrowid

        # Associo il giudice umano alla partita
        query = "INSERT INTO UserGames (game_id, player_id, player_role) VALUES (%s, %s, 'judge')"
        cursor.execute(query, (game_id, player_id))

        # Associo il partecipante AI (user_id = 1)
        query = "INSERT INTO UserGames (game_id, player_id, player_role) VALUES (%s, %s, 'participant')"
        cursor.execute(query, (game_id, 1))

        # Prendo domande esistenti
        query = "SELECT DISTINCT question, ai_question FROM Q_A"
        cursor.execute(query)
        all_questions = cursor.fetchall()

        selected_questions: List[str] = []
        ai_flags: List[bool] = []

        if all_questions:
            # Mescolo domande per casualità
            questions = [(q.strip(), flag) for q, flag in all_questions]
            random.shuffle(questions)

            for question, flag in questions:
                if is_distinct(question, selected_questions):
                    selected_questions.append(question)
                    ai_flags.append(flag)

                if len(selected_questions) == NUM_QUESTIONS_PER_GAME:
                    break
        
        # Se non ho abbastanza domande distinte, chiedo all'AI di generare
        if len(selected_questions) < NUM_QUESTIONS_PER_GAME:
            ai_answer = get_ai_answer(prompt)
            selected_questions = parse_ai_questions(ai_answer)

            if len(selected_questions) < NUM_QUESTIONS_PER_GAME:
                raise HTTPException(status_code=500, detail="AI fallback fallito: domande insufficienti.")

            ai_flags = [True] * NUM_QUESTIONS_PER_GAME

        # Genero risposte AI per ciascuna domanda selezionata
        risposte_ai: List[str] = []
        for question in selected_questions:
            prompt = (
                f"Sei un concorrente di un quiz televisivo. Rispondi alla domanda: {question}.\n"
                "La risposta deve essere naturale, colloquiale e breve (1-2 frasi massimo).\n"
                "Evita esclamazioni, introduzioni o commenti extra.\n"
                "Scrivi solo la risposta."
            )
            risposta_ai = get_ai_answer(prompt)
            if not risposta_ai:
                raise HTTPException(status_code=500, detail="Errore nella risposta dell'AI")
            risposte_ai.append(risposta_ai.strip())

        # Inserisco domande e risposte nel DB
        query = """
            INSERT INTO Q_A (game_id, question_id, question, answer, ai_question, ai_answer)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        for idx, (question, answer, ai_flag) in enumerate(zip(selected_questions, risposte_ai, ai_flags), start=1):
            cursor.execute(query, (game_id, idx, question, answer, ai_flag, True))

        connection.commit()

        return {"game_id": game_id}

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Errore DB: {e}")
    
    finally:
        close_cursor(cursor)
        close_connection(connection)