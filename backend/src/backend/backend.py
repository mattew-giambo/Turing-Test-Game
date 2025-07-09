from fastapi import FastAPI, HTTPException
from models.user_info import UserInfo
from models.confirm_game import ConfirmGame
from models.judge_game_info import JudgeGameInfo
from models.judge_game import JudgeGameInput, JudgeGameOutput, JudgeGameAnswer, EndJudgeGameOutput
from models.user_stats import UserStats
from models.participant_game import ParticipantGameOutput, AnswerInput, ResponseSubmit
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.security import hash_password, verify_password
from utility.judge_game_api_ai import judge_game_api_ai
from utility.judge_game_api_db import judge_game_api_db
from utility.insert_q_a_judge_api import insert_q_a_judge_api
from utility.insert_q_a_participant_api import insert_q_a_participant_api
from models.authentication import UserRegister, UserLogin, RegisterResponse, LoginResponse
import mariadb
from typing import Dict, Any, List, Tuple
import time
from datetime import datetime
import random
from rapidfuzz import process, fuzz
from config.constants import JUDGE_WON_POINTS

from utility.ai_utils import get_ai_answer, parse_ai_questions

app = FastAPI()

active_judge_games: Dict[int, Dict[Any]] = {}
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

        return RegisterResponse(message="ok", user_id=user_id)

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Errore durante la registrazione: {e}")

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
            message="ok",
            user_id=user_id,
            user_name=user_name
        )

    except mariadb.Error:
        raise HTTPException(status_code=500, detail="Errore durante il login")

    finally:
        close_cursor(cursor)
        close_connection(connection)

@app.post("/start-judge-game-api")
def start_judge_game_api(payload: UserInfo):
    player_name = payload.player_name

    ## Verifica dell'utente nel database
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    cursor.execute("SELECT id FROM Users WHERE user_name = %s", player_name)
    result = cursor.fetchone()
    
    if(result is None):
        raise HTTPException(status_code= 404, detail= "Utente non trovato")
    ##

    ## Inserimento della partita nel database e nel dizionario
   
    player_id = result[0]
    try:
        cursor.execute( "INSERT INTO Games() VALUES ()")
        game_id = cursor.lastrowid()
        cursor.execute( "INSERT INTO UserGames(game_id, player_id, player_role) VALUES (%s)", (game_id, player_id, 'judge'))
        connection.commit()
    except mariadb.Error as e:
        print(e)
        raise HTTPException(
            status_code= 500,
            detail= "Errore del server nell'esecuzione della query"
        )
    finally:
        close_cursor(cursor)
        close_connection(connection)

    active_judge_games[game_id] = {
        "player_name": player_name,
        "datetime": datetime.now(),
        "opponent_ai": None
    }
    ##
    return ConfirmGame(game_id= game_id, player_id= player_id)

@app.get("/judge-game-info-api/{game_id}")
def player_role_api(game_id: int):
    if game_id not in active_judge_games.keys():
        raise HTTPException(status_code= 403, detail= "Partita non trovata")
    
    player_name = active_judge_games[game_id]["player_name"]
    game_date= active_judge_games[game_id]["datetime"]

    return JudgeGameInfo(
                    player_name= player_name,
                    game_date= game_date)

@app.post("/judge-game-api/{game_id}")
def judge_game_api(payload: JudgeGameInput, game_id: int):
    if game_id not in active_judge_games.keys():
        raise HTTPException(status_code= 403, detail= "Partita non trovata")
    
    lista_domande_input = payload.questions_list
    lista_risposte_output = []

    ai = random.choice([True, False])

    # RISPOSTE DEGLI UTENTI PRESE DA DB
    if not ai:
        lista_risposte_output = judge_game_api_db(lista_domande_input)

    # RISPOSTE PRESE DA AI
    if ai or len(lista_risposte_output) != len(lista_domande_input):
        lista_risposte_output = judge_game_api_ai(lista_domande_input)
        if len(lista_risposte_output) != len(lista_domande_input):
            raise HTTPException(status_code= 500, detail= "Errore del server")
        ai = True
    
    # INSERIMENT IN DB
    insert_q_a_judge_api(game_id, ai, lista_domande_input, lista_risposte_output)
    active_judge_games[game_id]["opponent_ai"] = ai

    return JudgeGameOutput(answers_list= lista_risposte_output)
        
@app.post("/participant-game-api/{game_id}", response_model=ParticipantGameOutput)
def participant_game_api(game_id: int) -> ParticipantGameOutput:
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query:str = "SELECT id FROM Games WHERE id = %s AND terminated = 0"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Partita non trovata o già terminata.")
        
        ai = random.choice([True, False])
        if ai:
            answer = get_ai_answer(flag_judge=False)
            questions = parse_ai_questions(answer)

            if len(questions) < 3:
                raise HTTPException(status_code=500, detail="L'AI non ha generato abbastanza domande")

            insert_q_a_participant_api(game_id, questions[:3], ai_question=True)

            return ParticipantGameOutput(questions=questions[:3])
        
        else:
            # Prende tutte le domande e la relativa flag ai_question dal DB
            cursor.execute("SELECT DISTINCT question, ai_question FROM Q_A")
            result = cursor.fetchall()

            if not result:
                raise HTTPException(status_code=404, detail="Nessuna domanda trovata nel database")
            
            # Estrae le domande e le mescola
            questions = [(elem[0].strip(), elem[1]) for elem in result]
            random.shuffle(questions)

            # Filtro fuzzy per evitare duplicati
            domande_distinte: List[str] = []
            ai_flags: List[bool] = []

            for question, flag in questions:
                add_question = True  # supponiamo che la domanda sia valida

                for esistente in domande_distinte:
                    similarita = fuzz.token_sort_ratio(question.lower(), esistente.lower())

                    if similarita >= 85:
                        add_question = False  # troppo simile a una domanda già presente
                        break  # non serve continuare a confrontare con le altre

                if add_question:
                    domande_distinte.append(question)
                    ai_flags.append(flag)

                if len(domande_distinte) == 3:
                    break  # abbiamo trovato abbastanza domande distinte

            # Fallback: usa domande generate dall'AI se non ci sono abbastanza distinte
            if len(domande_distinte) < 3:
                answer = get_ai_answer(flag_judge=False)
                domande_distinte = parse_ai_questions(answer)
                ai_flags = [True] * len(domande_distinte)

            # Inserisce le domande nel DB con i flag corretti
            for question, ai_flag in zip(domande_distinte[:3], ai_flags[:3]):
                insert_q_a_participant_api(game_id, [question], ai_question=ai_flag)

            return ParticipantGameOutput(questions=domande_distinte[:3])

    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail=f"Errore database: {e}")
    finally:
            close_cursor(cursor)
            close_connection(connection)

@app.post("/submit-participant-answers-api/{game_id}", response_model=ResponseSubmit)
def submit_answers_api(game_id: int, input_data: AnswerInput):
    if len(input_data.answers) != 3:
        raise HTTPException(status_code=422, detail="Devono essere fornite esattamente tre risposte")
    
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query:str = "SELECT id FROM Games WHERE id = %s AND terminated = 0"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Partita non trovata o già terminata.")
        
        query = "UPDATE Q_A SET answer = %s WHERE game_id = %s AND question_id = %s"

        for idx, answer in enumerate(input_data.answers, start=1):  
            cursor.execute(query, (answer.strip(), game_id, idx))

        connection.commit()
        return ResponseSubmit(status="ok")

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Errore durante l'aggiornamento delle risposte: {e}")

    finally:
        close_cursor(cursor)
        close_connection(connection)

@app.post("/start-pending-game-api")
def start_pending_game_api(payload: UserInfo):
    player_name = payload.player_name
    player_role = payload.player_role

    try:
        connection: mariadb.Connection = connect_to_database()
        cursor: mariadb.Cursor = get_cursor(connection)

        query= "SELECT id FROM Users WHERE user_name = %s"
        cursor.execute(query, player_name)
        result = cursor.fetchone()
        
        if(result is None):
            raise HTTPException(status_code= 403, detail= "Utente non trovato")
    
        user_id = result[0]

        ai = random.choice([True, False])
        if ai:
            pass

        else:


    except mariadb.Error:
        raise HTTPException(status_code=500, detail="Errore durante la generazione della partita")

    finally:
        close_cursor(cursor)
        close_connection(connection)

@app.post("/end-game-judge-api/{game_id}")
def end_game_judge_api(judge_answer: JudgeGameAnswer, game_id: int):
    if game_id not in active_judge_games:
        raise HTTPException(status_code=403, detail="Partita non trovata")
    
    player_name = active_judge_games[game_id]["player_name"]
    connection = connect_to_database()
    cursor = get_cursor(connection)
    try:
        # ID UTENTE
        cursor.execute("SELECT id FROM users WHERE user_name = %s", (player_name,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        player_id = result[0]

        # CONTROLLO SE IL GAME E' CHIUSO
        cursor.execute("SELECT terminated FROM games WHERE id = %s", (game_id,))
        game_result = cursor.fetchone()
        if game_result == True:
            raise HTTPException(status_code=400, detail="Questa partita è già stata chiusa.")

        # VERIFICO ESITO
        is_won: bool = False
        if judge_answer.is_ai == active_judge_games[game_id]["opponent_ai"]:
            cursor.execute("UPDATE games SET result = 'win', terminated= TRUE WHERE id = %s", (game_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_judge = score_judge + %s,
                    won_judge = won_judge + 1
                WHERE user_id = %s
            """, (JUDGE_WON_POINTS, player_id,))
            is_won= True
        else:
            cursor.execute("UPDATE games SET result = 'loss', terminated= TRUE WHERE id = %s", (game_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    lost_judge = lost_judge + 1
                WHERE user_id = %s
            """, (player_id,))

        connection.commit()
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore del server"
        )
    finally:
        close_cursor(cursor)
        close_connection(connection)
        active_judge_games.pop(game_id) # rimozione della partita attiva

    return EndJudgeGameOutput(message= "Partita terminata, esito registrato con successo!", is_won= is_won)

@app.get("/user-stats-api/{user_id}")
def get_user_stats(user_id: int):
    connection = connect_to_database()
    cursor = get_cursor(connection)

    cursor.execute("""
        SELECT user_id, n_games, score_part, score_judge, won_part, won_judge, lost_part, lost_judge
        FROM stats
        WHERE user_id = %s
    """, (user_id,))
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(
            status_code= 404,
            detail= "Utente non trovato!"
        )
    
    return UserStats(
        user_id= result[0],
        n_games= result[1],
        score_part= result[2],
        score_judge= result[3], 
        won_part= result[4], 
        won_judge= result[5], 
        lost_part= result[6], 
        lost_judge= result[7]
    )
