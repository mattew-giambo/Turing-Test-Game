from typing import List
from pydantic import BaseModel

class ParticipantGameOutput(BaseModel):
    questions: List[str]

class QADict(BaseModel):
    question: str
    answer: str
    ai_question: bool
    ai_answer: bool

class AnswerInput(BaseModel):
    answers: List[str]

class ResponseSubmit(BaseModel):
    status: str