import mariadb
from fastapi import HTTPException

def close_cursor(cursor: mariadb.Cursor) -> None:
    """ 
        Chiude il cursore di mariadb

        Return
        `None`
    """
    try:
        cursor.close()
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore nella chiusura del cursore"
        )

    return None