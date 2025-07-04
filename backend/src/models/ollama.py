from pydantic import BaseModel
from typing import List

class OllamaMessage(BaseModel):
    role: str
    content: str

class OllamaInput(BaseModel):
    model: str
    messages: List[OllamaMessage]
    stream: bool