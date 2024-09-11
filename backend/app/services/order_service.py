from sqlalchemy.orm import Session, joinedload
from typing import Dict, List
from ..models.product import Product, Part, Option, OptionCompatibility


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def validate_and_add_part(
        self,
        product_id: int,
        current_options: Dict[int, int],
        new_part_id: int,
        new_option_id: int,
    ) -> Dict[int, int]:
        """
        Validates if a new part can be added to the current configuration and adds it if valid.

        :param product_id: ID of the product being customized
        :param current_options: Dict of currently selected options {part_id: option_id}
        :param new_part_id: ID of the new part being added
        :param new_option_id: ID of the new option being added
        :return: Updated dict of selected options
        """
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product with id {product_id} not found")

        new_option = self.db.get(Option, new_option_id)
        if not new_option:
            raise ValueError(f"Option with id {new_option_id} not found")

        if new_option.part_id != new_part_id:
            raise ValueError(
                f"Option {new_option_id} does not belong to part {new_part_id}"
            )

        if not new_option.in_stock:
            raise ValueError(f"Option {new_option.name} is out of stock")

        # Check if the new option is compatible with currently selected options
        for part_id, option_id in current_options.items():
            if not self._are_options_compatible(option_id, new_option_id):
                current_option = self.db.get(Option, option_id)
                raise ValueError(
                    f"Option {new_option.name} is not compatible with {current_option.name}"
                )

        # Check specific business rules
        self._check_specific_rules(current_options, new_part_id, new_option_id)

        # If all checks pass, add the new option
        updated_options = current_options.copy()
        updated_options[new_part_id] = new_option_id
        return updated_options

    def _are_options_compatible(self, option_id1: int, option_id2: int) -> bool:
        """Check if two options are compatible."""
        compatibility = (
            self.db.query(OptionCompatibility)
            .filter(
                (
                    (OptionCompatibility.option_id == option_id1)
                    & (OptionCompatibility.compatible_option_id == option_id2)
                )
                | (
                    (OptionCompatibility.option_id == option_id2)
                    & (OptionCompatibility.compatible_option_id == option_id1)
                )
            )
            .first()
        )
        return compatibility is not None

    def _check_specific_rules(
        self, current_options: Dict[int, int], new_part_id: int, new_option_id: int
    ):
        """Check specific business rules."""
        new_option = self.db.get(Option, new_option_id)

        # Rule: If "mountain wheels" are selected, only full suspension frame is allowed
        if new_option.name == "mountain wheels":
            frame_option_id = current_options.get(self._get_part_id_by_name("Frame"))
            if frame_option_id:
                frame_option = self.db.query(Option).get(frame_option_id)
                if frame_option.name != "Full-suspension":
                    raise ValueError(
                        "Mountain wheels can only be used with a full suspension frame"
                    )

        # Rule: If "fat bike wheels" are selected, red rim color is unavailable
        if new_option.name == "fat bike wheels":
            rim_color_part_id = self._get_part_id_by_name("Rim color")
            rim_color_option_id = current_options.get(rim_color_part_id)
            if rim_color_option_id:
                rim_color_option = self.db.get(Option, rim_color_option_id)
                if rim_color_option.name == "Red":
                    raise ValueError(
                        "Red rim color is not available with fat bike wheels"
                    )

    def _get_part_id_by_name(self, part_name: str) -> int:
        """Get part ID by name."""
        part = self.db.query(Part).filter(Part.name == part_name).first()
        if not part:
            raise ValueError(f"Part {part_name} not found")
        return part.id

    def get_available_options(
        self, product_id: int, current_options: Dict[int, int]
    ) -> Dict[int, List[Option]]:
        """
        Get available options for each part based on current selections.

        :param product_id: ID of the product being customized
        :param current_options: Dict of currently selected options {part_id: option_id}
        :return: Dict of available options for each part {part_id: [Option]}
        """
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product with id {product_id} not found")

        print(f"Product found: {product.name}")

        available_options = {}
        parts = self.db.query(Part).options(joinedload(Part.options)).all()
        print(f"Number of parts found: {len(parts)}")

        for part in parts:
            print(f"Processing part: {part.name}")
            compatible_options = []
            for option in part.options:
                print(f"  Checking option: {option.name}")
                if option.in_stock:
                    print("    Option is in stock")
                    is_compatible = all(
                        self._are_options_compatible(current_option_id, option.id)
                        for current_option_id in current_options.values()
                    )
                    print(f"    Is compatible: {is_compatible}")
                    if is_compatible:
                        compatible_options.append(option)
                else:
                    print("    Option is out of stock")
            if compatible_options:
                available_options[part.id] = compatible_options
            print(
                f"  Compatible options for {part.name}: {[o.name for o in compatible_options]}"
            )

        print(f"Final available options: {available_options}")
        return available_options

    def _is_option_compatible_with_current(
        self, option_id: int, current_options: Dict[int, int]
    ) -> bool:
        """Check if an option is compatible with all currently selected options."""
        for current_option_id in current_options.values():
            if not self._are_options_compatible(option_id, current_option_id):
                return False
        return True
