from typing import Dict
from pydantic import BaseModel

class QA(BaseModel):
    question: str
    answer: str

class GameReviewOutput(BaseModel):
    game_id: int
    session: Dict[int, QA]