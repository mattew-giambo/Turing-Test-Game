from pydantic import BaseModel

class JudgeGameInput(BaseModel):
    question_1: str
    question_2: str
    question_3: str

class JudgeGameOutput(BaseModel):
    answer_1: str
    answer_2: str
    answer_3: str