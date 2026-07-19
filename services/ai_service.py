from database.engine import get_db
from repositories.product_repository import ProductRepository
from schemas.product import ProductFilterInput
from adapters.groq_adapter import recommend_flavors, generate_gift_message
from typing import Optional, List


class AIService:
    def get_flavor_recommendations(
        self,
        occasion: str,
        preferences: Optional[List[str]] = None,
        restrictions: Optional[List[str]] = None,
        only_available: bool = True,
    ) -> str:
        with get_db() as db:
            repo = ProductRepository(db)
            products = repo.list_products(ProductFilterInput())
            if only_available:
                products = [p for p in products if p.available_quantity > 0]
            available = [{"name": p.flavor.name if p.flavor else p.name} for p in products]
        return recommend_flavors(
            occasion=occasion,
            preferences=preferences or [],
            restrictions=restrictions or [],
            available_flavors=available,
        )

    def get_gift_message(self, sender: str, recipient: str,
                         occasion: str, tone: str = "afetuoso") -> str:
        return generate_gift_message(sender=sender, recipient=recipient,
                                     occasion=occasion, tone=tone)
