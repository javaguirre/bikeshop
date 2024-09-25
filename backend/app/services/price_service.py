from itertools import groupby
from operator import attrgetter

from sqlalchemy import Column

from backend.app.models.product import Option, PriceRule
from backend.app.services.base import BasePriceService


class PriceService(BasePriceService):
    def calculate_price(self, options: list[Option], rules: list[PriceRule]) -> float:
        """
        Calculate the price of an option based on the current order and the new option.
        """
        total_price = 0
        current_option_ids: list[Column[int]] = [option.id for option in options]

        for option in options:
            if not self._has_rules(option, rules):
                total_price += option.price
                continue

            total_price += self._get_price_with_rules(option, rules, current_option_ids)

        return total_price

    def _format_available_options(self, options: list[Option]) -> dict[int, list[int]]:
        return {
            part_id: list(map(attrgetter("id"), group))
            for part_id, group in groupby(
                sorted(options, key=attrgetter("part_id")), key=attrgetter("part_id")
            )
        }

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
