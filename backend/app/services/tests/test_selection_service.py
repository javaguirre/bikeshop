import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from z3 import sat
from backend.app.models import Base
from backend.app.models.product import (
    Option,
    OptionCompatibility,
    Part,
    Product,
)
from backend.app.repositories.pricing_repository import PricingOrderRepository
from backend.app.services.selection_service import PartSelectionService


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
def selection_service():
    return PartSelectionService()


@pytest.fixture
def repository(db_session):
    return PricingOrderRepository(db_session)


def test_load_compatibilities(selection_service, repository, db_session):
    parts = db_session.query(Part).all()
    options = db_session.query(Option).all()
    grouped_compatibilities = repository.get_compatibilities(product_id=1)

    selection_service.load_compatibilities(parts, options, grouped_compatibilities)

    assert len(selection_service.option_vars) == len(options)


def test_get_available_options(selection_service, repository, db_session):
    parts = db_session.query(Part).all()
    options = db_session.query(Option).all()
    grouped_compatibilities = repository.get_compatibilities(product_id=1)

    selection_service.load_compatibilities(parts, options, grouped_compatibilities)
    available_options = selection_service.get_available_options(parts)

    assert len(available_options) == len(parts)
    for part_id, options in available_options.items():
        assert len(options) > 0


def test_is_selection_valid_returns_valid(selection_service, repository, db_session):
    parts = db_session.query(Part).all()
    options = db_session.query(Option).all()
    grouped_compatibilities = repository.get_compatibilities(product_id=1)

    selection_service.load_compatibilities(parts, options, grouped_compatibilities)

    assert selection_service.is_selection_valid()


def test_is_selection_valid_returns_invalid(
    selection_service, repository, db_session, capsys
):
    parts = db_session.query(Part).all()
    options = db_session.query(Option).all()
    full_suspension = db_session.query(Option).filter_by(name="Full-suspension").first()
    fat_wheels = db_session.query(Option).filter_by(id=5).first()

    grouped_compatibilities = repository.get_compatibilities(product_id=1)
    selection_service.load_compatibilities(parts, options, grouped_compatibilities)

    # Add incompatible options
    selection_service.select_part_options([full_suspension, fat_wheels])

    assert not selection_service.is_selection_valid()


def test_select_part_option(selection_service, repository, db_session):
    parts = db_session.query(Part).all()
    options = db_session.query(Option).all()
    grouped_compatibilities = repository.get_compatibilities(product_id=1)

    selection_service.load_compatibilities(parts, options, grouped_compatibilities)

    full_suspension = db_session.query(Option).filter_by(name="Full-suspension").first()
    selection_service.select_part_options([full_suspension])

    assert selection_service.solver.check() == sat
