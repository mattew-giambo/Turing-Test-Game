from fastapi import HTTPException
import mariadb
from models.user_info import UserInfo
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor

def get_user_info_api(user_id: int):
    """
    Restituisce le informazioni anagrafiche di un utente dato il suo ID.
    Utilizzata per recuperare il profilo utente all’interno del gioco.

    Args:
        user_id (int): L'identificativo numerico univoco dell'utente.

    Returns:
        UserInfo: Oggetto contenente nome utente e email.

    Raises:
        HTTPException: Se l'utente non esiste o si verifica un errore nel database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = """
            SELECT user_name, email
            FROM Users
            WHERE id = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Utente non trovato"
            )

        return UserInfo(
            id=user_id,
            user_name=result[0],
            email=result[1]
        )

    except mariadb.Error:
        raise HTTPException(
            status_code=500,
            detail="Errore durante l'accesso al database"
        )

    finally:
        close_cursor(cursor)
        close_connection(connection)