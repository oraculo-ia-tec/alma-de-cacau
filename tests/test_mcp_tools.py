"""Testes basicos das ferramentas MCP."""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.engine import Base
from database.models import Product, Flavor
from decimal import Decimal


@pytest.fixture(autouse=True)
def mock_get_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    with patch("database.engine.engine", engine):
        yield Session()
    Base.metadata.drop_all(bind=engine)


def test_list_products_empty(mock_get_db):
    """list_products retorna lista vazia se nao ha produtos."""
    db = mock_get_db
    from repositories.product_repository import ProductRepository
    from schemas.product import ProductFilterInput
    repo = ProductRepository(db)
    result = repo.list_products(ProductFilterInput())
    assert result == []


def test_get_product_not_found(mock_get_db):
    db = mock_get_db
    from repositories.product_repository import ProductRepository
    repo = ProductRepository(db)
    result = repo.get_by_id(999)
    assert result is None
