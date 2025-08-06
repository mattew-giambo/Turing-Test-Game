import mariadb
from fastapi import HTTPException

def close_connection(connection: mariadb.Connection) -> None:
    """
    Chiude in modo sicuro la connessione al database MariaDB.

    Args:
        connection (mariadb.Connection): La connessione aperta al database.

    Raises:
        HTTPException: Se si verifica un errore durante la chiusura della connessione.
    """
    try:
        connection.close()
    except mariadb.Error:
        raise HTTPException(
            status_code=500,
            detail="Errore nella chiusura della connessione al database."
        )
