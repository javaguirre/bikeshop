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
        option_selector: BaseSelectionService,
        price_service: BasePriceService,
    ):
        self.repository = repository
        self.option_selector = option_selector
        self.price_service = price_service

    def create_order(self, product: Product, option: Option) -> OrderResponse:
        # We will cache this config in the future as it won't change a lot
        self.option_selector.load_compatibilities(
            self.repository.get_parts(product.id),
            self.repository.get_options(product.id),
            self.repository.get_compatibilities(product.id),
        )

        order: Order = self.repository.create_order(
            Order(product=product, total_price=0, status="pending")
        )
        order.options.append(option)
        self.repository.update_order(order)

        total_price = 0
        available_options = self.option_selector.get_available_options(order.product_id)

        return OrderResponse(
            id=order.id,
            total_price=total_price,
            available_options=available_options,
        )

    def update_order(self, order: Order, option: Option) -> OrderResponse:
        # We will cache this config in the future as it won't change a lot
        self.option_selector.load_compatibilities(
            self.repository.get_parts(product.id),
            self.repository.get_options(product.id),
            self.repository.get_compatibilities(product.id),
        )

        options: List[Option] = self.repository.get_options(order.product_id)

        if not self.option_selector.select_part_options([*order.options, option]):
            raise ValueError("Option is not valid")

        order.options.append(option)
        self.repository.update_order(order)

        current_option_ids = [option.id for option in order.options]

        rules: list[PriceRule] = self.repository.get_price_rules_by_option_ids(
            current_option_ids
        )

        total_price: float = self.price_service.calculate_price(options, rules)
        available_options = self.option_selector.get_available_options(order.product_id)

        return OrderResponse(
            id=order.id, total_price=total_price, available_options=available_options
        )
