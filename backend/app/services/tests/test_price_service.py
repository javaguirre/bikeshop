import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base
from backend.app.models.product import (
    Option,
    OptionCompatibility,
    Order,
    Part,
    PriceRule,
    PriceRuleCondition,
    Product,
)
from backend.app.services.price_service import PriceService


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create test data
    product = Product(id=1, name="Test Bike")
    session.add(product)

    parts = [
        Part(id=1, name="Frame", product_id=1),
        Part(id=2, name="Wheels", product_id=1),
        Part(id=3, name="Rim color", product_id=1),
        Part(id=4, name="Chain", product_id=1),
    ]
    session.add_all(parts)

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
    session.add_all(options)

    rule = PriceRule(id=1, option_id=7, price=30)
    session.add(rule)
    conditions = [
        PriceRuleCondition(price_rule_id=1, option_id=1),
        PriceRuleCondition(price_rule_id=1, option_id=4),
    ]
    session.add_all(conditions)

    # Add compatibility rules
    compatibilities = [
        OptionCompatibility(option1_id=1, option2_id=4, compatible=True),
        OptionCompatibility(option1_id=2, option2_id=3, compatible=True),
        OptionCompatibility(option1_id=5, option2_id=7, compatible=True),
    ]
    session.add_all(compatibilities)

    session.commit()

    yield session

    session.close()


@pytest.fixture
def price_service(db_session):
    return PriceService()


def test_calculate_price_basic(price_service, db_session):
    product = db_session.query(Product).first()
    order = Order(product=product, total_price=0)
    db_session.add(order)
    db_session.commit()
    price_rules = db_session.query(PriceRule).all()

    full_suspension = db_session.query(Option).filter_by(name="Full-suspension").first()
    mountain_wheels = db_session.query(Option).filter_by(name="Mountain wheels").first()
    black_rim = db_session.query(Option).filter_by(name="Black").first()

    order.options.extend([full_suspension, mountain_wheels, black_rim])
    db_session.commit()

    total_price = price_service.calculate_price(order.options, price_rules)
    assert total_price == 260  # 130 + 100 + 30 (price rule for black rim)


def test_price_rule_application(price_service, db_session):
    product = db_session.query(Product).first()
    order = Order(product=product, total_price=0)
    db_session.add(order)
    db_session.commit()

    price_rules = db_session.query(PriceRule).all()

    full_suspension = db_session.query(Option).filter_by(name="Full-suspension").first()
    mountain_wheels = db_session.query(Option).filter_by(name="Mountain wheels").first()
    black_rim = db_session.query(Option).filter_by(name="Black").first()

    order.options.extend([full_suspension, mountain_wheels, black_rim])
    db_session.commit()

    total_price = price_service.calculate_price(order.options, price_rules)
    assert total_price == 260  # 130 + 100 + 30 (price rule for black rim)

    # Change to road wheels, which should not trigger the price rule
    road_wheels = db_session.query(Option).filter_by(name="Road wheels").first()
    order.options.remove(mountain_wheels)
    order.options.append(road_wheels)
    db_session.commit()

    total_price = price_service.calculate_price(order.options, price_rules)
    assert total_price == 230  # 130 + 80 + 20 (no price rule applied)
