from .base import Base, engine
from .product import (
    Product,
    Category,
    Part,
    Option,
    OptionCompatibility,
    PriceRule,
    PriceRuleCondition,
    Order,
    OrderItem,
)

Base.metadata.create_all(bind=engine)
