import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base
from backend.app.models.product import Option, OptionCompatibility, Part, Product
from backend.app.services.order_service import OrderService


# Setup test database
@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create test data
    product = Product(id=1, name="Test Bike", base_price=100)
    session.add(product)

    parts = [
        Part(id=1, name="Frame"),
        Part(id=2, name="Wheels"),
        Part(id=3, name="Rim color"),
        Part(id=4, name="Chain"),
    ]
    session.add_all(parts)

    options = [
        Option(id=1, part_id=1, name="Full-suspension", base_price=130),
        Option(id=2, part_id=1, name="Diamond", base_price=100),
        Option(id=3, part_id=2, name="Road wheels", base_price=80),
        Option(id=4, part_id=2, name="Mountain wheels", base_price=100),
        Option(id=5, part_id=2, name="Fat bike wheels", base_price=120),
        Option(id=6, part_id=3, name="Red", base_price=20),
        Option(id=7, part_id=3, name="Black", base_price=20),
        Option(id=8, part_id=4, name="Single-speed chain", base_price=43),
        Option(id=9, part_id=4, name="8-speed chain", base_price=55),
    ]
    session.add_all(options)

    # Add compatibility rules
    compatibilities = [
        OptionCompatibility(
            option_id=1, compatible_option_id=4
        ),  # Full-suspension compatible with Mountain wheels
        OptionCompatibility(
            option_id=2, compatible_option_id=3
        ),  # Diamond frame compatible with Road wheels
        OptionCompatibility(
            option_id=5, compatible_option_id=7
        ),  # Fat bike wheels compatible with Black rim color
    ]
    session.add_all(compatibilities)

    session.commit()

    yield session

    session.close()


@pytest.fixture
def order_service(db_session):
    return OrderService(db_session)


def test_validate_and_add_part_valid(order_service):
    current_options = {1: 1}  # Full-suspension frame
    updated_options = order_service.validate_and_add_part(
        1, current_options, 2, 4
    )  # Add Mountain wheels
    assert updated_options == {1: 1, 2: 4}


def test_validate_and_add_part_incompatible(order_service):
    current_options = {1: 2}  # Diamond frame
    with pytest.raises(
        ValueError, match="Option Mountain wheels is not compatible with Diamond"
    ):
        order_service.validate_and_add_part(
            1, current_options, 2, 4
        )  # Try to add Mountain wheels


def test_validate_and_add_part_out_of_stock(order_service, db_session):
    db_session.query(Option).filter_by(id=3).update({"in_stock": False})
    db_session.commit()
    current_options = {1: 2}  # Diamond frame
    with pytest.raises(ValueError, match="Option Road wheels is out of stock"):
        order_service.validate_and_add_part(
            1, current_options, 2, 3
        )  # Try to add out-of-stock Road wheels


def test_validate_and_add_part_specific_rule_mountain_wheels(order_service):
    current_options = {1: 2}  # Diamond frame
    with pytest.raises(ValueError) as exc_info:
        order_service.validate_and_add_part(
            1, current_options, 2, 4
        )  # Try to add Mountain wheels
    assert "Option Mountain wheels is not compatible with Diamond" in str(
        exc_info.value
    )


def test_validate_and_add_part_specific_rule_fat_bike_wheels(order_service):
    current_options = {1: 1, 2: 5, 3: 6}  # Full-suspension, Fat bike wheels, Red rim
    with pytest.raises(ValueError) as exc_info:
        order_service.validate_and_add_part(
            1, current_options, 3, 6
        )  # Try to add Red rim color
    assert "Option Red is not compatible with Full-suspension" in str(exc_info.value)


def test_get_available_options(order_service):
    current_options = {1: 1}  # Full-suspension frame
    available_options = order_service.get_available_options(1, current_options)
    print("Available options:", available_options)

    assert len(available_options) > 0, "No available options returned"

    for part_id, options in available_options.items():
        print(f"Part {part_id} options: {[option.id for option in options]}")

    # Check if Mountain wheels (id 4) is available for any part
    assert any(
        any(option.id == 4 for option in options)
        for options in available_options.values()
    ), "Mountain wheels (id 4) not found in available options"


def test_get_available_options_empty_current_options(order_service):
    available_options = order_service.get_available_options(1, {})
    print("Available options:", available_options)

    assert len(available_options) > 0, "No available options returned"

    for part_id, options in available_options.items():
        print(f"Part {part_id} options: {[option.id for option in options]}")
        assert len(options) > 0, f"No options available for part {part_id}"


def test_get_available_options_invalid_product(order_service):
    with pytest.raises(ValueError, match="Product with id 999 not found"):
        order_service.get_available_options(999, {})


def test_validate_and_add_part_invalid_product(order_service):
    with pytest.raises(ValueError, match="Product with id 999 not found"):
        order_service.validate_and_add_part(999, {}, 1, 1)


def test_validate_and_add_part_invalid_option(order_service):
    with pytest.raises(ValueError, match="Option with id 999 not found"):
        order_service.validate_and_add_part(1, {}, 1, 999)
