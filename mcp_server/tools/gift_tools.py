from mcp.server.fastmcp import FastMCP
from database.engine import get_db
from services.gift_service import GiftService
from schemas.gift import CreateGiftBoxInput, GiftBoxItemInput, PersonalizedCardInput
from database.models import OccasionType
from typing import Optional, List


def register(mcp: FastMCP):

    @mcp.tool(
        name="create_gift_box",
        description="Monta uma caixa de presente personalizada com produtos, embalagem e cartao.",
    )
    def create_gift_box(
        name: str,
        items: List[dict],
        occasion: Optional[str] = None,
        packaging_type: str = "standard",
        sender_name: Optional[str] = None,
        recipient_name: Optional[str] = None,
        card_message: Optional[str] = None,
    ) -> dict:
        parsed_items = [GiftBoxItemInput(**it) for it in items]
        card = None
        if sender_name and recipient_name and card_message:
            occ = OccasionType(occasion) if occasion else None
            card = PersonalizedCardInput(
                sender_name=sender_name, recipient_name=recipient_name,
                message=card_message, occasion=occ,
            )
        occ_enum = OccasionType(occasion) if occasion else None
        data = CreateGiftBoxInput(
            name=name, items=parsed_items, occasion=occ_enum,
            packaging_type=packaging_type, card=card,
        )
        with get_db() as db:
            svc = GiftService(db)
            gift_box, err = svc.create_gift_box(data)
            if err:
                return {"error": err}
            price, _ = svc.calculate_price(gift_box.id)
            return {
                "success": True,
                "gift_box_id": gift_box.id,
                "name": gift_box.name,
                "packaging_type": gift_box.packaging_type,
                "total_price": float(price) if price else None,
                "has_card": card is not None,
            }

    @mcp.tool(name="get_gift_box_price", description="Calcula o preco total de uma caixa de presente.")
    def get_gift_box_price(gift_box_id: int) -> dict:
        with get_db() as db:
            svc = GiftService(db)
            price, err = svc.calculate_price(gift_box_id)
            if err:
                return {"error": err}
            return {"gift_box_id": gift_box_id, "total_price": float(price)}
