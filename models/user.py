from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import Column, Integer, String
from database import Base
import re

# SQLAlchemy model (table)
class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(String)
    password = Column(String)


#Pydantic model (validation)
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    password: str

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v
    
    @field_validator("phone")
    def phone_must_be_valid(cls, v):
        if not re.match(r"^\d{10}$", v):
            raise ValueError("Phone must be 10 digits")
        return v
    
    @field_validator("password")
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password cannot be longer than 72 characters")
        return v
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str