from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    user_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    message: str
    user_id: int

class LoginResponse(BaseModel):
    message: str
    user_id: int
    user_name: str