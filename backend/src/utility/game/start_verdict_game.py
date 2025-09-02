from fastapi import HTTPException

from models.start_game_info import StartGameInfo
from models.confirm_game import ConfirmGame
from utility.db.close_connection import close_connection
from utility.db.close_cursor import close_cursor
from utility.db.connect_to_database import connect_to_database
from utility.db.get_cursor import get_cursor
from utility.game.generate_ai_session import generate_ai_session

import mariadb
from typing import List, Tuple
import random

def start_verdict_game(payload: StartGameInfo) -> ConfirmGame:
    """
    Avvia una nuova partita in modalità 'verdict' per il ruolo di giudice.

    La funzione verifica l'esistenza dell'utente, recupera il nome, e tenta di assegnare il giocatore
    a una partita pendente esistente che rispetti determinati criteri. Se non sono disponibili partite 
    pendenti adeguate, viene generata una nuova sessione completamente AI.

    Criteri per assegnazione a partita pendente:
    - Partita non terminata
    - Presenza di almeno una risposta umana valida
    - Il giocatore non deve aver già partecipato alla partita
    - Nessun giudice assegnato alla partita

    Args:
        payload (PlayerInfo): Informazioni sul giocatore (ID e ruolo).

    Returns:
        ConfirmGame: Dati riepilogativi della partita appena avviata.

    Raises:
        HTTPException: 
            - 404 se il giocatore non è presente nel database.
            - 500 per errori nel database o durante la generazione della sessione AI.
    """
    player_id: int = payload.player_id
    player_role: str = "judge"

    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT user_name FROM Users WHERE id = %s"
        cursor.execute(query, (player_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code= 404, detail= "Utente non trovato")
        
        player_name: str = result[0]

        ai: bool = random.choice([True, False])

        if ai:
            ai_session = generate_ai_session(player_id)
            return ConfirmGame(
                game_id=ai_session["game_id"],
                player_id=player_id,
                player_name=player_name,
                player_role=player_role
            )

        query = """
            SELECT g.id
            FROM Games AS g
            WHERE g.is_terminated = FALSE
            AND EXISTS (
                SELECT 1
                FROM Q_A AS qa
                WHERE qa.game_id = g.id AND qa.ai_answer = FALSE AND TRIM(qa.answer) != ''
            )
            AND NOT EXISTS (
                SELECT 1
                FROM UserGames AS ug
                WHERE ug.game_id = g.id AND ug.player_id = %s
            )
            AND NOT EXISTS (
                SELECT 1
                FROM UserGames AS ug2
                WHERE ug2.game_id = g.id AND ug2.player_role = 'judge'
            )
        """
        cursor.execute(query, (player_id,))
        pending_games: List[Tuple[int]] = cursor.fetchall()

        if not pending_games:
            ai_session = generate_ai_session(player_id)
            return ConfirmGame(
                game_id=ai_session["game_id"],
                player_id=player_id,
                player_name=player_name,
                player_role=player_role
            )

        game_id: int = random.choice([row[0] for row in pending_games])
        cursor.execute(
            "INSERT INTO UserGames(game_id, player_id, player_role) VALUES (%s, %s, %s)",
            (game_id, player_id, player_role)
        )
        connection.commit()

        return ConfirmGame(
            game_id=game_id,
            player_id=player_id,
            player_name=player_name,
            player_role=player_role
        )

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Errore database: {e}")
    
    finally:
        close_cursor(cursor)
        close_connection(connection)