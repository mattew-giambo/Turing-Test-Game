from pydantic import BaseModel

class ParticipantGameOutput(BaseModel):
    question_1: str
    question_2: str
    question_3: str
