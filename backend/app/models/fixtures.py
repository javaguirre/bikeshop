from backend.app.models.product import (
    Option,
    OptionCompatibility,
    Part,
    PriceRule,
    PriceRuleCondition,
    Product,
)
from backend.app.models.base import get_db


def main():
    db = next(get_db())
    try:
        # Create test data
        product = Product(id=1, name="Test Bike", description="This is a test bike")
        db.add(product)

        parts = [
            Part(id=1, name="Frame", product_id=1),
            Part(id=2, name="Wheels", product_id=1),
            Part(id=3, name="Rim color", product_id=1),
            Part(id=4, name="Chain", product_id=1),
        ]
        db.add_all(parts)

        options = [
            Option(id=1, part_id=1, name="Full-suspension", price=130),
            Option(id=2, part_id=1, name="Diamond", price=100),
            Option(id=3, part_id=2, name="Road wheels", price=80),
            Option(id=4, part_id=2, name="Mountain wheels", price=100),
            Option(id=5, part_id=2, name="Fat bike wheels", price=120),
            Option(id=6, part_id=3, name="Red", price=20),
            Option(id=7, part_id=3, name="Black", price=20),
            Option(id=8, part_id=4, name="Single-speed chain", price=43),
            Option(id=9, part_id=4, name="8-speed chain", price=55),
        ]
        db.add_all(options)

        rule = PriceRule(id=1, option_id=7, price=30)
        db.add(rule)
        conditions = [
            PriceRuleCondition(price_rule_id=1, option_id=1),
            PriceRuleCondition(price_rule_id=1, option_id=4),
        ]
        db.add_all(conditions)

        # Add compatibility rules
        compatibilities = [
            OptionCompatibility(
                option_id=1, compatible_option_id=4, include_exclude="include"
            ),
            OptionCompatibility(
                option_id=2, compatible_option_id=3, include_exclude="exclude"
            ),
            OptionCompatibility(
                option_id=5, compatible_option_id=7, include_exclude="include"
            ),
        ]
        db.add_all(compatibilities)

        db.commit()
        print("Fixtures data created")
    finally:
        db.close()


if __name__ == "__main__":
    main()
