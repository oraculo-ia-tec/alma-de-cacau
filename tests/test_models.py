"""Testes basicos dos modelos ORM."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.engine import Base
from database.models import User, UserRole, CustomerProfile, Product, Order, OrderStatus
from decimal import Decimal
from datetime import datetime


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_user(db):
    user = User(email="test@alma.com", hashed_password="hashed", full_name="Test User")
    db.add(user)
    db.commit()
    assert user.id is not None
    assert user.role == UserRole.customer
    assert user.is_active is True


def test_create_customer_profile(db):
    user = User(email="client@alma.com", hashed_password="hashed", full_name="Cliente")
    db.add(user)
    db.flush()
    profile = CustomerProfile(user_id=user.id, marketing_consent=True)
    db.add(profile)
    db.commit()
    assert profile.id is not None
    assert profile.marketing_consent is True


def test_order_status_enum(db):
    assert OrderStatus.pending.value == "pending"
    assert OrderStatus.delivered.value == "delivered"
    assert len(OrderStatus) == 7
