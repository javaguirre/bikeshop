from typing import List
from backend.app.models.product import Product
from backend.app.schemas.product import ProductCreate
from backend.app.services.product_service import ProductService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models.base import get_db


router = APIRouter()


@router.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.create_product(product)


@router.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    product: Product | None = product_service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products/", response_model=list[Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    products: List[Product] = product_service.get_products(skip=skip, limit=limit)
    return products
