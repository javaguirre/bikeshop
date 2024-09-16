from sqlalchemy import (
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


# Product, Parts, Rules and Options would be in different files,
# but for simplicity, we'll keep them in the same file


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    categories = relationship(
        "Category", secondary=product_categories, back_populates="products"
    )
    parts = relationship("Part", secondary=product_parts, back_populates="products")
    orders = relationship("Order", back_populates="product")


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


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    base_price = Column(Numeric(10, 2), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"))

    in_stock = Column(Boolean, default=True)

    part = relationship("Part", back_populates="options")
    orders = relationship("Order", secondary="order_options", back_populates="options")


class OptionCompatibility(Base):
    __tablename__ = "option_compatibility"

    option_id = Column(Integer, ForeignKey("options.id"), primary_key=True)
    compatible_option_id = Column(Integer, ForeignKey("options.id"), primary_key=True)
    include_exclude = Column(
        Enum("include", "exclude"), nullable=False, default="include"
    )


class PriceRule(Base):
    __tablename__ = "price_rules"

    id = Column(Integer, primary_key=True)
    option_id = Column(Integer, ForeignKey("products.id"))
    # TODO: We could add a rule type
    price = Column(Numeric(10, 2), nullable=False)

    conditions = relationship("PriceRuleCondition", back_populates="price_rule")


class PriceRuleCondition(Base):
    __tablename__ = "price_rule_conditions"

    id = Column(Integer, primary_key=True)
    price_rule_id = Column(Integer, ForeignKey("price_rules.id"))
    option_id = Column(Integer, ForeignKey("options.id"))

    price_rule = relationship("PriceRule", back_populates="conditions")
    option = relationship("Option")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)  # Assuming a customers table exists
    order_date = Column(DateTime, default=func.now())
    total_price = Column(Numeric(10, 2), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))

    product = relationship("Product", back_populates="orders")
    options = relationship("Option", secondary="order_options", back_populates="orders")
