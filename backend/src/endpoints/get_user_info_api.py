from fastapi import HTTPException
import mariadb

from models.user_info import UserInfo
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.close_cursor import close_cursor
from utility.close_connection import close_connection

def get_user_info_api(user_id: int) -> UserInfo:
    """
    Recupera le informazioni di base associate a un utente tramite il suo ID.
    I dati includono il nome utente e l'indirizzo email registrato.

    Args:
        user_id (int): L'ID univoco dell'utente di cui recuperare le informazioni.

    Returns:
        UserInfo: Oggetto contenente nome utente ed email.

    Raises:
        HTTPException: 
            - 404: Se l'utente non è presente nel database.
            - 500: In caso di errore interno al database.
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