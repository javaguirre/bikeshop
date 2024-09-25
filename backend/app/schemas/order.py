from pydantic import BaseModel, ConfigDict


class OrderResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: int
    total_price: float
    available_options: dict[int, list[int]]


class CreateOrderPayload(BaseModel):
    product_id: int


class UpdateOrderPayload(BaseModel):
    option_id: int
