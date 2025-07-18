from fastapi import HTTPException
from models.judge_game import JudgeGameInput, JudgeGameOutput
from utility.judge_game_api_ai import judge_game_api_ai
from utility.judge_game_api_db import judge_game_api_db
from utility.insert_q_a_judge_api import insert_q_a_judge_api
from utility.connect_to_database import connect_to_database
from utility.close_connection import close_connection
from utility.get_cursor import get_cursor
from utility.close_cursor import close_cursor
from typing import Dict
import mariadb
import random

def judge_game_api(payload: JudgeGameInput, game_id: int):
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    cursor.execute("SELECT id, terminated FROM Games WHERE id = %s", (game_id,))
    res = cursor.fetchone()

    if res is None:
        raise HTTPException(status_code= 404, detail= "Partita non trovata")
    if res[1] == True:
        raise HTTPException(status_code= 403, detail= "Partita già terminata")
    
    lista_domande_input = payload.questions_list
    lista_risposte_output = []

    ai = random.choice([True, False])

    # RISPOSTE DEGLI UTENTI PRESE DA DB
    if not ai:
        lista_risposte_output = judge_game_api_db(lista_domande_input)

    # RISPOSTE PRESE DA AI - FALLBACK NEL CASO IN CUI LE RISPOSTE PRESE DAL DB NON SIANO SUFFICIENTI
    if ai or len(lista_risposte_output) != len(lista_domande_input):
        lista_risposte_output = judge_game_api_ai(lista_domande_input)
        if len(lista_risposte_output) != len(lista_domande_input):
            raise HTTPException(status_code= 500, detail= "Errore del server")
        ai = True
    
    # INSERIMENT IN DB
    if ai:
        try:
            cursor.execute( "INSERT INTO UserGames(game_id, player_id, player_role) VALUES (%s)", (game_id, 1, "participant"))
            connection.commit()
        except mariadb.Error as e:
            raise HTTPException(
                status_code= 500,
                detail= "Errore del server"
            )
        
    close_cursor(cursor)
    close_connection(connection)

    insert_q_a_judge_api(game_id, ai, lista_domande_input, lista_risposte_output)
    return JudgeGameOutput(answers_list= lista_risposte_output)