import mariadb
from fastapi import HTTPException

def get_cursor(connection: mariadb.Connection) -> mariadb.Cursor:
    """ 
        Restituisce il cursore per effettuare le query

        Return
            - `connection`: mariadb.Connection
    """
    try:
        cursor = connection.cursor()
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore nell'apertura del cursore"
        )

    return cursor