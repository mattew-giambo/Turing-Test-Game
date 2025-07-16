from fastapi import HTTPException
from models.player_info import PlayerInfo
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from typing import Dict, List, Tuple
import random
from models.pending_game import QA, GameReviewOutput
from utility.generate_ai_session import generate_full_ai_session

def start_pending_game_api(payload: PlayerInfo) -> GameReviewOutput:
    player_id: int = payload.player_id
    player_role: str = "judge"

    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id FROM Users WHERE id = %s"
        cursor.execute(query, (player_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code= 403, detail= "Utente non trovato")

        ai: bool = random.choice([True, False])
        if ai:
            ai_result = generate_full_ai_session(player_id)
            return GameReviewOutput(game_id=ai_result["game_id"], session=ai_result["session"])

        else:
            # Selezionare solo le partite “appese”:
            # La partita non è terminata
            # Esiste almeno una risposta umana
            # Esiste almeno una risposta non vuota -> TRIM() per eliminare eventuali spazi vuoti, tab, ecc., quindi anche risposte contenenti solo spazi saranno escluse.
            # Il player_id fornito non ha già partecipato alla partita
            # Non è ancora stato assegnato un giudice alla partita

            query = """ SELECT id 
            FROM Games as g
            WHERE g.terminated = FALSE
            AND EXISTS (
            SELECT *
            FROM Q_A AS qa
            WHERE qa.game_id = g.id AND qa.ai_answer = FALSE AND TRIM(qa.answer) != '')
            AND NOT EXISTS (
            SELECT *
            FROM UserGame as ug
            WHERE ug.game_id = g.id AND player_id = %s)
            AND NOT EXISTS (
            SELECT *
            FROM UserGames AS ug2
            WHERE ug2.game_id = g.id AND ug2.player_role = 'judge')
            """

            cursor.execute(query, (player_id,))
            pending_games: List[Tuple] = cursor.fetchall()

            if not pending_games:
                # se non ci sono pending games generane uno con AI
                ai_result = generate_full_ai_session(player_id)
                return GameReviewOutput(game_id=ai_result["game_id"], session=ai_result["session"])

            random_game = random.choice(pending_games)
            game_id = random_game[0]

            query = "INSERT INTO UserGames(game_id, player_id, player_role) VALUES (%s, %s, %s)"
            cursor.execute(query, (game_id, player_id, player_role))
            connection.commit()

            # Recupera le domande della partita
            query = "SELECT question_id, question, answer FROM Q_A WHERE game_id = %s"
            cursor.execute(query, (game_id,))
            game: List[Tuple[int, str, str]] = cursor.fetchall()

            # Ordina per question_id (1, 2, 3)
            game.sort(key=lambda x: x[0])  # x[0] = question_id

            # Costruisce il dizionario con chiavi 1, 2, 3
            session: Dict[int, QA] = {
                question_id: QA(question=question, answer=answer)
                for question_id, question, answer in game
            }

            return GameReviewOutput(game_id=game_id, session=session)

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Errore durante la generazione della partita: {e}")

    finally:
        close_cursor(cursor)
        close_connection(connection)