from fastapi import FastAPI, HTTPException
from models.user_info import UserInfo
from models.confirm_game import ConfirmGame
from models.game_info import GameInfo
from models.judge_game import JudgeGameInput, JudgeGameOutput
from models.participant_game import ParticipantGameOutput
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.security import hash_password, verify_password
from utility.judge_game_api_ai import judge_game_api_ai
from utility.judge_game_api_db import judge_game_api_db
from utility.insert_q_a_judge_api import insert_q_a_judge_api
from models.authentication import UserRegister, UserLogin
from models.response_models import RegisterResponse, LoginResponse
import mariadb
from typing import Dict, Any, Tuple
import time
from datetime import datetime
import random
from rapidfuzz import process, fuzz

app = FastAPI()

active_games: Dict[str, Dict[Any]] = {}
sessioni_attive: Dict[int, Dict[str, str]] = {}

@app.post("/register-api", response_model=RegisterResponse)
def register_api(user: UserRegister) -> RegisterResponse:
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id FROM Users WHERE email = %s OR user_name = %s"
        cursor.execute(query, (user.email, user.user_name))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Utente già registrato con questa email o username")

        hashed_password = hash_password(user.password)

        query = "INSERT INTO Users (user_name, email, hashed_password) VALUES (%s, %s, %s)"
        cursor.execute(query, (user.user_name, user.email, hashed_password))
        connection.commit()

        user_id = cursor.lastrowid

        query = "INSERT INTO Stats (user_id) VALUES (%s)"
        cursor.execute(query, (user_id,))
        connection.commit()

        return RegisterResponse(message="Registrazione avvenuta con successo", user_id=user_id)

    except mariadb.Error:
        raise HTTPException(status_code=500, detail="Errore durante la registrazione")

    finally:
        close_cursor(cursor)
        close_connection(connection)

@app.post("/login-api", response_model=LoginResponse)
def login_api(user: UserLogin) -> LoginResponse:
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id, user_name, hashed_password FROM Users WHERE email = %s"
        cursor.execute(query, (user.email,))
        result: Tuple[int, str, str] = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Utente non trovato")

        user_id: int = result[0]
        user_name: str = result[1]
        hashed_password: str = result[2]

        if not verify_password(user.password, hashed_password):
            raise HTTPException(status_code=401, detail="Password errata")

        sessioni_attive[user_id] = {
            "user_name": user_name,
            "email": user.email
        }

        return LoginResponse(
            message="Login riuscito",
            user_id=user_id,
            user_name=user_name
        )

    except mariadb.Error:
        raise HTTPException(status_code=500, detail="Errore durante il login")

    finally:
        close_cursor(cursor)
        close_connection(connection)

@app.post("/start-game-api")
def start_game_api(payload: UserInfo):
    player_name = payload.player_name
    player_role = payload.player_role

    ## Verifica dell'utente nel database
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    query= "SELECT id FROM Users WHERE user_name = %s"
    cursor.execute(query, player_name)
    result = cursor.fetchone()
    
    if(result is None):
        raise HTTPException(status_code= 403, detail= "Utente non trovato")
    ##

    ## Inserimento della partita nel database e nel dizionario
   
    user_id = result[0]
    query = "INSERT INTO Games(user_id, player_role) VALUES (%s, %s)"
    try:
        cursor.execute(query, (user_id, player_role))
        connection.commit()
        game_id = cursor.lastrowid
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore del server nell'esecuzione della query"
        )
    finally:
        close_cursor(cursor)
        close_connection(connection)

    active_games[game_id] = {
        "player_name": player_name,
        "player_role": player_role,
        "datetime": datetime.now(),
        "result": None
    }
    ##
    return ConfirmGame(game_id= game_id)

@app.get("/game-info-api/{game_id}")
def player_role_api(game_id: int):
    if game_id not in active_games.keys():
        raise HTTPException(status_code= 403, detail= "Partita non trovata")
    
    player_name = active_games[game_id]["player_name"]
    player_role = active_games[game_id]["player_role"]
    game_date= active_games[game_id]["datetime"]

    return GameInfo(player_name= player_name, 
                    player_role= player_role, 
                    game_date= game_date)

@app.post("/judge-game-api/{game_id}")
def judge_game_api(judge_game: JudgeGameInput, game_id: int):
    if game_id not in active_games.keys():
        raise HTTPException(status_code= 403, detail= "Partita non trovata")
    
    lista_domande_input = [
        judge_game.question_1,
        judge_game.question_2,
        judge_game.question_3
    ]
    lista_risposte_output = []

    ai = random.choice([True, False])
    if not ai:
        lista_risposte_output = judge_game_api_db(lista_domande_input)

    if ai or len(lista_risposte_output) != len(lista_domande_input):
        lista_risposte_output = judge_game_api_ai(lista_domande_input)
        if len(lista_risposte_output) != len(lista_domande_input):
            raise HTTPException(status_code= 500, detail= "Errore del server")
        ai = True
    
    insert_q_a_judge_api(game_id, ai, lista_domande_input, lista_risposte_output)

    return JudgeGameOutput(answer_1= lista_risposte_output[0], 
                           answer_2= lista_risposte_output[1], 
                           answer_3= lista_risposte_output[2])
        
@app.post("/participant-game-api/{game_id}", response_model=ParticipantGameOutput)
def participant_game_api(game_id: int) -> ParticipantGameOutput:
    if game_id not in active_games.keys():
        raise HTTPException(status_code= 403, detail= "Partita non trovata")
    
    partita = active_games[game_id]
    if partita["player_role"] != "participant":
        raise HTTPException(status_code=400, detail="Ruolo non valido per questa richiesta")
    
    ai = random.choice([True, False])
    if ai:
        ## COLLEGARSI A OLLAMA E FAR RISPONDERE TRAMITE ALLE DOMANDE get_ai_answer for tutte le domande
        pass
    else:

        try:
            connection: mariadb.Connection = connect_to_database()
            cursor: mariadb.Cursor = get_cursor(connection)

            # Prende domande scritte da esseri umani
            cursor.execute("SELECT DISTINCT question FROM Q_A WHERE ai_question = %s", (False,))
            questions = cursor.fetchall()

            if not questions:
                raise HTTPException(status_code=404, detail="Nessuna domanda trovata nel database")
            
            # Estrae le domande e le mescola
            tutte_le_domande = [question[0].strip() for question in questions]
            random.shuffle(tutte_le_domande)

            # Filtro fuzzy per evitare duplicati
            domande_distinte = []
            for domanda in tutte_le_domande:
                aggiungi_domanda = True  # supponiamo che la domanda sia valida

                for esistente in domande_distinte:
                    similarita = fuzz.token_sort_ratio(domanda.lower(), esistente.lower())
                    
                    if similarita >= 85:
                        aggiungi_domanda = False  # troppo simile a una domanda già presente
                        break  # non serve continuare a confrontare

                if aggiungi_domanda:
                    domande_distinte.append(domanda)


            if len(domande_distinte) < 3:
                ## COLLEGARSI A OLLAMA E FAR RISPONDERE TRAMITE ALLE DOMANDE get_ai_answer for tutte le domande
                pass

            # Salva le domande nel database
            for idx, domanda in enumerate(domande_distinte[:3], start=1):
                query = "INSERT INTO Q_A (game_id, question_id, question, answer, ai_question, ai_answer) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (
                    game_id,             # ID della partita
                    idx,                 # question_id: 1, 2, 3
                    domanda,             # testo della domanda
                    "",                  # risposta vuota
                    False,               # ai_question
                    False                # ai_answer
                ))
            connection.commit()

            return ParticipantGameOutput(
                question_1=domande_distinte[0],
                question_2=domande_distinte[1],
                question_3=domande_distinte[2]
            )

        except mariadb.Error:
            raise HTTPException(status_code=500, detail="Errore durante la registrazione")

        finally:
            close_cursor(cursor)
            close_connection(connection)