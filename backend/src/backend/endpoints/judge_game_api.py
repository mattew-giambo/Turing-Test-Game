from fastapi import HTTPException
from models.judge_game import JudgeGameInput, JudgeGameOutput
from utility.judge_game_api_ai import judge_game_api_ai
from utility.judge_game_api_db import judge_game_api_db
from utility.insert_q_a_judge_api import insert_q_a_judge_api
from typing import Dict
import random

def judge_game_api(payload: JudgeGameInput, game_id: int, active_judge_games: Dict):
    if game_id not in active_judge_games.keys():
        raise HTTPException(status_code= 404, detail= "Partita non trovata")
    
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
    insert_q_a_judge_api(game_id, ai, lista_domande_input, lista_risposte_output)
    active_judge_games[game_id]["opponent_ai"] = ai

    return JudgeGameOutput(answers_list= lista_risposte_output)