from itertools import groupby
from operator import attrgetter
from typing import List
from sqlalchemy.sql.schema import Column
from backend.app.models.product import Order, Product
from backend.app.repositories.pricing_repository import PricingOrderRepository
from backend.app.schemas.order import OrderResponse
from ..models.product import Option, OptionCompatibility, PriceRule


# TODO: Interface
class OrderService:
    def __init__(self, repository: PricingOrderRepository):
        self.repository = repository

    def create_order(self, product: Product) -> OrderResponse:
        order: Order = self.repository.create_order(
            Order(product=product, total_price=0)
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
        conditions: List[OptionCompatibility] = (
            self.repository.get_option_compatibilities(options)
        )

        if not self._have_valid_options_with_current_order(
            order.options + [option], conditions
        ):
            raise ValueError("Option is not compatible with the order")

        order.options.append(option)
        self.repository.update_order(order)

        total_price: float = self.calculate_price(order)
        product_available_options: list[Option] = self.repository.get_options(
            order.product_id
        )

        available_options: dict[int, list[int]] = self._format_available_options(
            self.get_available_options(
                product_available_options, order.options, conditions
            )
        )

        return OrderResponse(
            id=order.id, total_price=total_price, available_options=available_options
        )

    def get_available_options(
        self,
        options: list[Option],
        order_options: list[Option],
        conditions: list[OptionCompatibility],
    ) -> list[Option]:
        return [
            option
            for option in options
            if self._is_valid_option_with_current_order(
                option, order_options, conditions
            )
        ]

    def _is_valid_option_with_current_order(
        self,
        option: Option,
        order_options: list[Option],
        conditions: list[OptionCompatibility],
    ) -> bool:
        # TODO
        return True

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

            total_price += self._get_valid_price(option, rules, current_option_ids)

        return total_price

    def _has_rules(self, option: Option, rules: list[PriceRule]):
        return any(rule.option_id == option.id for rule in rules)

    def _get_valid_price(
        self, option: Option, rules: list[PriceRule], current_option_ids
    ) -> float:
        """
        Get the valid price of an option based on the current order and the new option.
        """
        return self._get_price_with_rules(option, rules, current_option_ids)

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

    def _have_valid_options_with_current_order(
        self,
        options: list[Option],
        conditions: list[OptionCompatibility],
    ):
        if len(options) <= 1:
            return True

        current_option_ids: list[int] = [option.id for option in options]

        # Check compatibility for the options with the new option
        option_conditions = self._get_option_compatibilities(
            current_option_ids, conditions
        )

        if not option_conditions:
            return True  # If no conditions, the option is always valid

        for condition in option_conditions:
            if condition.include_exclude == "include":
                if condition.compatible_option_id not in current_option_ids:
                    return False
            elif condition.include_exclude == "exclude":
                if condition.compatible_option_id in current_option_ids:
                    return False

        return True

    def _get_option_compatibilities(
        self, option_ids: list[int], compatibilities: list[OptionCompatibility]
    ) -> List[OptionCompatibility]:
        return [
            compatibility
            for compatibility in compatibilities
            if compatibility.option_id in option_ids
            or compatibility.compatible_option_id in option_ids
        ]
