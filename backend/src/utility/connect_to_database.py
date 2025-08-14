import mariadb
from fastapi import HTTPException
from config.constants import HOST_DB, PORT_DB, USER_DB, DATABASE_NAME_DB, USER_PASSWORD_DB

def connect_to_database() -> mariadb.Connection:
    """
    Stabilisce una connessione al database MariaDB utilizzando i parametri di configurazione.

    Returns:
        mariadb.Connection: Oggetto connessione attivo verso il database.

    Raises:
        HTTPException: 
            - 500: In caso di errore interno durante l’accesso al database.
    """
    try:
        connection: mariadb.Connection = mariadb.connect(
            host= HOST_DB,
            port= PORT_DB,
            user= USER_DB,
            password= USER_PASSWORD_DB,
            database= DATABASE_NAME_DB
        )
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore nella connessione al database"
        )
    return connection