from sqlalchemy.orm import Session
from database.models import GiftBox, GiftBoxItem, PersonalizedCard, Product
from schemas.gift import CreateGiftBoxInput
from typing import Optional, Tuple
from decimal import Decimal

PACKAGING_PRICES = {
    "standard": Decimal("5.00"),
    "premium": Decimal("12.00"),
    "luxury": Decimal("25.00"),
}


class GiftService:
    def __init__(self, db: Session):
        self.db = db

    def create_gift_box(self, data: CreateGiftBoxInput) -> Tuple[Optional[GiftBox], Optional[str]]:
        packaging_price = PACKAGING_PRICES.get(data.packaging_type, Decimal("5.00"))
        gift_box = GiftBox(
            name=data.name,
            description=data.description,
            occasion=data.occasion,
            packaging_type=data.packaging_type,
            packaging_price=packaging_price,
            is_active=True,
        )
        self.db.add(gift_box)
        self.db.flush()
        for item_input in data.items:
            product = self.db.query(Product).filter_by(id=item_input.product_id, is_active=True).first()
            if not product:
                return None, f"Produto {item_input.product_id} nao encontrado."
            self.db.add(GiftBoxItem(
                gift_box_id=gift_box.id,
                product_id=product.id,
                quantity=item_input.quantity,
                unit_price_snapshot=product.price,
            ))
        if data.card:
            self.db.add(PersonalizedCard(
                gift_box_id=gift_box.id,
                sender_name=data.card.sender_name,
                recipient_name=data.card.recipient_name,
                message=data.card.message,
                occasion=data.card.occasion,
            ))
        return gift_box, None

    def calculate_price(self, gift_box_id: int) -> Tuple[Optional[Decimal], Optional[str]]:
        gift_box = self.db.query(GiftBox).filter_by(id=gift_box_id).first()
        if not gift_box:
            return None, "Caixa de presente nao encontrada."
        items_total = sum(i.unit_price_snapshot * i.quantity for i in gift_box.items)
        return gift_box.packaging_price + items_total, None
