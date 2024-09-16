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
        available_options: List[dict[int, int]] = {
            option.part_id: option.id
            for option in self.repository.get_options(product.id)
        }

        return OrderResponse(
            order_id=order.id,
            total_price=total_price,
            available_options=available_options,
        )

    def update_order(self, order: Order, option: Option) -> OrderResponse:
        options: List[Option] = self.repository.get_options(order.product_id)
        conditions: List[OptionCompatibility] = (
            self.repository.get_option_compatibilities(options)
        )

        if not self._is_valid_option_with_current_order(
            order.options, conditions, option
        ):
            raise ValueError("Option is not compatible with the order")

        total_price: float = self.calculate_price(order)
        available_options: List[dict[int, int]] = {
            option.part_id: option.id
            for option in self.get_available_options(order, options, conditions)
        }

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

    def get_available_options(
        self, order: Order, options: list[Option], conditions: list[OptionCompatibility]
    ) -> list[Option]:
        """
        Get the available options for the current order.
        """
        return list(
            filter(
                lambda option: self._is_valid_option_with_current_order(
                    order.options, conditions, option
                ),
                options,
            )
        )

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

    def _is_valid_option_with_current_order(
        self,
        order_options: list[Option],
        conditions: list[OptionCompatibility],
        option: Option,
    ):
        for option in order_options:
            option_conditions: List[OptionCompatibility] = (
                self._get_option_compatibitilies(option, conditions)
            )

            if not option_conditions:
                return True

            else:
                return self._is_option_compatible_with_order(
                    option, option_conditions, order_options
                )

    def _get_option_compatibitilies(
        self, option: Option, compatibilities: list[OptionCompatibility]
    ) -> List[OptionCompatibility]:
        option_compatibilities: List[OptionCompatibility] = [
            compatibility
            for compatibility in compatibilities
            if compatibility.option_id == option.id
        ]

        # If a part from this option has other compatibilities, we need to check them
        option_compatibilities += [
            compatibility
            for compatibility in compatibilities
            if compatibility.option.part_id == option.part_id
        ]

        return option_compatibilities

    def _is_option_compatible_with_order(
        self,
        option: Option,
        compatibilities: list[OptionCompatibility],
        order_options: list[Option],
    ):
        order_option_ids = {opt.id for opt in order_options}

        for compatibility in compatibilities:
            if compatibility.option_id == option.id:
                if compatibility.include_exclude == "include":
                    if compatibility.compatible_option_id not in order_option_ids:
                        return False
                elif compatibility.compatible_option_id in order_option_ids:
                    return False
            elif compatibility.compatible_option.part_id == option.part_id:
                if compatibility.include_exclude == "exclude":
                    if compatibility.compatible_option_id == option.id:
                        return False
                elif compatibility.compatible_option_id != option.id:
                    return False

        return True
