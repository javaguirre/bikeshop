from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.models.base import Base

# Product Categories (Many-to-Many)
product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)

# Product Parts (Many-to-Many)
product_parts = Table(
    "product_parts",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("part_id", Integer, ForeignKey("parts.id"), primary_key=True),
    Column("required", Boolean, default=False),
)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    base_price = Column(Numeric(10, 2), nullable=False)

    categories = relationship(
        "Category", secondary=product_categories, back_populates="products"
    )
    parts = relationship("Part", secondary=product_parts, back_populates="products")
    price_rules = relationship("PriceRule", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    products = relationship(
        "Product", secondary=product_categories, back_populates="categories"
    )


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    products = relationship("Product", secondary=product_parts, back_populates="parts")
    options = relationship("Option", back_populates="part")


# Options (e.g., Full-suspension, Road wheels, Single-speed chain)
class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("parts.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    base_price = Column(Numeric(10, 2), nullable=False)
    in_stock = Column(Boolean, default=True)

    part = relationship("Part", back_populates="options")

    compatible_options = relationship(
        "Option",
        secondary="option_compatibility",
        primaryjoin="Option.id==option_compatibility.c.option_id",
        secondaryjoin="Option.id==option_compatibility.c.compatible_option_id",
        back_populates="compatible_with",
    )
    compatible_with = relationship(
        "Option",
        secondary="option_compatibility",
        primaryjoin="Option.id==option_compatibility.c.compatible_option_id",
        secondaryjoin="Option.id==option_compatibility.c.option_id",
        back_populates="compatible_options",
    )


class OptionCompatibility(Base):
    __tablename__ = "option_compatibility"

    option_id = Column(Integer, ForeignKey("options.id"), primary_key=True)
    compatible_option_id = Column(Integer, ForeignKey("options.id"), primary_key=True)


class PriceRule(Base):
    __tablename__ = "price_rules"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    rule_type = Column(
        Enum("combination", "dependency", name="rule_types"), nullable=False
    )
    price_adjustment = Column(Numeric(10, 2), nullable=False)

    product = relationship("Product", back_populates="price_rules")
    conditions = relationship("PriceRuleCondition", back_populates="price_rule")


class PriceRuleCondition(Base):
    __tablename__ = "price_rule_conditions"

    id = Column(Integer, primary_key=True)
    price_rule_id = Column(Integer, ForeignKey("price_rules.id"))
    part_id = Column(Integer, ForeignKey("parts.id"))
    option_id = Column(Integer, ForeignKey("options.id"))

    price_rule = relationship("PriceRule", back_populates="conditions")
    part = relationship("Part")
    option = relationship("Option")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)  # Assuming a customers table exists
    order_date = Column(DateTime, default=func.now())
    total_price = Column(Numeric(10, 2), nullable=False)

    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    options = Column(JSON, nullable=False)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
