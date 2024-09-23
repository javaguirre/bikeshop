from abc import ABC, abstractmethod
from itertools import groupby
from operator import attrgetter
from typing import List
from sqlalchemy.sql.schema import Column
from backend.app.models.product import Order, Product
from backend.app.repositories.pricing_repository import PricingOrderRepository
from backend.app.schemas.order import OrderResponse
from backend.app.services.part_service import PartService
from ..models.product import Option, OptionCompatibility, PriceRule


class OrderService(ABC):
    @abstractmethod
    def create_order(self, product: Product) -> OrderResponse:
        pass

    @abstractmethod
    def update_order(self, order: Order, option: Option) -> OrderResponse:
        pass


class CartOrderService(OrderService):
    def __init__(
        self, repository: PricingOrderRepository, selector_solver: PartService
    ):
        self.repository = repository
        self.selector_solver = selector_solver

    def create_order(self, product: Product) -> OrderResponse:
        order: Order = self.repository.create_order(
            Order(product=product, total_price=0, status="pending")
        )

        total_price = 0
        options: List[Option] = self.repository.get_options(product.id)
        available_options: dict[int, list[int]] = self._format_available_options(
            options
        )

        return OrderResponse(
            id=order.id,
            total_price=total_price,
            available_options=available_options,
        )

    def update_order(self, order: Order, option: Option) -> OrderResponse:
        options: List[Option] = self.repository.get_options(order.product_id)

        # TODO: Validate with solver

        order.options.append(option)
        self.repository.update_order(order)

        total_price: float = self.calculate_price(order)
        product_available_options: list[Option] = self.repository.get_options(
            order.product_id
        )

        available_options: dict[int, list[int]] = self._format_available_options(
            # TODO all
            []
        )

        return OrderResponse(
            id=order.id, total_price=total_price, available_options=available_options
        )

    def calculate_price(self, order: Order) -> float:
        """
        Calculate the price of an option based on the current order and the new option.
        """
        current_option_ids = [option.id for option in order.options]
        rules: list[PriceRule] = self.repository.get_price_rules_by_option_ids(
            current_option_ids
        )

        return self._calculate_price_by_options(order.options, rules)

    def _format_available_options(self, options: list[Option]) -> dict[int, list[int]]:
        return {
            part_id: list(map(attrgetter("id"), group))
            for part_id, group in groupby(
                sorted(options, key=attrgetter("part_id")), key=attrgetter("part_id")
            )
        }

    def _calculate_price_by_options(
        self, options: list[Option], rules: list[PriceRule]
    ) -> float:
        total_price = 0
        current_option_ids: list[Column[int]] = [option.id for option in options]

        for option in options:
            if not self._has_rules(option, rules):
                total_price += option.price
                continue

            total_price += self._get_price_with_rules(option, rules, current_option_ids)

        return total_price

    def _has_rules(self, option: Option, rules: list[PriceRule]):
        return any(rule.option_id == option.id for rule in rules)

    def _get_price_with_rules(
        self, option: Option, rules: list[PriceRule], current_option_ids: list[int]
    ) -> float:
        for rule in rules:
            current_rule_condition_option_ids = [
                condition.option_id for condition in rule.conditions
            ]

            # We get the first rule that matches
            if all(
                option_id in current_option_ids
                for option_id in current_rule_condition_option_ids
            ):
                return rule.price

        return option.price
