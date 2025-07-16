from fastapi import HTTPException
from models.user_stats import UserStats
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor

def get_user_stats_api(user_id: int):
    connection = connect_to_database()
    cursor = get_cursor(connection)

    cursor.execute("""
        SELECT user_id, n_games, score_part, score_judge, won_part, won_judge, lost_part, lost_judge
        FROM stats
        WHERE user_id = %s
    """, (user_id,))
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(
            status_code= 404,
            detail= "Utente non trovato!"
        )
    
    close_cursor(cursor)
    close_connection(connection)
    
    return UserStats(
        user_id= result[0],
        n_games= result[1],
        score_part= result[2],
        score_judge= result[3], 
        won_part= result[4], 
        won_judge= result[5], 
        lost_part= result[6], 
        lost_judge= result[7]
    )