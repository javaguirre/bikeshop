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
from backend.app.repositories.pricing_repository import PricingOrderRepository
from backend.app.services.order_service import OrderService


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
    session.add_all(compatibilities)

    session.commit()

    yield session

    session.close()


@pytest.fixture
def order_service(db_session):
    repository = PricingOrderRepository(db_session)
    return OrderService(repository)


# def test_create_order(order_service, db_session):
#     product = db_session.query(Product).first()
#     response = order_service.create_order(product)

#     assert response.id is not None
#     assert response.total_price == 0
#     assert len(response.available_options) > 0


def test_update_order_valid_option(order_service, db_session):
    product = db_session.query(Product).first()
    order = Order(product=product, total_price=0)  # Set initial total_price
    db_session.add(order)
    db_session.commit()

    full_suspension = db_session.query(Option).filter_by(name="Full-suspension").first()
    response = order_service.update_order(order, full_suspension)

    assert response.id == order.id
    assert response.total_price == 130
    assert len(response.available_options) > 0


def test_update_order_incompatible_option(order_service, db_session):
    product = db_session.query(Product).first()
    order = Order(product=product, total_price=0)
    db_session.add(order)
    db_session.commit()

    full_suspension = db_session.query(Option).filter_by(name="Full-suspension").first()
    order_service.update_order(order, full_suspension)

    road_wheels = db_session.query(Option).filter_by(name="Road wheels").first()

    with pytest.raises(ValueError, match="Option is not compatible with the order"):
        order_service.update_order(order, road_wheels)


def test_calculate_price_basic(order_service, db_session):
    product = db_session.query(Product).first()
    order = Order(product=product, total_price=0)
    db_session.add(order)
    db_session.commit()

    full_suspension = db_session.query(Option).filter_by(name="Full-suspension").first()
    mountain_wheels = db_session.query(Option).filter_by(name="Mountain wheels").first()
    black_rim = db_session.query(Option).filter_by(name="Black").first()

    order.options.extend([full_suspension, mountain_wheels, black_rim])
    db_session.commit()

    total_price = order_service.calculate_price(order)
    assert total_price == 260  # 130 + 100 + 30 (price rule for black rim)


def test_get_available_options(order_service, db_session):
    product = db_session.query(Product).first()
    order = Order(product=product, total_price=0)
    db_session.add(order)
    db_session.commit()

    full_suspension = db_session.query(Option).filter_by(name="Full-suspension").first()
    order.options.append(full_suspension)
    db_session.commit()

    options = db_session.query(Option).all()
    conditions = db_session.query(OptionCompatibility).all()

    available_options = order_service.get_available_options(options, conditions)

    available_option_names = [option.name for option in available_options]
    assert "Mountain wheels" in available_option_names
    assert "Road wheels" not in available_option_names


def test_price_rule_application(order_service, db_session):
    product = db_session.query(Product).first()
    order = Order(product=product, total_price=0)
    db_session.add(order)
    db_session.commit()

    full_suspension = db_session.query(Option).filter_by(name="Full-suspension").first()
    mountain_wheels = db_session.query(Option).filter_by(name="Mountain wheels").first()
    black_rim = db_session.query(Option).filter_by(name="Black").first()

    order.options.extend([full_suspension, mountain_wheels, black_rim])
    db_session.commit()

    total_price = order_service.calculate_price(order)
    assert total_price == 260  # 130 + 100 + 30 (price rule for black rim)

    # Change to road wheels, which should not trigger the price rule
    road_wheels = db_session.query(Option).filter_by(name="Road wheels").first()
    order.options.remove(mountain_wheels)
    order.options.append(road_wheels)
    db_session.commit()

    total_price = order_service.calculate_price(order)
    assert total_price == 230  # 130 + 80 + 20 (no price rule applied)
