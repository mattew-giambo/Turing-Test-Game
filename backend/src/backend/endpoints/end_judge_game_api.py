from fastapi import HTTPException
from models.judge_game import JudgeGameAnswer, EndJudgeGameOutput
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from config.constants import JUDGE_WON_POINTS, JUDGE_LOST_POINTS, PART_WON_POINTS, PART_LOST_POINTS
from typing import Dict

def end_judge_game_api(judge_answer: JudgeGameAnswer, game_id: int, active_judge_games: Dict):
    if game_id not in active_judge_games.keys():
        raise HTTPException(status_code=404, detail="Partita non trovata")
    
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

        cursor.execute("UPDATE games SET terminated= TRUE WHERE id = %s", (game_id,))

        # VERIFICO ESITO
        is_won: bool
        points: int = 0
        message: str
        if judge_answer.is_ai == active_judge_games[game_id]["opponent_ai"]:
            # IL GIUDICE HA VINTO
            cursor.execute("UPDATE UserGames SET is_won = TRUE, points = %s WHERE game_id = %s AND player_id = %s", (JUDGE_WON_POINTS, game_id, player_id))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_judge = score_judge + %s,
                    won_judge = won_judge + 1
                WHERE user_id = %s
            """, (JUDGE_WON_POINTS, player_id,))

            if active_judge_games[game_id]["opponent_ai"]:
                # SE L'OPPONENT E' AI ALLORA RESGISTRO UNA SCONFITTA
                cursor.execute("UPDATE UserGames SET is_won = FALSE, points = %s WHERE game_id = %s AND player_id = %s", (PART_LOST_POINTS, game_id, 1))
                cursor.execute("""
                    UPDATE stats
                    SET n_games = n_games + 1,
                        lost_part = lost_part + 1,
                        score_part = score_part + %s
                    WHERE user_id = %s
                """, (PART_LOST_POINTS, 1,))

            is_won= True
            points = JUDGE_WON_POINTS
            message= "Congratulazioni hai vinto!"
        else:
            # IL GIUDICE HA PERSO
            cursor.execute("UPDATE UserGames SET is_won = = FALSE, points = %s WHERE game_id = %s AND player_id = %s", (JUDGE_LOST_POINTS, game_id, player_id))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    lost_judge = lost_judge + 1
                    score_judge = score_judge + %s,
                WHERE user_id = %s
            """, (JUDGE_LOST_POINTS, player_id,))

            if active_judge_games[game_id]["opponent_ai"]:
                # SE L'OPPONENT E' AI ALLORA RESGISTRO UNA VITTORIA
                cursor.execute("UPDATE UserGames SET is_won = TRUE, points = %s WHERE game_id = %s AND player_id = %s", (PART_WON_POINTS, game_id, 1))
                cursor.execute("""
                    UPDATE stats
                    SET n_games = n_games + 1,
                        won_part = won_part + 1,
                        score_part = score_part + %s
                    WHERE user_id = %s
                """, (PART_LOST_POINTS, 1))

            is_won = False
            points = JUDGE_LOST_POINTS
            message= "Ooohh Noo, hai perso!"
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

    return EndJudgeGameOutput(message= message, is_won= is_won, points= points)