import mariadb
from fastapi import HTTPException

def close_cursor(cursor: mariadb.Cursor) -> None:
    """
    Chiude in modo sicuro il cursore del database MariaDB.

    Args:
        cursor (mariadb.Cursor): Il cursore attivo da chiudere.

    Raises:
        HTTPException: Se si verifica un errore durante la chiusura del cursore.
    """
    try:
        cursor.close()
    except mariadb.Error:
        raise HTTPException(
            status_code=500,
            detail="Errore nella chiusura del cursore del database."
        )