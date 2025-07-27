from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    user_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class RegisterResponse(BaseModel):
    user_id: int

class LoginResponse(BaseModel):
    user_id: int
    user_name: str
    email: EmailStr