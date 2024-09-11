from sqlalchemy.orm import Session
from typing import Dict
from backend.app.models.product import Product, Option, PriceRule, PriceRuleCondition


class PricingService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_price(
        self, product_id: int, selected_options: Dict[int, int]
    ) -> float:
        """
        Calculate the final price of a product with selected options.

        :param product_id: ID of the product
        :param selected_options: Dict of {part_id: option_id} for selected options
        :return: Final price
        """
        # Get base price of the product
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product with id {product_id} not found")

        total_price = product.base_price

        # Add prices of selected options
        for part_id, option_id in selected_options.items():
            option = self.db.get(Option, option_id)
            if not option:
                raise ValueError(f"Option with id {option_id} not found")
            total_price += option.base_price

        # Apply price rules
        price_rules = (
            self.db.query(PriceRule).filter(PriceRule.product_id == product_id).all()
        )

        for rule in price_rules:
            conditions = (
                self.db.query(PriceRuleCondition)
                .filter(PriceRuleCondition.price_rule_id == rule.id)
                .all()
            )

            if self._rule_conditions_met(conditions, selected_options):
                total_price += rule.price_adjustment

        return total_price

    def _rule_conditions_met(
        self, conditions: list[PriceRuleCondition], selected_options: Dict[int, int]
    ) -> bool:
        """
        Check if all conditions for a price rule are met.

        :param conditions: List of PriceRuleCondition objects
        :param selected_options: Dict of {part_id: option_id} for selected options
        :return: True if all conditions are met, False otherwise
        """
        for condition in conditions:
            if (
                condition.part_id not in selected_options
                or selected_options[condition.part_id] != condition.option_id
            ):
                return False
        return True

    def get_option_price(self, option_id: int) -> float:
        """
        Get the price of a single option.

        :param option_id: ID of the option
        :return: Price of the option
        """
        option = self.db.get(Option, option_id)
        if not option:
            raise ValueError(f"Option with id {option_id} not found")
        return option.base_price
