from fastapi import HTTPException
from models.judge_game import JudgeGameAnswer
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb
from config.constants import JUDGE_WON_POINTS, PART_WON_POINTS

from models.pending_game import EndPendingGame

def end_pending_game_api(judge_answer: JudgeGameAnswer, game_id: int):
    player_id = judge_answer.player_id
    is_won: bool = False
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

        if players["judge"] != player_id:
            raise HTTPException(status_code= 403,
                                detail= "Un partecipante non può giudicare")
        
        if players["participant"] == 1 and judge_answer.is_ai == True:
            cursor.execute("UPDATE games SET result = 'win', terminated= TRUE WHERE id = %s", (game_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_judge = score_judge + %s,
                    won_judge = won_judge + 1
                WHERE user_id = %s
            """, (JUDGE_WON_POINTS, player_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    lost_part = lost_part + 1,
                WHERE user_id = 1
            """)
            is_won = True
        elif players["participant"] == 1 and judge_answer.is_ai == False:
            cursor.execute("UPDATE games SET result = 'loss', terminated= TRUE WHERE id = %s", (game_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    lost_judge = lost_judge + 1
                WHERE user_id = %s
            """, (player_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_part = score_part + %s,
                    won_part = won_part + 1
                WHERE user_id = 1
            """, (PART_WON_POINTS,))

        elif players["participant"] != 1 and judge_answer.is_ai == True:
            cursor.execute("UPDATE games SET result = 'loss', terminated= TRUE WHERE id = %s", (game_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    lost_judge = lost_judge + 1
                WHERE user_id = %s
            """, (player_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    lost_part = lost_part + 1
                WHERE user_id = %s
            """, (players["participant"],))
        else:
            cursor.execute("UPDATE games SET result = 'win', terminated= TRUE WHERE id = %s", (game_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_judge = score_judge + %s,
                    won_judge = won_judge + 1
                WHERE user_id = %s
            """, (JUDGE_WON_POINTS, player_id,))
            cursor.execute("""
                UPDATE stats
                SET n_games = n_games + 1,
                    score_part = score_part + %s,
                    won_part = won_part + 1
                WHERE user_id = %s
            """, (PART_WON_POINTS, players["participant"],))

            is_won = True

        connection.commit()
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore del server"
        )
    finally:
        close_cursor(cursor)
        close_connection(connection)

    return EndPendingGame(game_id= game_id, is_won = is_won, message= "Partita terminata, esito registrato con successo!")
