from fastapi import HTTPException
from models.participant_game import AnswerInput, ResponseSubmit
from utility.close_connection import close_connection
from utility.close_cursor import close_cursor
from utility.connect_to_database import connect_to_database
from utility.get_cursor import get_cursor
import mariadb

def submit_answers_api(game_id: int, input_data: AnswerInput):
    if len(input_data.answers) != 3:
        raise HTTPException(status_code=422, detail="Devono essere fornite esattamente tre risposte")
    
    connection: mariadb.Connection = connect_to_database()
    cursor: mariadb.Cursor = get_cursor(connection)

    try:
        query:str = "SELECT id FROM Games WHERE id = %s AND is_terminated = FALSE"
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Partita non trovata o già terminata.")
        
        query: str = "UPDATE Q_A SET answer = %s WHERE game_id = %s AND question_id = %s"

        for idx, answer in enumerate(input_data.answers, start=1):  
            cursor.execute(query, (answer.strip(), game_id, idx))

        connection.commit()
        return ResponseSubmit(status="ok")

    except mariadb.Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Errore durante l'aggiornamento delle risposte: {e}")

    finally:
        close_cursor(cursor)
        close_connection(connection)