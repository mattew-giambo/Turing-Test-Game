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
import mariadb
from typing import Dict, Any
import time
from datetime import datetime
import random
from rapidfuzz import process, fuzz

app = FastAPI()
active_games: Dict[str, Dict[Any]] = {}

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
    cursor.execute(query, (user_id, player_role))
    connection.commit()
    game_id = cursor.lastrowid

    active_games[game_id] = {
        "player_name": player_name,
        "player_role": player_role,
        "datetime": datetime.now(),
        "result": None
    }
    ##
    close_connection(connection)
    close_cursor(cursor)

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
    risposte_lista_output = []

    ai = random.choice([True, False])
    if ai:
        ## COLLEGARSI A OLLAMA E FAR RISPONDERE TRAMITE ALLE DOMANDE get_ai_answer for tutte le domande
        pass
    else:
        connection: mariadb.Connection = connect_to_database()
        cursor: mariadb.Cursor = get_cursor(connection)

        cursor.execute("SELECT id, question, answer FROM Q_A")
        domande = cursor.fetchall()

        close_connection(connection)
        close_cursor(cursor)

        # Converte in lista di dizionari
        lista_domande = [{"id": row[0], "question": row[1], "answer": row[2]} for row in domande]

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
                risposte_lista_output.append(lista_domande[index]["answer"])

        if len(risposte_lista_output) != len(lista_domande_input):
            ## COLLEGARSI A OLLAMA E FAR RISPONDERE ALLE DOMANDE TRAMITE FUNZIONE get_ai_answer
            pass
    
    return JudgeGameOutput(answer_1= risposte_lista_output[0], 
                           answer_2= risposte_lista_output[1], 
                           answer_3= risposte_lista_output[2])
        
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

            cursor.execute("SELECT DISTINCT question FROM Q_A")
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