from fastapi import HTTPException
from models.user_info import UserInfo
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor

def get_user_info_api(user_id: int):
    connection = connect_to_database()
    cursor = get_cursor(connection) 
    
    cursor.execute("""
                   SELECT user_name, email
                   FROM Users
                   WHERE id = %s
                   """, (user_id,))
    result = cursor.fetchone()

    if result is None:
        raise HTTPException(
            status_code= 404,
            detail= "Utente non trovato"
        )
    close_cursor(cursor)
    close_connection(connection)

    return UserInfo(
        id= user_id,
        user_name= result[0],
        email= result[1]
    )