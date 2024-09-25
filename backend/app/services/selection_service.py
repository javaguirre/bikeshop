from z3 import Solver, sat, Int, Or, Implies, ArithRef
import logging

from backend.app.models.product import Option, Part
from backend.app.services.base import BaseSelectionService

logger = logging.getLogger(__name__)


class PartSelectionService(BaseSelectionService):
    def __init__(self):
        self.solver = Solver()
        self.option_vars: dict[int, ArithRef] = {}

    def load_compatibilities(
        self,
        parts: list[Part],
        options: list[Option],
        grouped_compatibilities: dict[int, dict[str, list[int]]],
    ):
        self.option_vars = {
            option.id: Int(f"part{option.part_id}") for option in options
        }

        for part in parts:
            part_options = [
                self.option_vars[option.id] == option.id for option in part.options
            ]
            self.solver.add(Or(part_options))

        for option1_id, rules in grouped_compatibilities.items():
            option1_var: ArithRef = self.option_vars[option1_id]

            if not rules:
                continue

            self.solver.add(
                Implies(
                    option1_var == option1_id,
                    Or(
                        [
                            self.option_vars[opt_id] == opt_id
                            for opt_id in rules["compatible"]
                        ]
                        + [
                            self.option_vars[opt_id] != opt_id
                            for opt_id in rules["incompatible"]
                        ]
                    ),
                )
            )

    def get_available_options(self, parts: list[Part]) -> dict[int, list[int]]:
        available_options = {}

        for part in parts:
            available_options[part.id] = []

            for option in part.options:
                self.solver.push()
                self.solver.add(self.option_vars[option.id] == option.id)

                if self.solver.check() == sat:
                    available_options[part.id].append(option.id)

                self.solver.pop()

        return available_options

    def is_selection_valid(self) -> bool:
        return self.solver.check() == sat

    def select_part_options(self, options: list[Option]):
        for option in options:
            self.solver.add(self.option_vars[option.id] == option.id)
