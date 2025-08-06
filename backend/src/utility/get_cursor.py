import mariadb
from fastapi import HTTPException

def get_cursor(connection: mariadb.Connection) -> mariadb.Cursor:
    """
    Restituisce un cursore attivo per eseguire query SQL sulla connessione fornita.

    Args:
        connection (mariadb.Connection): Oggetto connessione attiva al database.

    Returns:
        mariadb.Cursor: Oggetto cursore per esecuzione di comandi SQL.

    Raises:
        HTTPException: Errore HTTP 500 in caso di fallimento nella creazione del cursore.
    """
    try:
        cursor: mariadb.Cursor = connection.cursor()
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore nell'apertura del cursore"
        )

    return cursor