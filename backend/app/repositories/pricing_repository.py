from typing import List
from sqlalchemy import Column
from sqlalchemy.orm import Session, joinedload

from backend.app.models.product import (
    Option,
    OptionCompatibility,
    Order,
    Part,
    PriceRule,
    Product,
)


class PricingOrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_order(self, order_id: int):
        order: Order | None = self.db.query(Order).filter(Order.id == order_id).first()

        if not order:
            raise ValueError(f"Order not found: {order_id}")

        return order

    def get_product(self, product_id: int):
        product: Product | None = (
            self.db.query(Product).filter(Product.id == product_id).first()
        )

        if not product:
            raise ValueError(f"Product not found: {product_id}")

        return product

    def get_options_by_ids(self, option_ids: list[int]):
        return self.db.query(Option).filter(Option.id.in_(option_ids)).all()

    def get_price_rules(self, product_id: int):
        return self.db.query(PriceRule).filter(PriceRule.product_id == product_id).all()

    def get_option(self, option_id: int):
        option: Option | None = (
            self.db.query(Option).filter(Option.id == option_id).first()
        )

        if not option:
            raise ValueError(f"Option not found: {option_id}")

        return option

    def get_price_rule_by_option_id(self, option_id: Column[int]) -> List[PriceRule]:
        return self.db.query(PriceRule).filter(PriceRule.option_id == option_id).all()

    def get_price_rules_by_option_ids(self, option_ids: list[int]) -> List[PriceRule]:
        return (
            self.db.query(PriceRule).filter(PriceRule.option_id.in_(option_ids)).all()
        )

    def get_options(self, product_id: int) -> List[Option]:
        return (
            self.db.query(Option)
            .join(Part, Part.id == Option.part_id)
            .filter(Option.in_stock, Part.product_id == product_id)
            .all()
        )

    def get_option_compatibilities(
        self, options: list[Option]
    ) -> List[OptionCompatibility]:
        option_ids = [option.id for option in options]
        return (
            self.db.query(OptionCompatibility)
            .filter(OptionCompatibility.option_id.in_(option_ids))
            .options(
                joinedload(OptionCompatibility.option),
                joinedload(OptionCompatibility.compatible_option),
            )
            .all()
        )

    def update_order(self, order: Order):
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def create_order(self, order: Order):
        # TODO: Initial status??
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order
