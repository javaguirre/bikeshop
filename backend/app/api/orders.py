from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models.base import get_db
from backend.app.models.product import Option, Order, Product
from backend.app.repositories.pricing_repository import PricingOrderRepository
from backend.app.schemas.order import (
    CreateOrderPayload,
    OrderResponse,
    UpdateOrderPayload,
)
from backend.app.services.order_service import OrderService

router = APIRouter()


@router.post("/orders", response_model=OrderResponse)
def create_product(
    payload: CreateOrderPayload,
    db: Session = Depends(get_db),
):
    repository = PricingOrderRepository(db)
    order_service = OrderService(repository)

    try:
        product: Product = repository.get_product(payload.product_id)
        return order_service.create_order(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/orders/{order_id}", response_model=Order)
def update_order(
    payload: UpdateOrderPayload, order_id: int, db: Session = Depends(get_db)
):
    repository = PricingOrderRepository(db)
    order_service = OrderService(repository)

    try:
        order: Order = repository.get_order(order_id)
        option: Option = repository.get_option(payload.option_id)
        return order_service.update_order(order, option)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
