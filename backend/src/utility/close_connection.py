import mariadb
from fastapi import HTTPException

def close_connection(connection: mariadb.Connection) -> None:
    """ 
        Effettua la disconnessione al database di mariadb

        Args
            - `connection`: mariadb.Connection
    """
    try:
        connection.close()
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore nella chiusura della connessione"
        )
    return None