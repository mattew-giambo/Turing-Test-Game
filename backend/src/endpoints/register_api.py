from fastapi import HTTPException
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.security import hash_password
from models.authentication import UserRegister, RegisterResponse
import mariadb

def register_api(user: UserRegister) -> RegisterResponse:
    """
    Registra un nuovo utente nel sistema. La funzione verifica che l'email o lo username 
    non siano già presenti nel database. In caso contrario, esegue l'hashing della password 
    e salva i dati nelle tabelle `Users` e `Stats`.

    Args:
        user (UserRegister): Oggetto contenente username, email e password in chiaro dell'utente.

    Returns:
        RegisterResponse: Identificativo dell'utente registrato.

    Raises:
        HTTPException: 
            - 400 se l'utente è già registrato con la stessa email o username.
            - 500 in caso di errore interno al database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = """
            SELECT id FROM Users 
            WHERE email = %s OR user_name = %s
        """
        cursor.execute(query, (user.email, user.user_name))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Utente già registrato con questa email o username"
            )

        hashed_password: str = hash_password(user.password)

        query = """
            INSERT INTO Users (user_name, email, hashed_password)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user.user_name, user.email, hashed_password))
        connection.commit()

        user_id: int = cursor.lastrowid

        query = """
            INSERT INTO Stats (user_id)
            VALUES (%s)
        """
        cursor.execute(query, (user_id,))
        connection.commit()

        return RegisterResponse(user_id=user_id)
    
    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la registrazione: {e}"
        )

    finally:
        close_cursor(cursor)
        close_connection(connection)