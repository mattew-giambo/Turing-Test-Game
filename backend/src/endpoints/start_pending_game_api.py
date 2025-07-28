from fastapi import HTTPException

from models.player_info import PlayerInfo
from models.confirm_game import ConfirmGame
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.generate_ai_session import generate_full_ai_session

import mariadb
from typing import List, Tuple
import random

def start_pending_game_api(payload: PlayerInfo) -> ConfirmGame:
    """
    Avvia una nuova partita in modalità 'pending' per il ruolo di giudice.

    Se esiste una partita non terminata, con almeno una risposta umana valida,
    senza giudice assegnato e a cui l'utente non ha ancora partecipato,
    viene assegnata tale partita. In caso contrario, viene generata una nuova
    sessione completamente AI.

    Args:
        payload (PlayerInfo): Informazioni sul giocatore (ID e ruolo).

    Returns:
        ConfirmGame: Dati riepilogativi della partita appena avviata.
    """
    player_id: int = payload.player_id
    player_role: str = "judge"

    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        # Verifica che l'utente esista
        query: str = "SELECT id FROM Users WHERE id = %s"
        cursor.execute(query, (player_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code= 403, detail= "Utente non trovato")
        
        query = "SELECT user_name FROM Users WHERE id = %s"
        cursor.execute(query, (player_id,))
        result = cursor.fetchone()
        player_name: str = result[0]

        ai: bool = random.choice([True, False])
        if ai:
            ai_result = generate_full_ai_session(player_id)
            return ConfirmGame(
                game_id=ai_result["game_id"],
                player_id=player_id,
                player_name=player_name,
                player_role=player_role
            )

        # Seleziona una partita 'pending' tra quelle già esistenti nel database.
        # Criteri:
        # 1. La partita non è terminata (g.terminated = FALSE)
        # 2. Esiste almeno una risposta umana valida (qa.ai_answer = FALSE e TRIM(qa.answer) != '')
        # 3. Il player corrente non ha già partecipato alla partita (assenza in UserGames)
        # 4. Nessun giudice è stato ancora assegnato alla partita (assenza di ruolo 'judge' in UserGames)

        query = """
            SELECT g.id
            FROM Games AS g
            WHERE g.terminated = FALSE
            AND EXISTS (
                SELECT *
                FROM Q_A AS qa
                WHERE qa.game_id = g.id AND qa.ai_answer = FALSE AND TRIM(qa.answer) != ''
            )
            AND NOT EXISTS (
                SELECT *
                FROM UserGames AS ug
                WHERE ug.game_id = g.id AND ug.player_id = %s
            )
            AND NOT EXISTS (
                SELECT *
                FROM UserGames AS ug2
                WHERE ug2.game_id = g.id AND ug2.player_role = 'judge'
            )
            """
        cursor.execute(query, (player_id,))
        pending_games: List[Tuple[int]] = cursor.fetchall()

        if not pending_games:
            ai_result = generate_full_ai_session(player_id)
            return ConfirmGame(
                game_id=ai_result["game_id"],
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