from functools import reduce
from backend.app.repositories.pricing_repository import PricingOrderRepository
from ..models.product import Option, PriceRule


class OrderService:
    def __init__(self, repository: PricingOrderRepository):
        self.repository = repository

    def calculate_price(self, order_id: int, option_id: int) -> float:
        """
        Calculate the price of an option based on the current order and the new option.
        """

        # TODO Check the new part is valid with the current other options
        current_order = self.repository.get_order(order_id)

        return reduce(
            lambda x, y: x + y, map(self.get_valid_price, current_order.options)
        )

    def get_valid_price(self, option: Option) -> float:
        """
        Get the valid price of an option based on the current order and the new option.
        """

        rules: list[PriceRule] = self.repository.get_price_rule_by_option_id(option.id)

        if not rules:
            return option.price

        return self.get_price_with_rules(option, rules)

    def get_price_with_rules(self, option: Option, rules: list[PriceRule]) -> float:
        # TODO: How to get this here?
        current_option_ids = [option.id for option in current_options]

        for rule in rules:
            current_rule_condition_option_ids = [
                condition.option_id for condition in rule.conditions
            ]

            # TODO: What if we have a rule with more than these conditions? (e.g. [p1, p2] vs [p1, p2, p3])
            if current_rule_condition_option_ids in current_option_ids:
                return rule.price

        return option.price

    def validate_part(self, order_id: int, option_id: int) -> bool:
        """
        Validate if a new part can be added to the current configuration.
        """
        current_order = self.repository.get_order(order_id)
        current_options = current_order.options

        current_option_ids: list[int] = [option.id for option in current_options]

        conditions = self.repository.get_conditions_by_option_id(option_id)

        # TODO: Check
        for condition in conditions:
            if condition.include_exclude == "exclude":
                if any(
                    option.id in current_option_ids
                    for option in condition.compatible_options
                ):
                    return False
            else:
                # TODO: This is wrong
                if not any(
                    option.id in current_option_ids
                    for option in condition.compatible_options
                ):
                    return False

        return True
