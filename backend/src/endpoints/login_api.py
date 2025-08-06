from fastapi import HTTPException
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.security import verify_password
from models.authentication import UserLogin, LoginResponse
import mariadb
from typing import Optional, Tuple

def login_api(user: UserLogin) -> LoginResponse:
    """
    Autentica un utente sulla base dello username e della password forniti.

    Recupera l'utente dal database, verifica la correttezza della password e,
    in caso di successo, restituisce i dati essenziali del profilo.

    Args:
        user (UserLogin): Dati dell’utente in fase di login (username e password).

    Returns:
        LoginResponse: Oggetto contenente l'ID, username e email dell'utente autenticato.

    Raises:
        HTTPException:
            - 404 se lo username non esiste nel sistema.
            - 401 se la password è errata o non verificabile.
            - 500 in caso di errore interno durante l'accesso al database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = """
            SELECT id, email, hashed_password
            FROM Users
            WHERE user_name = %s
        """
        cursor.execute(query, (user.user_name,))
        result: Optional[Tuple[int, str, str]] = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Utente non trovato")

        user_id: int = result[0]
        email: str = result[1]
        hashed_password: str = result[2]

        if not verify_password(user.password, hashed_password):
            raise HTTPException(status_code=401, detail="Password errata")

        return LoginResponse(
            user_id= user_id,
            user_name= user.user_name,
            email= email
        )

    except mariadb.Error as e:
        raise HTTPException(
            status_code=500,
            detail="Errore durante il login"
        )

    finally:
        close_cursor(cursor)
        close_connection(connection)