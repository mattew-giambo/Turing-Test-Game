from pydantic import BaseModel

class RegisterResponse(BaseModel):
    message: str
    user_id: int

class LoginResponse(BaseModel):
    message: str
    user_id: int
    user_name: str