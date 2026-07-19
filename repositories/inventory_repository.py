from sqlalchemy.orm import Session
from database.models import InventoryItem
from typing import Optional, List
from decimal import Decimal


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> List[InventoryItem]:
        return self.db.query(InventoryItem).order_by(InventoryItem.name).all()

    def get_by_id(self, item_id: int) -> Optional[InventoryItem]:
        return self.db.query(InventoryItem).filter_by(id=item_id).first()

    def get_low_stock(self) -> List[InventoryItem]:
        """Retorna itens abaixo do estoque mínimo."""
        return (
            self.db.query(InventoryItem)
            .filter(InventoryItem.quantity <= InventoryItem.min_quantity)
            .all()
        )

    def adjust_quantity(self, item_id: int, delta: Decimal) -> tuple[bool, Optional[str]]:
        item = self.db.query(InventoryItem).filter_by(id=item_id).with_for_update().first()
        if not item:
            return False, "Item não encontrado."
        new_qty = item.quantity + delta
        if new_qty < 0:
            return False, f"Saldo insuficiente para '{item.name}'."
        item.quantity = new_qty
        return True, None
