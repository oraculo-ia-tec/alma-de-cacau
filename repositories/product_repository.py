from sqlalchemy.orm import Session, selectinload
from database.models import Product, Flavor, ProductAllergen, Allergen
from schemas.product import ProductFilterInput
from typing import List, Optional


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_products(self, filters: ProductFilterInput) -> List[Product]:
        q = (
            self.db.query(Product)
            .options(
                selectinload(Product.flavor),
                selectinload(Product.allergens).selectinload(ProductAllergen.allergen),
            )
            .filter(Product.is_active == True)
        )
        if filters.only_featured:
            q = q.filter(Product.is_featured == True)
        if filters.only_seasonal:
            q = q.filter(Product.is_seasonal == True)
        if filters.only_best_sellers:
            q = q.filter(Product.is_best_seller == True)
        if filters.max_price is not None:
            q = q.filter(Product.price <= filters.max_price)
        if filters.min_price is not None:
            q = q.filter(Product.price >= filters.min_price)
        if filters.flavor_name:
            q = q.join(Product.flavor).filter(Flavor.name.ilike(f"%{filters.flavor_name}%"))
        offset = (filters.page - 1) * filters.page_size
        return q.offset(offset).limit(filters.page_size).all()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return (
            self.db.query(Product)
            .options(
                selectinload(Product.flavor),
                selectinload(Product.allergens).selectinload(ProductAllergen.allergen),
                selectinload(Product.ingredients),
            )
            .filter(Product.id == product_id, Product.is_active == True)
            .first()
        )

    def get_by_sku(self, sku: str) -> Optional[Product]:
        return self.db.query(Product).filter_by(sku=sku, is_active=True).first()

    def decrement_stock(self, product_id: int, quantity: int) -> bool:
        product = self.db.query(Product).filter_by(id=product_id).with_for_update().first()
        if not product or product.available_quantity < quantity:
            return False
        product.available_quantity -= quantity
        return True

