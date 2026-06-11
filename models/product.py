from pydantic import BaseModel, field_validator
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class CategoryTable(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    products = relationship("ProductTable", back_populates="category")

class ProductTable(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(DECIMAL)
    available_qty = Column(Integer)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("CategoryTable", back_populates="products")

class ProductCreate(BaseModel):
    name: str
    price: float
    available_qty: int
    category_id: int

    @field_validator("price")
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("price must be positive")
        return v
    
    @field_validator("available_qty")
    def qty_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("quantity must be positive")
        return v
    

class CategoryCreate(BaseModel):
        name: str
