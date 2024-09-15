from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.models.base import get_db
from backend.app.models.product import Option, Order
from backend.app.repositories.pricing_repository import PricingOrderRepository
from backend.app.services.order_service import OrderService

router = APIRouter()


class OrderResponse(BaseModel):
    order: Order
    total_price: float
    available_options: list[Option]


class CreateOrderPayload(BaseModel):
    product_id: int


class UpdateOrderPayload(BaseModel):
    option_id: int


@router.post("/orders", response_model=OrderResponse)
def create_product(
    payload: CreateOrderPayload,
    db: Session = Depends(get_db),
):
    repository = PricingOrderRepository(db)
    order_service = OrderService(repository)
    return order_service.create_order(payload.product_id)


@router.put("/orders/{order_id}", response_model=Order)
def update_order(
    payload: UpdateOrderPayload, order_id: int, db: Session = Depends(get_db)
):
    repository = PricingOrderRepository(db)
    order_service = OrderService(repository)
    return order_service.update_order(order_id)
