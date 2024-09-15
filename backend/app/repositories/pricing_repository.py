from typing import List
from sqlalchemy import Column
from sqlalchemy.orm import Session

from backend.app.models.product import Option, PriceRule, PriceRuleCondition, Product


class PricingOrderRepository(OrderRepository, PricingRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_product(self, product_id: int):
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_options_by_ids(self, option_ids: list[int]):
        return self.db.query(Option).filter(Option.id.in_(option_ids)).all()

    def get_price_rules(self, product_id: int):
        return self.db.query(PriceRule).filter(PriceRule.product_id == product_id).all()

    def get_option(self, option_id: int):
        return self.db.query(Option).filter(Option.id == option_id).first()

    def get_price_rule_by_option_id(self, option_id: Column[int]) -> List[PriceRule]:
        return self.db.query(PriceRule).filter(PriceRule.option_id == option_id).all()
