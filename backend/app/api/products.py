from app.schemas.product import Product, ProductCreate
from app.services.product_service import ProductService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models import get_db
from backend.app.services.order_service import OrderService
from backend.app.services.price_service import PricingService


router = APIRouter()


@router.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.create_product(product)


@router.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    product = product_service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products/", response_model=list[Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    products = product_service.get_products(skip=skip, limit=limit)
    return products


@router.post("/calculate-price")
def calculate_price(
    product_id: int, selected_options: dict[int, int], db: Session = Depends(get_db)
):
    pricing_service = PricingService(db)
    total_price = pricing_service.calculate_price(product_id, selected_options)
    return {"total_price": total_price}


@router.get("/option-price/{option_id}")
def get_option_price(option_id: int, db: Session = Depends(get_db)):
    pricing_service = PricingService(db)
    option_price = pricing_service.get_option_price(option_id)
    return {"option_price": option_price}


@router.post("/add-part")
def add_part(
    product_id: int,
    current_options: dict[int, int],
    new_part_id: int,
    new_option_id: int,
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)
    try:
        updated_options = order_service.validate_and_add_part(
            product_id, current_options, new_part_id, new_option_id
        )
        return {"updated_options": updated_options}
    except ValueError as e:
        return {"error": str(e)}


@router.get("/available-options")
def get_available_options(
    product_id: int, current_options: dict[int, int], db: Session = Depends(get_db)
):
    order_service = OrderService(db)
    available_options = order_service.get_available_options(product_id, current_options)
    return {"available_options": available_options}
