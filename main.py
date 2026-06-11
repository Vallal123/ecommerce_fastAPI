from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models.user import UserTable, UserRegister, UserLogin
from models.product import ProductTable, CategoryTable, ProductCreate, CategoryCreate
from auth import create_access_token, admin_required
from passlib.context import CryptContext

Base.metadata.create_all(bind=engine)

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/register")
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

@app.post("/category")
def create_category(category: CategoryCreate, db: Session = Depends(get_db), admin = Depends(admin_required)):
    existing = db.query(CategoryTable).filter(CategoryTable.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    new_category = CategoryTable(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@app.post("/product")
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