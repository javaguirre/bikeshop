from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import orders, products
from backend.app.models import Base, engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(products.router)
app.include_router(orders.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Marcus's Bicycle Shop API"}
