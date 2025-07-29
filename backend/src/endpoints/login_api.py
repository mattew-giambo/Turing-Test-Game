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
    Esegue l'autenticazione dell'utente sulla base dell'email e della password forniti.
    Verifica l'esistenza dell'utente e la corrispondenza dell'hash della password.
    
    Args:
        user (UserLogin): Oggetto contenente email e password dell'utente.

    Returns:
        LoginResponse: Oggetto con messaggio di successo, ID e username dell’utente autenticato.

    Raises:
        HTTPException:
            - 404 se l'utente non è registrato con l'email fornita.
            - 401 se la password non è corretta.
            - 500 in caso di errore interno durante l’accesso al database.
    """
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id, email, hashed_password FROM Users WHERE user_name = %s"
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

    except mariadb.Error:
        raise HTTPException(status_code=500, detail="Errore durante il login")

    finally:
        close_cursor(cursor)
        close_connection(connection)