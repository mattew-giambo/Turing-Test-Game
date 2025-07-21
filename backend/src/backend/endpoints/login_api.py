from fastapi import HTTPException
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.security import verify_password
from models.authentication import UserLogin, LoginResponse
import mariadb
from typing import Tuple, Dict

def login_api(user: UserLogin) -> LoginResponse:
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id, user_name, hashed_password FROM Users WHERE email = %s"
        cursor.execute(query, (user.email,))
        result: Tuple[int, str, str] = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Utente non trovato")

        user_id: int = result[0]
        user_name: str = result[1]
        hashed_password: str = result[2]

        if not verify_password(user.password, hashed_password):
            raise HTTPException(status_code=401, detail="Password errata")

        return LoginResponse(
            message="ok",
            user_id=user_id,
            user_name=user_name
        )

    except mariadb.Error:
        raise HTTPException(status_code=500, detail="Errore durante il login")

    finally:
        close_cursor(cursor)
        close_connection(connection)