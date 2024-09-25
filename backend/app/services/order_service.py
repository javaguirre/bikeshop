from typing import List
from backend.app.models.product import Order, Product
from backend.app.repositories.pricing_repository import PricingOrderRepository
from backend.app.schemas.order import OrderResponse
from backend.app.services.base import (
    BaseOrderService,
    BasePriceService,
    BaseSelectionService,
)
from ..models.product import Option, PriceRule


class CartOrderService(BaseOrderService):
    def __init__(
        self,
        repository: PricingOrderRepository,
        part_service: BaseSelectionService,
        price_service: BasePriceService,
    ):
        self.repository = repository
        self.part_service = part_service
        self.price_service = price_service

    def create_order(self, product: Product) -> OrderResponse:
        order: Order = self.repository.create_order(
            Order(product=product, total_price=0, status="pending")
        )

        total_price = 0
        available_options = self.part_service.get_available_options(order.product_id)

        return OrderResponse(
            id=order.id,
            total_price=total_price,
            available_options=available_options,
        )

    def update_order(self, order: Order, option: Option) -> OrderResponse:
        options: List[Option] = self.repository.get_options(order.product_id)

        if not self.part_service.select_part_option(option):
            raise ValueError("Option is not valid")

        order.options.append(option)
        self.repository.update_order(order)

        current_option_ids = [option.id for option in order.options]

        rules: list[PriceRule] = self.repository.get_price_rules_by_option_ids(
            current_option_ids
        )

        total_price: float = self.price_service.calculate_price(options, rules)
        available_options = self.part_service.get_available_options(order.product_id)

        return OrderResponse(
            id=order.id, total_price=total_price, available_options=available_options
        )
