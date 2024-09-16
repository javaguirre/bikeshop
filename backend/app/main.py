from fastapi import FastAPI

from backend.app.api import orders, products
from backend.app.models import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(products.router)
app.include_router(orders.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Marcus's Bicycle Shop API"}
