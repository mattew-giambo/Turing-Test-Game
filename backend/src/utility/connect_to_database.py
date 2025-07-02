import mariadb
from fastapi import HTTPException

def connect_to_database() -> mariadb.Connection:
    """ 
        Effettua la connessione al database di mariadb

        Return
            - `connection`: mariadb.Connection
    """
    HOST = "127.0.0.1"
    PORT = 3307
    USER = "user_db"
    USER_PASSWORD = "userpassword"
    DATABASE_NAME = "turing_db"

    connection: mariadb.Connection
    try:
        connection = mariadb.connect(
            host= HOST,
            port= PORT,
            user= USER,
            password= USER_PASSWORD,
            database= DATABASE_NAME
        )
    except mariadb.Error as e:
        raise HTTPException(
            status_code= 500,
            detail= "Errore nella connessione al database"
        )
    return connection