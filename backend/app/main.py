from fastapi import FastAPI
from app.api import products, parts, orders
from app.database import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(products.router)
app.include_router(parts.router)
app.include_router(orders.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Marcus's Bicycle Shop API"}
