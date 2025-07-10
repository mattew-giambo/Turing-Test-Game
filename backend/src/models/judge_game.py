from pydantic import BaseModel
from typing import List

class JudgeGameInput(BaseModel):
    questions_list: List[str]

class JudgeGameOutput(BaseModel):
    answers_list: List[str]

class JudgeGameAnswer(BaseModel):
    player_id: int
    is_ai: bool

class EndJudgeGameOutput(BaseModel):
    message: str
    is_won: bool