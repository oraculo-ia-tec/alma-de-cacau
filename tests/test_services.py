"""Testes dos servicos de negocio."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.engine import Base
from database.models import User, CustomerProfile, Product, Flavor
from services.customer_service import CustomerService, _hash_password
from services.product_service import ProductService
from schemas.customer import CreateCustomerInput
from schemas.product import CreateProductInput
from decimal import Decimal


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_customer_register(db):
    svc = CustomerService(db)
    data = CreateCustomerInput(
        full_name="Maria Silva", email="maria@test.com",
        password="senha1234", marketing_consent=True,
    )
    profile, err = svc.register(data)
    assert err is None
    assert profile is not None
    assert profile.marketing_consent is True


def test_customer_duplicate_email(db):
    svc = CustomerService(db)
    data = CreateCustomerInput(full_name="A", email="dup@test.com", password="senha1234")
    svc.register(data)
    db.commit()
    _, err = svc.register(data)
    assert err is not None
    assert "cadastrado" in err.lower()


def test_customer_authenticate(db):
    svc = CustomerService(db)
    data = CreateCustomerInput(full_name="Test", email="auth@test.com", password="mypassword")
    svc.register(data)
    db.commit()
    user, err = svc.authenticate("auth@test.com", "mypassword")
    assert err is None
    assert user is not None
    _, err2 = svc.authenticate("auth@test.com", "wrong")
    assert err2 is not None


def test_create_product(db):
    svc = ProductService(db)
    data = CreateProductInput(
        sku="TEST-001", name="Teste Bombom",
        description="Descricao teste", price=Decimal("9.90"),
    )
    product, err = svc.create_product(data)
    assert err is None
    assert product.id is not None


def test_duplicate_sku(db):
    svc = ProductService(db)
    data = CreateProductInput(
        sku="DUP-001", name="Produto 1",
        description="Desc", price=Decimal("9.90"),
    )
    svc.create_product(data)
    db.commit()
    _, err = svc.create_product(data)
    assert err is not None
