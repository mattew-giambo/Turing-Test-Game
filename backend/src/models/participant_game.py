from typing import List
from pydantic import BaseModel

class ParticipantGameOutput(BaseModel):
    questions: List[str]

class AnswerInput(BaseModel):
    answers: List[str]

class ResponseSubmit(BaseModel):
    status: str