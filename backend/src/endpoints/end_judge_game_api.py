from typing import Optional
from fastapi import HTTPException
from models.judge_game import JudgeGameAnswer, EndJudgeGameOutput
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from config.constants import JUDGE_WON_POINTS, JUDGE_LOST_POINTS, PART_WON_POINTS, PART_LOST_POINTS

def end_judge_game_api(judge_answer: JudgeGameAnswer, game_id: int) -> EndJudgeGameOutput:
    """
    Termina una sessione di gioco da parte del giudice, valuta la risposta, aggiorna lo stato del database
    e restituisce il risultato della partita.

    Args:
        judge_answer (JudgeGameAnswer): Indica il verdetto del giudice.
        game_id (int): ID della partita da terminare.

    Returns:
        EndJudgeGameOutput: Esito finale con messaggio, esito (vittoria/sconfitta) e punti guadagnati.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT terminated FROM Games WHERE id = %s"
        cursor.execute(query, (game_id,))

        if result is None:
            raise HTTPException(status_code=404, detail="Partita non trovata")
        if result[0] is True:
            raise HTTPException(status_code=403, detail="Partita già terminata")

        # Recupera l'ID del giudice
        query = "SELECT player_id FROM UserGames WHERE game_id = %s AND player_role = 'judge'"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Giudice non trovato")
        judge_id: int = result[0]

        # Recupera l'ID del partecipante, se esiste 
        query = "SELECT player_id FROM UserGames WHERE game_id = %s AND player_role = 'participant'"
        cursor.execute(query, (game_id,))
        participant = cursor.fetchone()
        participant_id: Optional[int] = participant[0] if participant else None

        query = "UPDATE Games SET terminated = TRUE WHERE id = %s"
        cursor.execute(query, (game_id,))

        verdetto: bool = judge_answer.is_ai
        participant_is_ai: bool = (participant_id == 1)
        is_won: bool = verdetto == participant_is_ai

        message: str = "Congratulazioni hai vinto!" if is_won else "Ooohh Noo, hai perso!"
        points: int = JUDGE_WON_POINTS if is_won else JUDGE_LOST_POINTS

        # Aggiorna UserGames e Stats per il giudice
        query = """
            UPDATE UserGames SET is_won = %s, points = %s
            WHERE game_id = %s AND player_id = %s
        """
        cursor.execute(query, (is_won, points, game_id, judge_id))

        query = """
            UPDATE Stats
            SET n_games = n_games + 1,
                score_judge = score_judge + %s,
                won_judge = won_judge + %s,
                lost_judge = lost_judge + %s
            WHERE user_id = %s
        """
        cursor.execute(query, (
            points,
            1 if is_won else 0,
            0 if is_won else 1,
            judge_id
        ))

        # Se il partecipante è AI (ID=1), si aggiornano anche i suoi dati: l’AI vince se il giudice ha sbagliato.
        if participant_id == 1:
            ai_is_won: bool = not is_won
            ai_points: int = PART_WON_POINTS if ai_is_won else PART_LOST_POINTS

            query = """
                UPDATE UserGames SET is_won = %s, points = %s
                WHERE game_id = %s AND player_id = %s
            """
            cursor.execute(query, (ai_is_won, ai_points, game_id, participant_id))

            query = """
                UPDATE Stats
                SET n_games = n_games + 1,
                    score_part = score_part + %s,
                    won_part = won_part + %s,
                    lost_part = lost_part + %s
                WHERE user_id = %s
            """
            cursor.execute(query, (
                ai_points,
                1 if ai_is_won else 0,
                0 if ai_is_won else 1,
                participant_id
            ))

            connection.commit()

        return EndJudgeGameOutput(
            message=message,
            is_won=is_won,
            points=points
        )
    
    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Errore del database: {e}")

    finally:
        close_cursor(cursor)
        close_connection(connection)