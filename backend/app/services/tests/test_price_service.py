from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base
from backend.app.models.product import (
    Option,
    Part,
    PriceRule,
    PriceRuleCondition,
    Product,
)


@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    product = Product(id=1, name="Test Bike", base_price=100)
    session.add(product)

    parts = [
        Part(id=1, name="Frame"),
        Part(id=2, name="Wheels"),
        Part(id=3, name="Chain"),
    ]
    session.add_all(parts)

    options = [
        Option(id=1, part_id=1, name="Full suspension", base_price=130),
        Option(id=2, part_id=1, name="Diamond", base_price=100),
        Option(id=3, part_id=1, name="Shiny frame", base_price=30),
        Option(id=4, part_id=1, name="Matte frame", base_price=20),
        Option(id=5, part_id=2, name="Road wheels", base_price=80),
        Option(id=6, part_id=2, name="Mountain wheels", base_price=100),
        Option(id=7, part_id=3, name="Single-speed chain", base_price=43),
        Option(id=8, part_id=3, name="8-speed chain", base_price=55),
    ]
    session.add_all(options)

    # Add a price rule: Matte finish on full-suspension costs extra
    rule = PriceRule(id=1, product_id=1, rule_type="combination", price_adjustment=30)
    session.add(rule)
    conditions = [
        PriceRuleCondition(price_rule_id=1, part_id=1, option_id=1),  # Full suspension
        PriceRuleCondition(price_rule_id=1, part_id=1, option_id=4),  # Matte frame
    ]
    session.add_all(conditions)

    session.commit()

    yield session

    session.close()


@pytest.fixture
def pricing_service(db_session):
    repository = PricingRepository(db_session)
    return PricingService(repository)


def test_calculate_price_basic(pricing_service):
    selected_options = {
        1: 1,
        2: 5,
        3: 7,
    }  # Full suspension, Road wheels, Single-speed chain
    expected_price = 100 + 130 + 80 + 43  # Base + Frame + Wheels + Chain

    total_price = pricing_service.calculate_price(1, selected_options)

    assert total_price == expected_price


def test_calculate_price_with_rule(pricing_service):
    selected_options = {
        1: 1,  # Full suspension
        2: 4,  # Mountain wheels
        3: 7,  # Black rim color
        4: 8,  # Single-speed chain
    }
    total_price = pricing_service.calculate_price(1, selected_options)

    expected_price = Decimal("348.00")

    assert total_price == expected_price


def test_calculate_price_rule_not_applied(pricing_service):
    selected_options = {
        1: 2,  # Diamond frame
        2: 3,  # Road wheels
        3: 7,  # Black rim color
        4: 8,  # Single-speed chain
    }
    total_price = pricing_service.calculate_price(1, selected_options)
    expected_price = Decimal("328.00")

    assert total_price == expected_price


# def test_get_option_price(pricing_service):
#     option_price = pricing_service.get_option_price(1)  # Full suspension
#     assert option_price == 130


def test_calculate_price_invalid_product(pricing_service):
    with pytest.raises(ValueError):
        pricing_service.calculate_price(999, {})


# def test_calculate_price_invalid_option(pricing_service):
#     with pytest.raises(ValueError):
#         pricing_service.calculate_price(1, {1: 999})


# def test_get_option_price_invalid_option(pricing_service):
#     with pytest.raises(ValueError):
#         pricing_service.get_option_price(999)
