from fastapi import FastAPI, HTTPException
from models.user_info import UserInfo
from models.confirm_game import ConfirmGame
from models.game_info import GameInfo
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
from models.authentication import UserRegister, UserLogin
from models.response_models import RegisterResponse, LoginResponse
import mariadb
from typing import Dict, Any, List, Tuple
import time
from datetime import datetime
import random
from rapidfuzz import process, fuzz

from utility.ai_utils import get_ai_answer, parse_ai_questions

app = FastAPI()

active_games: Dict[int, Dict[Any]] = {}
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
        "opponent_ai": None
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

    # RISPOSTE PRESE DA DB
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
    active_games[game_id]["opponent_ai"] = ai

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
        answer = get_ai_answer("", flag_judge=False)
        questions = parse_ai_questions(answer)

        if len(questions) < 3:
            raise HTTPException(status_code=500, detail="L'AI non ha generato abbastanza domande")

        insert_q_a_participant_api(game_id, questions[:3], ai_question=True)

        return ParticipantGameOutput(
            question_1=questions[0],
            question_2=questions[1],
            question_3=questions[2]
        )

    else:

        try:
            connection: mariadb.Connection = connect_to_database()
            cursor: mariadb.Cursor = get_cursor(connection)

            # Prende tutte le domande dal DB, con la flag ai_question
            cursor.execute("SELECT DISTINCT question, ai_question FROM Q_A")
            rows = cursor.fetchall()

            if not rows:
                raise HTTPException(status_code=404, detail="Nessuna domanda trovata nel database")
            
            # Estrae le domande e le mescola
            tutte_le_domande = [(row[0].strip(), row[1]) for row in rows]
            random.shuffle(tutte_le_domande)

            # Filtro fuzzy per evitare duplicati
            domande_distinte: List[str] = []
            ai_flags: List[bool] = []

            for domanda, flag in tutte_le_domande:
                aggiungi_domanda = True  # supponiamo che la domanda sia valida

                for esistente in domande_distinte:
                    similarita = fuzz.token_sort_ratio(domanda.lower(), esistente.lower())

                    if similarita >= 85:
                        aggiungi_domanda = False  # troppo simile a una domanda già presente
                        break  # non serve continuare a confrontare con le altre

                if aggiungi_domanda:
                    domande_distinte.append(domanda)
                    ai_flags.append(flag)

                if len(domande_distinte) == 3:
                    break  # abbiamo trovato abbastanza domande distinte

            # Fallback: usa domande generate dall'AI se non ci sono abbastanza distinte
            if len(domande_distinte) < 3:
                answer = get_ai_answer("", flag_judge=False)
                domande_distinte: List[str] = []
                ai_flags: List[bool] = []

                domande_distinte = parse_ai_questions(answer)
                ai_flags = [True] * len(domande_distinte)

            # Inserisce le domande nel DB con i flag corretti
            for domanda, ai_flag in zip(domande_distinte[:3], ai_flags[:3]):
                insert_q_a_participant_api(game_id, [domanda], ai_question=ai_flag)

            return ParticipantGameOutput(
                question_1=domande_distinte[0],
                question_2=domande_distinte[1],
                question_3=domande_distinte[2]
            )

        except mariadb.Error:
            raise HTTPException(status_code=500, detail="Errore durante la generazione delle domande")

        finally:
            close_cursor(cursor)
            close_connection(connection)

@app.post("/submit-participant-answers-api/{game_id}", response_model=ResponseSubmit)
def submit_answers_api(game_id: int, input_data: AnswerInput):
    if game_id not in active_games.keys():
        raise HTTPException(status_code= 403, detail= "Partita non trovata")
    
    partita = active_games[game_id]
    if partita["player_role"] != "participant":
        raise HTTPException(status_code=400, detail="Ruolo non valido per questa richiesta")
    
    if len(input_data.answers) != 3:
        raise HTTPException(status_code=422, detail="Devono essere fornite esattamente tre risposte")

    try:
        connection: mariadb.Connection = connect_to_database()
        cursor: mariadb.Cursor = get_cursor(connection)

        query: str = """
            UPDATE Q_A
            SET answer = %s
            WHERE game_id = %s AND question_id = %s
        """

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

@app.post("/end-game-judge-api/{game_id}")
def end_game_judge_api(judge_answer: JudgeGameAnswer, game_id: int):
    if game_id not in active_games:
        raise HTTPException(status_code=403, detail="Partita non trovata")
    
    player_role = active_games[game_id]["player_role"]
    if player_role != "judge":
        raise HTTPException(status_code=400, detail="Ruolo non valido per questa richiesta")
    
    player_name = active_games[game_id]["player_name"]
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
        cursor.execute("SELECT result FROM games WHERE id = %s", (game_id,))
        game_result = cursor.fetchone()
        if game_result is not None:
            raise HTTPException(status_code=400, detail="Questa partita è già stata chiusa.")

        # VERIFICO ESITO
        if judge_answer.is_ai == active_games[game_id]["opponent_ai"]:
            cursor.execute("UPDATE games SET result = 'win' WHERE id = %s", (game_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_judge = score_judge + 3,
                    won_judge = won_judge + 1
                WHERE user_id = %s
            """, (player_id,))
        else:
            cursor.execute("UPDATE games SET result = 'loss' WHERE id = %s", (game_id,))
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
        active_games.pop(game_id) # rimozione della partita attiva

    return EndJudgeGameOutput(message= "Partita terminata, esito registrato con successo!")

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
