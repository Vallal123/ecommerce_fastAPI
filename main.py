from fastapi import Depends, FastAPI, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from decimal import Decimal

from auth import admin_required, create_access_token
from database import Base, engine, get_db
from models.product import (CategoryCreate, CategoryTable, ProductCreate,
                            ProductTable, ProductResponse, CategoryResponse)
from models.user import UserLogin, UserRegister, UserTable, UserResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(UserTable).filter(UserTable.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = UserTable(
        name=user.name,
        email=user.email,
        phone=user.phone,
        address=user.address,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"{user.email} registered successfully"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserTable).filter(UserTable.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/category", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db), admin = Depends(admin_required)):
    existing = db.query(CategoryTable).filter(CategoryTable.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    new_category = CategoryTable(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@app.post("/product", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db), admin = Depends(admin_required)):
    category = db.query(CategoryTable).filter(CategoryTable.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")
    new_product = ProductTable(
        name=product.name,
        price=product.price,
        available_qty=product.available_qty,
        category_id=product.category_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.get("/products", response_model=list[ProductResponse])
def list_products(price: Decimal = None, category_id: int = None, db: Session = Depends(get_db)):
    query = db.query(ProductTable)

    if price is not None:
        query = query.filter(ProductTable.price <= price)
    
    if category_id is not None:
        query = query.filter(ProductTable.category_id == category_id)

    products = query.all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    return products

@app.get("/products/{id}", response_model=ProductResponse)
def get_product(id: int, db: Session = Depends(get_db)):
    item = db.query(ProductTable).filter(ProductTable.id).first()

    if not item:
        return HTTPException(status_code=404, detail="No item found")
    
    return item
