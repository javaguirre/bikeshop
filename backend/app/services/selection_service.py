from z3 import Solver, sat, unsat, Int, Or, Implies, ArithRef

from backend.app.models.product import Option, OptionCompatibility, Part


class PartSelectionService:
    def __init__(self):
        self.solver = Solver()
        self.option_vars: dict[int, ArithRef] = {}

    def load_compatibilities(
        self,
        parts: list[Part],
        options: list[Option],
        compatibilities: list[OptionCompatibility],
    ):
        self.option_vars = {
            option.id: Int(f"part{option.part_id}_option{option.id}")
            for option in options
        }

        for part in parts:
            part_options = [
                self.option_vars[option.id] == option.id for option in part.options
            ]
            self.solver.add(Or(part_options))

        for compatibility in compatibilities:
            option1 = self.option_vars[compatibility.option1_id]
            option2 = self.option_vars[compatibility.option2_id]

            if compatibility.compatible:
                self.solver.add(
                    Implies(
                        option1 == compatibility.option1_id,
                        Or(option2 == compatibility.option2_id),
                    )
                )
            else:
                self.solver.add(
                    Implies(
                        option1 == compatibility.option1_id,
                        option2 != compatibility.option2_id,
                    )
                )

    def get_available_options(self, parts: list[Part]):
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

    def check_satisfiability(self):
        if self.solver.check() == sat:
            print("The constraints are satisfiable.")
        elif self.solver.check() == unsat:
            print(
                "The constraints are unsatisfiable! No valid configuration is possible."
            )
        else:
            print("Solver returned unknown. Could not determine satisfiability.")

    def find_conflicting_constraints(self):
        if self.solver.check() == unsat:
            print("\nUnsatisfiable! Here's the reason:")
            print(self.solver.unsat_core())
        else:
            print("The constraints are satisfiable.")

    def select_part_option(self, option: Option):
        self.solver.add(self.option_vars[option.id] == option.id)
