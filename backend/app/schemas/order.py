from pydantic import BaseModel


class OrderResponse(BaseModel):
    id: int
    total_price: float
    available_options: dict[int, list[int]]

    class Config:
        orm_mode = True


class CreateOrderPayload(BaseModel):
    product_id: int


class UpdateOrderPayload(BaseModel):
    option_id: int
