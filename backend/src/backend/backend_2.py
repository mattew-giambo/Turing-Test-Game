from typing import Dict, Tuple
from fastapi import FastAPI, HTTPException
from models.user_info import UserInfo
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
from utility.security import hash_password, verify_password
from models.authentication import UserRegister, UserLogin
from models.response_models import RegisterResponse, LoginResponse
import mariadb

app = FastAPI()

@app.post("/register", response_model=RegisterResponse)
def register(user: UserRegister) -> RegisterResponse:
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id FROM Users WHERE email = ? OR user_name = ?"
        cursor.execute(query, (user.email, user.user_name))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Utente già registrato con questa email o username")

        hashing = hash_password(user.password)

        query = "INSERT INTO Users (user_name, email, hashed_password) VALUES (?, ?, ?)"
        cursor.execute(query, (user.user_name, user.email, hashing))
        connection.commit()

        user_id = cursor.lastrowid

        query = "INSERT INTO Stats (user_id) VALUES (?)"
        cursor.execute(query, (user_id,))
        connection.commit()

        return RegisterResponse(message="Registrazione avvenuta con successo", user_id=user_id)

    except mariadb.Error:
        raise HTTPException(status_code=500, detail="Errore durante la registrazione")

    finally:
        close_cursor(cursor)
        close_connection(connection)

sessioni_attive: Dict[int, Dict[str, str]] = {}

@app.post("/login", response_model=LoginResponse)
def login(user: UserLogin) -> LoginResponse:
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query: str = "SELECT id, user_name, hashed_password FROM Users WHERE email = ?"
        cursor.execute(query, (user.email,))
        result: Tuple[int, str, str] = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Utente non trovato")

        user_id: int = result[0]
        user_name: str = result[1]
        hashed_password: str = result[2]

        if not verify_password(user.password, hashed_password):
            raise HTTPException(status_code=401, detail="Password errata")

        sessioni_attive[user_id] = {
            "user_name": user_name,
            "email": user.email
        }

        return LoginResponse(
            message="Login riuscito",
            user_id=user_id,
            user_name=user_name
        )

    except mariadb.Error:
        raise HTTPException(status_code=500, detail="Errore durante il login")

    finally:
        close_cursor(cursor)
        close_connection(connection)