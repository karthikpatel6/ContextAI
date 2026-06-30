from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    username : str
    email : EmailStr
    full_name : str
    password : str