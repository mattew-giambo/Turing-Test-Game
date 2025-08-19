from typing import Optional
from fastapi import HTTPException
from models.judge_game import JudgeGameAnswer, EndJudgeGameOutput
from utility.db.close_connection import close_connection
from utility.db.close_cursor import close_cursor
from utility.db.connect_to_database import connect_to_database
from utility.db.get_cursor import get_cursor
import mariadb
from config.constants import JUDGE_WON_POINTS, JUDGE_LOST_POINTS, PART_WON_POINTS, PART_LOST_POINTS

def end_judge_game_api(judge_answer: JudgeGameAnswer, game_id: int) -> EndJudgeGameOutput:
    """
    Termina una partita nel ruolo di giudice e aggiorna punteggi e statistiche.

    Verifica lo stato della partita e recupera gli ID del giudice e del partecipante.
    Aggiorna lo stato della partita come terminata.
    Calcola l'esito (vittoria/sconfitta) del giudice basandosi sulla risposta fornita
    e aggiorna punti e statistiche sia del giudice che del partecipante (inclusa AI).

    Args:
        judge_answer (JudgeGameAnswer): Risposta del giudice (is_ai indica se ha scelto AI).
        game_id (int): Identificativo della partita da terminare.

    Returns:
        EndJudgeGameOutput: Messaggio di risultato, esito vittoria e punti assegnati.

    Raises:
        HTTPException:
            - 404 se partita, giudice o partecipante non trovati.
            - 403 se partita già terminata.
            - 500 per errori di database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT is_terminated FROM Games WHERE id = %s"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Partita non trovata")
        if result[0] is True:
            raise HTTPException(status_code=403, detail="Partita già terminata")

        # Recupera l'ID del giudice
        query = "SELECT player_id FROM UserGames WHERE game_id = %s AND player_role = 'judge'"
        cursor.execute(query, (game_id,))
        judge = cursor.fetchone()
        if judge is None:
            raise HTTPException(status_code=404, detail="Giudice non trovato")
        judge_id: int = judge[0]

        # Recupera ID del partecipante (se presente)
        query = "SELECT player_id FROM UserGames WHERE game_id = %s AND player_role = 'participant'"
        cursor.execute(query, (game_id,))
        participant = cursor.fetchone()
        participant_id: Optional[int] = participant[0] if participant else None

        # Termina la partita
        query = "UPDATE Games SET is_terminated = TRUE WHERE id = %s"
        cursor.execute(query, (game_id,))

        # Determina esito giudice e punteggio
        verdict_is_ai: bool = judge_answer.is_ai
        participant_is_ai: bool = (participant_id == 1)
        judge_won: bool = (verdict_is_ai == participant_is_ai)

        message: str = "Congratulazioni hai vinto!" if judge_won else "Ooohh Noo, hai perso!"
        judge_points: int = JUDGE_WON_POINTS if judge_won else JUDGE_LOST_POINTS

        # Aggiorna record giudice in UserGames
        cursor.execute(
            """
            UPDATE UserGames SET is_won = %s, points = %s
            WHERE game_id = %s AND player_id = %s
            """,
            (judge_won, judge_points, game_id, judge_id)
        )

        # Aggiorna statistiche giudice in Stats
        cursor.execute(
            """
            UPDATE Stats
            SET n_games = n_games + 1,
                score_judge = score_judge + %s,
                won_judge = won_judge + %s,
                lost_judge = lost_judge + %s
            WHERE user_id = %s
            """,
            (
                judge_points,
                1 if judge_won else 0,
                0 if judge_won else 1,
                judge_id
            )
        )

        # Se partecipante è AI (ID=1), aggiorna anche i suoi dati
        if participant_id == 1:
            ai_won: bool = not judge_won
            ai_points: int = PART_WON_POINTS if ai_won else PART_LOST_POINTS

            cursor.execute(
                """
                UPDATE UserGames SET is_won = %s, points = %s
                WHERE game_id = %s AND player_id = %s
                """,
                (ai_won, ai_points, game_id, participant_id)
            )

            cursor.execute(
                """
                UPDATE Stats
                SET n_games = n_games + 1,
                    score_part = score_part + %s,
                    won_part = won_part + %s,
                    lost_part = lost_part + %s
                WHERE user_id = %s
                """,
                (
                    ai_points,
                    1 if ai_won else 0,
                    0 if ai_won else 1,
                    participant_id
                )
            )

        connection.commit()

        return EndJudgeGameOutput(
            message=message,
            is_won=judge_won,
            points=judge_points
        )
    
    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Errore del database: {e}")

    finally:
        close_cursor(cursor)
        close_connection(connection)