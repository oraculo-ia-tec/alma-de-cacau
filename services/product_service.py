from sqlalchemy.orm import Session
from database.models import Product
from schemas.product import CreateProductInput, ProductFilterInput
from repositories.product_repository import ProductRepository
from typing import Optional, Tuple, List


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    def list_products(self, filters: Optional[ProductFilterInput] = None) -> List[Product]:
        return self.repo.list_products(filters or ProductFilterInput())

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.repo.get_by_id(product_id)

    def create_product(self, data: CreateProductInput) -> Tuple[Optional[Product], Optional[str]]:
        if self.repo.get_by_sku(data.sku):
            return None, f"SKU '{data.sku}' ja cadastrado."
        product = Product(**data.model_dump())
        self.db.add(product)
        return product, None

    def update_stock(self, product_id: int, delta: int) -> Tuple[bool, Optional[str]]:
        product = self.db.query(Product).filter_by(id=product_id).with_for_update().first()
        if not product:
            return False, "Produto nao encontrado."
        new_qty = product.available_quantity + delta
        if new_qty < 0:
            return False, f"Estoque insuficiente: disponivel {product.available_quantity}."
        product.available_quantity = new_qty
        return True, None

    def toggle_active(self, product_id: int) -> Tuple[Optional[bool], Optional[str]]:
        product = self.db.query(Product).filter_by(id=product_id).first()
        if not product:
            return None, "Produto nao encontrado."
        product.is_active = not product.is_active
        return product.is_active, None
