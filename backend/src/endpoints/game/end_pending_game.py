from typing import Dict
from fastapi import HTTPException
from models.judge_game import JudgeGameAnswer
from models.pending_game import EndPendingJudgeGameOutput
from utility.db.close_connection import close_connection
from utility.db.close_cursor import close_cursor
from utility.db.connect_to_database import connect_to_database
from utility.db.get_cursor import get_cursor
from config.constants import JUDGE_WON_POINTS, PART_WON_POINTS, PART_LOST_POINTS, JUDGE_LOST_POINTS
import mariadb

def end_pending_game_api(judge_answer: JudgeGameAnswer, game_id: int) -> EndPendingJudgeGameOutput:
    """
    Termina una partita in modalità 'pending' gestendo la risposta del giudice,
    calcola l'esito (vittoria o sconfitta), assegna i punti a giudice e partecipante,
    e aggiorna lo stato della partita e le statistiche nel database.

    Args:
        judge_answer (JudgeGameAnswer): La risposta del giudice (se crede che il partecipante sia un'IA).
        game_id (int): ID della partita da terminare.

    Returns:
        EndPendingJudgeGameOutput: Esito finale per il giudice con messaggio, punteggio e risultato.
    
    Raises:
        HTTPException: 
            - 404: Se il `game_id` è associato a una partita inesistente.
            - 403: Se il `game_id` è associato a una partita già terminata.
            - 500: In caso di errore interno durante l’accesso al database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        cursor.execute("""
            SELECT ug.player_id, ug.player_role
            FROM Games AS g
            JOIN UserGames AS ug ON g.id = ug.game_id
            WHERE g.is_terminated = FALSE AND g.id = %s
        """, (game_id,))
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code= 404, detail= "Partita non trovata")
        if len(result) < 2:
            raise HTTPException(status_code= 403, detail= f"Nessuna partita con {game_id} è stata avviata")
        
        # Mappa i ruoli in un dizionario: {"judge": judge_id, "participant": participant_id}
        players: Dict[str, int] = {role: player_id for player_id, role in result}

        # Termina ufficialmente la partita nel database
        query: str = "UPDATE Games SET is_terminated = TRUE WHERE id = %s"
        cursor.execute(query, (game_id,))

        # Valuta il verdetto: se il giudice ha indovinato l'identità del partecipante (IA o umano)
        verdetto: bool = judge_answer.is_ai
        participant_is_ai: bool = (players["participant"] == 1)
        is_won: bool = (verdetto == participant_is_ai)

        message: str = "Congratulazioni, hai vinto!" if is_won else "Ohh Noo, hai perso!"
        judge_points: int = JUDGE_WON_POINTS if is_won else JUDGE_LOST_POINTS

        # Aggiorna UserGames e Stats del giudice
        cursor.execute("""
            UPDATE UserGames SET is_won = %s, points = %s
            WHERE game_id = %s AND player_id = %s
        """, (is_won, judge_points, game_id, players["judge"]))
        
        cursor.execute("""
            UPDATE Stats
            SET n_games = n_games + 1,
                score_judge = score_judge + %s,
                won_judge = won_judge + %s,
                lost_judge = lost_judge + %s
            WHERE user_id = %s
        """, (
            judge_points,
            1 if is_won else 0,
            0 if is_won else 1,
            players["judge"]
        ))

        # Aggiorna UserGames e Stats del partecipante
        participant_id: int = players["participant"]
        participant_won: bool = not is_won if participant_is_ai else is_won
        participant_points: int = PART_WON_POINTS if participant_won else PART_LOST_POINTS

        cursor.execute("""
            UPDATE UserGames SET is_won = %s, points = %s
            WHERE game_id = %s AND player_id = %s
        """, (participant_won, participant_points, game_id, participant_id))

        cursor.execute("""
            UPDATE Stats
            SET n_games = n_games + 1,
                score_part = score_part + %s,
                won_part = won_part + %s,
                lost_part = lost_part + %s
            WHERE user_id = %s
        """, (
            participant_points,
            1 if participant_won else 0,
            0 if participant_won else 1,
            participant_id
        ))

        connection.commit()

        return EndPendingJudgeGameOutput(
            game_id=game_id,
            is_won=is_won,
            message=message,
            points=judge_points
        )

    except mariadb.Error as e:
        raise HTTPException(status_code=500, detail="Errore del server.")
    
    finally:
        close_cursor(cursor)
        close_connection(connection)