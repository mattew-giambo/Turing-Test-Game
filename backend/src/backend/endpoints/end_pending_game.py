from fastapi import HTTPException
from models.judge_game import JudgeGameAnswer
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from config.constants import JUDGE_WON_POINTS, PART_WON_POINTS, PART_LOST_POINTS, JUDGE_LOST_POINTS

from models.pending_game import EndPendingJudgeGameOutput

def end_pending_game_api(judge_answer: JudgeGameAnswer, game_id: int):
    connection = connect_to_database()
    cursor = get_cursor(connection)

    try:
        cursor.execute("""SELECT ug.player_id, ug.player_role 
                    FROM Games as g JOIN UserGames as ug ON g.id = ug.game_id
                    WHERE g.terminated = FALSE AND g.id = game_id""")
        result = cursor.fetchall()

        if result is None:
            raise HTTPException(status_code= 404,
                                detail= "Partita non trovata")
        if len(result) < 2:
            raise HTTPException(status_code= 403,
                                detail= f"Nessuna partita con {game_id} è stata avviata")
        
        players = {p_role: p_id for p_id, p_role in result} # dizionario[ruolo: id] per salvare i due utenti
        
        cursor.execute("UPDATE games SET terminated= TRUE WHERE id = %s", (game_id,))
        
        is_won: bool = False
        message: str = ""
        points: int = 0
        if players["participant"] == 1 and judge_answer.is_ai == True:
            # IL PARTECIPANTE E' AI E IL GIUDICE INDOVINA e VINCE
            cursor.execute("UPDATE UserGames SET is_won = TRUE, points = %s WHERE game_id = %s AND player_id = %s", (JUDGE_WON_POINTS, game_id, players["judge"]))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_judge = score_judge + %s,
                    won_judge = won_judge + 1
                WHERE user_id = %s
            """, (JUDGE_WON_POINTS, players["judge"],))

            cursor.execute("UPDATE UserGames SET is_won = FALSE points = %s WHERE game_id = %s AND player_id = %s", (PART_LOST_POINTS, game_id, 1))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    lost_part = lost_part + 1,
                    score_part = score_part + %s
                WHERE user_id = %s
            """, (PART_LOST_POINTS, 1))
            is_won = True
            message = "Congratulazione, hai vinto!"
            points = JUDGE_WON_POINTS
        elif players["participant"] == 1 and judge_answer.is_ai == False:
            # IL PARTECIPANTE E' AI E IL GIUDICE SBAGLIA
            cursor.execute("UPDATE UserGames SET is_won = FALSE, points = %s WHERE game_id = %s AND player_id = %s", (JUDGE_LOST_POINTS, game_id, players["judge"]))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    lost_judge = lost_judge + 1
                    score_judge = score_judge + %s
                WHERE user_id = %s
            """, (JUDGE_LOST_POINTS, players["judge"]))

            cursor.execute("UPDATE UserGames SET is_won = TRUE, points = %s WHERE game_id = %s AND player_id = %s", (PART_WON_POINTS, game_id, 1))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_part = score_part + %s,
                    won_part = won_part + 1
                WHERE user_id = %s
            """, (PART_WON_POINTS, 1))

            message = "Ohh Noo, hai perso!"
            points = JUDGE_LOST_POINTS
        elif players["participant"] != 1 and judge_answer.is_ai == True:
            # IL PARTECIPANTE E' UMANO E IL GIUDICE SBAGLIA, QUINDI PERDONO ENTRAMBI
            cursor.execute("UPDATE UserGames SET is_won = FALSE, points = %s WHERE game_id = %s AND player_id = %s", (JUDGE_LOST_POINTS, game_id, players["judge"]))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    lost_judge = lost_judge + 1
                WHERE user_id = %s
            """, (JUDGE_LOST_POINTS, players["judge"]))

            cursor.execute("UPDATE UserGames SET is_won = FALSE, points = %s WHERE game_id = %s AND player_id = %s", (PART_LOST_POINTS, game_id, players["participant"]))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    lost_part = lost_part + 1,
                    score_part = score_part + %s
                WHERE user_id = %s
            """, (PART_LOST_POINTS, players["participant"]))

            message = "Ohh Noo, hai perso!"
            points = JUDGE_LOST_POINTS
        else:
            # IL PARTECIPANTE E' UMANO E IL GIUDICE VINCE
            cursor.execute("UPDATE UserGames SET is_won = TRUE, points = %s WHERE game_id = %s AND player_id = %s", (JUDGE_WON_POINTS, game_id, players["judge"]))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_judge = score_judge + %s,
                    won_judge = won_judge + 1
                WHERE user_id = %s
            """, (JUDGE_WON_POINTS, players["judge"],))

            cursor.execute("UPDATE UserGames SET is_won = TRUE, points = %s WHERE game_id = %s AND player_id = %s", (PART_WON_POINTS, game_id, players["participant"]))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_part = score_part + %s,
                    won_part = won_part + 1
                WHERE user_id = %s
            """, (PART_WON_POINTS, players["participant"],))

            is_won = True
            message = "Congratulazioni, hai vinto!"
            points = JUDGE_WON_POINTS
        connection.commit()
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore del server"
        )
    finally:
        close_cursor(cursor)
        close_connection(connection)

    return EndPendingJudgeGameOutput(game_id= game_id, is_won = is_won, message= message, points = points)
