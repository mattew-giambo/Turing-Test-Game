import mariadb
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from typing import List
from rapidfuzz import process, fuzz
import random

def judge_game_api_db(lista_domande_input: List[str]):
    lista_risposte_output = []

    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    cursor.execute("SELECT id, question, answer FROM Q_A")
    domande = cursor.fetchall()

    close_connection(connection)
    close_cursor(cursor)

    # Converte in lista di dizionari
    lista_domande = [{"id": row[0], "question": row[1], "answer": row[2]} for row in domande]
    random.shuffle(lista_domande)
    
    # Estrai solo i testi delle domande, lista di domande
    domande_testo = [diz["question"] for diz in lista_domande]

    for i in range(0, len(lista_domande_input)):
        domanda_input = lista_domande_input[i]
        # Matching fuzzy
        match, score, index = process.extractOne(
            domanda_input,
            domande_testo,
            scorer=fuzz.token_sort_ratio
        )
        # Se somiglianza >= 80%, prendi la risposta associata
        if score >= 80:
            lista_risposte_output.append(lista_domande[index]["answer"])
    
    return lista_risposte_output