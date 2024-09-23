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


def test_load_compatibilities(selection_service, db_session):
    parts = db_session.query(Part).all()
    options = db_session.query(Option).all()
    compatibilities = db_session.query(OptionCompatibility).all()

    selection_service.load_compatibilities(parts, options, compatibilities)

    assert len(selection_service.option_vars) == len(options)


def test_get_available_options(selection_service, db_session):
    parts = db_session.query(Part).all()
    options = db_session.query(Option).all()
    compatibilities = db_session.query(OptionCompatibility).all()

    selection_service.load_compatibilities(parts, options, compatibilities)
    available_options = selection_service.get_available_options(parts)

    assert len(available_options) == len(parts)
    for part_id, options in available_options.items():
        assert len(options) > 0


def test_check_satisfiability(selection_service, db_session, capsys):
    parts = db_session.query(Part).all()
    options = db_session.query(Option).all()
    compatibilities = db_session.query(OptionCompatibility).all()

    selection_service.load_compatibilities(parts, options, compatibilities)
    selection_service.check_satisfiability()

    captured = capsys.readouterr()
    assert "The constraints are satisfiable." in captured.out


def test_find_conflicting_constraints(selection_service, db_session, capsys):
    parts = db_session.query(Part).all()
    options = db_session.query(Option).all()
    compatibilities = db_session.query(OptionCompatibility).all()

    # Add an incompatible rule to make it unsatisfiable
    incompatibility = OptionCompatibility(option1_id=1, option2_id=4, compatible=False)
    db_session.add(incompatibility)
    db_session.commit()

    compatibilities = db_session.query(OptionCompatibility).all()
    selection_service.load_compatibilities(parts, options, compatibilities)
    selection_service.find_conflicting_constraints()

    captured = capsys.readouterr()

    assert "Unsatisfiable! Here's the reason:" in captured.out


def test_select_part_option(selection_service, db_session):
    parts = db_session.query(Part).all()
    options = db_session.query(Option).all()
    compatibilities = db_session.query(OptionCompatibility).all()

    selection_service.load_compatibilities(parts, options, compatibilities)

    full_suspension = db_session.query(Option).filter_by(name="Full-suspension").first()
    selection_service.select_part_option(full_suspension)

    assert selection_service.solver.check() == sat
